from src.v6.api.calibration_summary import (
    get_calibration_summary,
)


def test_calibration_summary_for_existing_instrument():
    summary = get_calibration_summary(1)

    assert summary["instrument_id"] == 1
    assert summary["total_calibrations"] >= 0
    assert summary["pass_count"] >= 0
    assert summary["fail_count"] >= 0
    assert summary["pass_count"] + summary["fail_count"] == (
        summary["total_calibrations"]
    )
    assert 0 <= summary["pass_rate"] <= 100
    assert summary["average_absolute_error"] >= 0


def test_calibration_summary_invalid_instrument_id():
    try:
        get_calibration_summary(0)
        assert False, "Invalid instrument ID should be rejected."
    except ValueError as exc:
        assert "greater than 0" in str(exc)