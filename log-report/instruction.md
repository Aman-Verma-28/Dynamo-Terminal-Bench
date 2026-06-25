An Apache-style access log is at `/app/access.log`. Most lines are the combined log format:

```
IP - - [DD/Mon/YYYY:HH:MM:SS +ZZZZ] "METHOD PATH PROTOCOL" STATUS BYTES "REFERER" "USER-AGENT"
```

Some lines use the common log format (no `"REFERER" "USER-AGENT"` at the end). The file also
contains blank lines, comment lines starting with `#`, and malformed lines.

Parse the log and write a summary as a single JSON object to `/app/report.json` (absolute path),
with exactly these keys:

- `valid_requests` (integer)
- `unique_visitors` (integer)
- `top_path` (string)
- `total_bytes` (integer)
- `busiest_hour` (string)
- `error_rate` (number)

Definitions — read carefully; the rules interact:

A line is a **valid request** only if it matches one of the two formats above AND its quoted request
field is exactly three whitespace-separated tokens (`METHOD PATH PROTOCOL`) AND its BYTES field is
either digits or `-`. Blank lines, `#` comment lines, and any line failing these checks are skipped
(not counted anywhere). All keys below are computed over valid requests only.

A request is a **bot** if its user-agent contains `bot`, `crawler`, or `spider` (case-insensitive).
Common-format lines (no user-agent) are never bots.

**Path normalization** (used for `top_path`), applied in this order:
1. drop the query string (everything from the first `?`),
2. percent-decode (e.g. `%7E` → `~`, `%61` → `a`),
3. collapse any run of `/` into a single `/`,
4. remove a trailing `/` unless the path is exactly `/`.

Examples: `/a//b/?x=1` → `/a/b`; `/%61bout` → `/about`; `//about` → `/about`; `/` → `/`.

Success criteria:

1. `/app/report.json` exists and is a single valid JSON object.
2. `valid_requests` = the number of valid request lines.
3. `unique_visitors` = the number of distinct client IPs among valid requests, **excluding bot
   requests** (a bot's IP is counted only if it also appears on a non-bot valid request).
4. `top_path` = the most frequently requested **normalized** path among valid requests whose status
   is 2xx or 3xx (100–199, 4xx, 5xx are excluded from this count). If several paths tie, choose the
   lexicographically smallest.
5. `total_bytes` = the sum of the BYTES field over valid requests, where `-` counts as 0.
6. `busiest_hour` = the clock hour with the most valid requests **after converting each timestamp to
   UTC** using its `+ZZZZ` offset, formatted `"HH:00"` (zero-padded, e.g. `"08:00"`). If several
   hours tie, choose the earliest.
7. `error_rate` = (valid requests with status ≥ 400) ÷ (valid_requests), rounded to 4 decimal places
   using round-half-to-even (banker's rounding).

You have 600 seconds to complete this task.
