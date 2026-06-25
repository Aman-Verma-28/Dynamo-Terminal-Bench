"""Reference solution for the log-report task.

Parses /app/access.log (mixed Apache combined/common log format) and writes a
six-field summary to /app/report.json. Standard library only.
"""
import json
import re
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_EVEN
from urllib.parse import unquote

LOG_PATH = "/app/access.log"
OUT_PATH = "/app/report.json"

# IP - - [timestamp] "request" status size "referer" "user-agent"
# The referer/user-agent pair is optional (common log format omits it).
LINE_RE = re.compile(
    r'^(\S+) \S+ \S+ \[([^\]]+)\] "([^"]*)" (\d{3}) (\S+)'
    r'(?: "([^"]*)" "([^"]*)")?\s*$'
)
BOT_RE = re.compile(r"(bot|crawler|spider)", re.IGNORECASE)


def parse_lines(text):
    """Yield one record per well-formed request line; skip everything else."""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = LINE_RE.match(line)
        if not m:
            continue
        ip, ts, request, status, size, _referer, ua = m.groups()
        parts = request.split()
        if len(parts) != 3:                     # "-", truncated, missing fields
            continue
        if not re.fullmatch(r"\d+|-", size):     # size must be an int or "-"
            continue
        try:
            dt = datetime.strptime(ts, "%d/%b/%Y:%H:%M:%S %z")
        except ValueError:
            continue
        _method, path, _proto = parts
        yield {
            "ip": ip,
            "dt": dt,
            "path": path,
            "status": int(status),
            "bytes": 0 if size == "-" else int(size),
            "ua": ua or "",
        }


def normalize_path(path):
    """Strip query, percent-decode, collapse // , drop trailing slash (not root)."""
    p = path.split("?", 1)[0]
    p = unquote(p)
    p = re.sub(r"/+", "/", p)
    if len(p) > 1 and p.endswith("/"):
        p = p[:-1]
    return p


def build_report(records):
    valid = len(records)

    visitors = {
        r["ip"] for r in records if not BOT_RE.search(r["ua"])
    }

    total_bytes = sum(r["bytes"] for r in records)

    path_counts = Counter(
        normalize_path(r["path"]) for r in records if 200 <= r["status"] < 400
    )
    # most frequent path; tie-break = lexicographically smallest
    top_path = sorted(path_counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    hour_counts = Counter(
        r["dt"].astimezone(timezone.utc).hour for r in records
    )
    # busiest hour; tie-break = earliest hour
    busiest = sorted(hour_counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    errors = sum(1 for r in records if r["status"] >= 400)
    error_rate = float(
        (Decimal(errors) / Decimal(valid)).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_EVEN
        )
    )

    return {
        "valid_requests": valid,
        "unique_visitors": len(visitors),
        "top_path": top_path,
        "total_bytes": total_bytes,
        "busiest_hour": f"{busiest:02d}:00",
        "error_rate": error_rate,
    }


def main():
    with open(LOG_PATH) as f:
        records = list(parse_lines(f.read()))
    report = build_report(records)
    with open(OUT_PATH, "w") as out:
        json.dump(report, out)
    print(f"wrote {OUT_PATH}: {report}")


if __name__ == "__main__":
    main()
