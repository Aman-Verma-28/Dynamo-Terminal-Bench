import json
from pathlib import Path

REPORT = Path("/app/report.json")

# Ground-truth summary for the bundled /app/access.log (32 well-formed request
# lines after skipping comments, blanks, and malformed lines). Values are
# produced by the reference solver, not hand-guessed.
EXPECTED = {
    "valid_requests": 32,
    "unique_visitors": 6,     # distinct non-bot client IPs
    "top_path": "/about",     # most-frequent normalized 2xx/3xx path
    "total_bytes": 14307,     # sum of response sizes ("-" counts as 0)
    "busiest_hour": "08:00",  # busiest hour in UTC, earliest-hour tie-break
    "error_rate": 0.2812,     # 9/32 status>=400, 4dp round-half-to-even
}


def _load():
    return json.loads(REPORT.read_text())


def test_report_is_valid_json():
    """Criterion 1: /app/report.json exists and is a valid JSON object."""
    assert REPORT.exists(), "no report.json found at /app/report.json"
    report = _load()
    assert isinstance(report, dict), (
        f"report must be a JSON object, got {type(report).__name__}"
    )


def test_valid_requests():
    """Criterion 2: valid_requests counts only well-formed request lines."""
    report = _load()
    assert report.get("valid_requests") == EXPECTED["valid_requests"], (
        f"valid_requests should be {EXPECTED['valid_requests']}, "
        f"got {report.get('valid_requests')!r}"
    )


def test_unique_visitors():
    """Criterion 3: unique_visitors counts distinct non-bot client IPs."""
    report = _load()
    assert report.get("unique_visitors") == EXPECTED["unique_visitors"], (
        f"unique_visitors should be {EXPECTED['unique_visitors']}, "
        f"got {report.get('unique_visitors')!r}"
    )


def test_top_path():
    """Criterion 4: top_path is the most-frequent normalized 2xx/3xx path."""
    report = _load()
    assert report.get("top_path") == EXPECTED["top_path"], (
        f"top_path should be {EXPECTED['top_path']!r}, "
        f"got {report.get('top_path')!r}"
    )


def test_total_bytes():
    """Criterion 5: total_bytes sums response sizes ('-' counts as 0)."""
    report = _load()
    assert report.get("total_bytes") == EXPECTED["total_bytes"], (
        f"total_bytes should be {EXPECTED['total_bytes']}, "
        f"got {report.get('total_bytes')!r}"
    )


def test_busiest_hour():
    """Criterion 6: busiest_hour is the busiest UTC hour (earliest-hour tie-break)."""
    report = _load()
    assert report.get("busiest_hour") == EXPECTED["busiest_hour"], (
        f"busiest_hour should be {EXPECTED['busiest_hour']!r}, "
        f"got {report.get('busiest_hour')!r}"
    )


def test_error_rate():
    """Criterion 7: error_rate is the status>=400 fraction, 4dp round-half-to-even."""
    report = _load()
    value = report.get("error_rate")
    assert isinstance(value, (int, float)), (
        f"error_rate should be a number, got {type(value).__name__}"
    )
    assert abs(value - EXPECTED["error_rate"]) < 1e-9, (
        f"error_rate should be {EXPECTED['error_rate']}, got {value!r}"
    )
