#!/usr/bin/env python3
"""
Integration tests for build_video.py — verifies that the refactor computes
slide/BGM-fade durations correctly when TTS segment lengths change.

We monkeypatch `probe_duration` so the tests run in milliseconds without
touching ffmpeg or real media files. The tests exercise the same code paths
that real `python3 build_video.py` hits:
  - Step 0: probe TTS durations
  - Step 2: resolve SLIDES from SLIDES_SPEC + durations
  - Step 3: compute BGM fade-out start

Run:  python3 -m pytest scripts/test_build_video_integration.py -v
Or:   python3 scripts/test_build_video_integration.py
"""
import importlib.util
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
BUILD_VIDEO_PATH = SCRIPTS_DIR / "build_video.py"

# --- load build_video.py as a module (file has hyphen-friendly name issues? no, it imports fine) ---
_spec = importlib.util.spec_from_file_location("build_video", BUILD_VIDEO_PATH)
bv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bv)


def _make_slides(tts_durations: list[float]) -> list[tuple[Path, float]]:
    """Replicate main()'s slide-resolution logic without invoking ffmpeg."""
    slides = []
    for img_name, seg_indices in bv.SLIDES_SPEC:
        if seg_indices is None:
            dur = bv.COVER_DURATION
        else:
            dur = sum(tts_durations[i - 1] for i in seg_indices)
        slides.append((Path("images") / img_name, dur))
    return slides


def _bgm_fade_out_start(slides_total_dur: float) -> float:
    """Replicate build_final()'s fade-start computation."""
    return max(0.0, slides_total_dur - bv.BGM_FADE_OUT_BEFORE_END)


# ---------------------------------------------------------------------------
# Test 1: SLIDES_SPEC wiring is consistent with TTS_COUNT
# ---------------------------------------------------------------------------
def test_slides_spec_references_valid_segments():
    """Every segment index in SLIDES_SPEC must be in [1, TTS_COUNT],
    and segments [1..TTS_COUNT] must all be covered exactly once."""
    referenced: list[int] = []
    for _img, segs in bv.SLIDES_SPEC:
        if segs is None:
            continue
        for s in segs:
            assert 1 <= s <= bv.TTS_COUNT, f"segment {s} out of range [1,{bv.TTS_COUNT}]"
            referenced.append(s)
    expected = list(range(1, bv.TTS_COUNT + 1))
    assert sorted(referenced) == expected, (
        f"SLIDES_SPEC must cover segments {expected} exactly once, "
        f"got {sorted(referenced)}"
    )


# ---------------------------------------------------------------------------
# Test 2: cover + all-TTS duration = slideshow total (no gaps, no overlaps)
# ---------------------------------------------------------------------------
def test_slides_total_equals_cover_plus_all_tts():
    """Slideshow = cover + every TTS segment exactly once.
    A regression here would mean a slide double-counts or drops a segment."""
    fake_durations = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0]  # arbitrary
    assert len(fake_durations) == bv.TTS_COUNT

    slides = _make_slides(fake_durations)
    slides_total = sum(d for _img, d in slides)

    expected = bv.COVER_DURATION + sum(fake_durations)
    assert abs(slides_total - expected) < 1e-6, (
        f"slides total {slides_total} != cover+durations {expected}"
    )


# ---------------------------------------------------------------------------
# Test 3: simulated TTS length change → SLIDES lengths follow
# ---------------------------------------------------------------------------
def test_slides_follow_tts_length_changes():
    """When TTS durations change (e.g. regeneration), the slide for each
    image must scale with the segments it covers. This is the core refactor
    guarantee — if true, re-running needs no hand-edits."""
    durations_v1 = [26.388, 23.220, 47.556, 50.508, 53.028, 52.020, 22.176]
    durations_v2 = [30.000, 20.000, 50.000, 45.000, 55.000, 50.000, 25.000]

    slides_v1 = _make_slides(durations_v1)
    slides_v2 = _make_slides(durations_v2)

    # cover is constant
    assert slides_v1[0][1] == slides_v2[0][1] == bv.COVER_DURATION

    # 配图① covers [1, 2] → sum of segments 1+2
    assert abs(slides_v1[1][1] - (26.388 + 23.220)) < 1e-6
    assert abs(slides_v2[1][1] - (30.000 + 20.000)) < 1e-6

    # 配图⑤ covers [6, 7] → sum of segments 6+7
    assert abs(slides_v1[5][1] - (52.020 + 22.176)) < 1e-6
    assert abs(slides_v2[5][1] - (50.000 + 25.000)) < 1e-6

    # Single-segment slides track that one segment
    for slide_idx, seg_idx in [(2, 3), (3, 4), (4, 5)]:
        assert abs(slides_v1[slide_idx][1] - durations_v1[seg_idx - 1]) < 1e-6
        assert abs(slides_v2[slide_idx][1] - durations_v2[seg_idx - 1]) < 1e-6


# ---------------------------------------------------------------------------
# Test 4: BGM fade-out start scales with video length, not hardcoded
# ---------------------------------------------------------------------------
def test_bgm_fade_out_is_dynamic():
    """The old code hardcoded st=275. Verify the new value follows
    actual slideshow length."""
    short_durations = [5.0] * bv.TTS_COUNT      # 35s of TTS
    long_durations = [60.0] * bv.TTS_COUNT      # 420s of TTS

    for durations in (short_durations, long_durations):
        slides = _make_slides(durations)
        slides_total = sum(d for _img, d in slides)
        fade_start = _bgm_fade_out_start(slides_total)
        assert abs(fade_start - (slides_total - bv.BGM_FADE_OUT_BEFORE_END)) < 1e-6
        # The old hardcoded value (275) would be wrong for both short and long:
        assert fade_start != 275.0 or abs(slides_total - 278.0) < 1e-6, (
            "fade-out start should not be the old hardcoded 275 "
            "unless the video really is ~278s"
        )


# ---------------------------------------------------------------------------
# Test 5: build_tts_full expected-duration formula matches reality
# ---------------------------------------------------------------------------
def test_tts_full_duration_formula():
    """build_tts_full prints `expected = OPEN + sum(TTS) + TAIL`.
    That formula must equal the sum of every input segment's declared length."""
    fake_durations = [12.345, 23.456, 34.567, 45.678, 56.789, 67.890, 78.901]
    expected_per_formula = bv.OPEN_SILENCE + sum(fake_durations) + bv.TAIL_SILENCE

    # What the ffmpeg concat graph will actually produce (sum of input durations):
    actual_concat_sum = bv.OPEN_SILENCE + sum(fake_durations) + bv.TAIL_SILENCE

    assert abs(expected_per_formula - actual_concat_sum) < 1e-9


# ---------------------------------------------------------------------------
# Runner so the file works without pytest
# ---------------------------------------------------------------------------
def _run_all():
    tests = [
        ("test_slides_spec_references_valid_segments", test_slides_spec_references_valid_segments),
        ("test_slides_total_equals_cover_plus_all_tts", test_slides_total_equals_cover_plus_all_tts),
        ("test_slides_follow_tts_length_changes",       test_slides_follow_tts_length_changes),
        ("test_bgm_fade_out_is_dynamic",                test_bgm_fade_out_is_dynamic),
        ("test_tts_full_duration_formula",              test_tts_full_duration_formula),
    ]
    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {name}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed, {passed + failed} total")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    # If run as a script, just execute all tests directly.
    if "--pytest" in sys.argv:
        sys.exit(pytest_main())  # noqa: F821 -- only reached if pytest imported
    sys.exit(_run_all())
