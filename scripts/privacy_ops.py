#!/usr/bin/env python3
"""Private monthly aggregate export; network is disabled unless --execute is given.

Deletion remains offline-only. Uses only the Python standard library.
"""
import argparse
import calendar
import datetime as dt
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

PROPERTY = "555488369"
STREAMS = ["15827868073", "15827890246"]
MIN_COUNT = 20
BUCKET_SIZE = 20
MAX_RESPONSE_BYTES = 1_000_000
REPORT_URL = f"https://analyticsdata.googleapis.com/v1beta/properties/{PROPERTY}:runReport"
READ_SCOPE = "https://www.googleapis.com/auth/analytics.readonly"


def fail(message):
    raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail("Duplicate JSON key")
        result[key] = value
    return result


def load_json(path):
    # No content or identifier is printed in error paths.
    if Path(path).stat().st_size > MAX_RESPONSE_BYTES:
        fail("Input exceeds local size limit")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle, object_pairs_hook=unique_object)


def month_request(month, timezone, today=None):
    if not re.fullmatch(r"20\d{2}-(0[1-9]|1[0-2])", month):
        fail("Month must be YYYY-MM")
    tz = ZoneInfo(timezone)
    today = today or dt.datetime.now(tz).date()
    year, number = map(int, month.split("-"))
    start = dt.date(year, number, 1)
    end = dt.date(year, number, calendar.monthrange(year, number)[1])
    if today < end + dt.timedelta(days=8):
        fail("Wait seven full days after month end; this is a workflow buffer, not a Google finality guarantee")
    return {
        "dateRanges": [{"startDate": start.isoformat(), "endDate": end.isoformat()}],
        "metrics": [{"name": "activeUsers"}],
        "dimensionFilter": {"filter": {
            "fieldName": "streamId",
            "inListFilter": {"values": STREAMS, "caseSensitive": True},
        }},
        "keepEmptyRows": False,
        "limit": "1",
        "returnPropertyQuota": True,
    }


def deletion_plan(payload):
    if not isinstance(payload, dict) or set(payload) != {"appInstanceId"}:
        fail("Exactly appInstanceId is required; no email, User ID, installation ID or extra fields")
    identifier = payload["appInstanceId"]
    # Deliberate broad transport check, NOT proof that a Google identifier exists.
    if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,256}", identifier):
        fail("Identifier transport shape rejected; value is not echoed")
    return {
        "mode": "OFFLINE_DRY_RUN_ONLY", "submitted": False,
        "method": "POST",
        "url": f"https://analyticsadmin.googleapis.com/v1alpha/properties/{PROPERTY}:submitUserDeletion",
        "oauth_scope": "https://www.googleapis.com/auth/analytics.edit",
        "body": {"appInstanceId": "<redacted; use original private input during separately authorized operator submission>"},
        "identifier_existence_or_ownership_verified": False,
    }


def sanitise(response, request, month, timezone, today=None):
    if json.dumps(request, sort_keys=True) != json.dumps(month_request(month, timezone, today), sort_keys=True):
        fail("Request differs from the fixed two-stream, one-month, no-dimension design")
    allowed_top = {"dimensionHeaders", "metricHeaders", "rows", "rowCount", "metadata", "propertyQuota", "kind"}
    if not isinstance(response, dict) or set(response) - allowed_top:
        fail("Unknown response shape")
    if response.get("kind", "analyticsData#runReport") != "analyticsData#runReport":
        fail("Unexpected report kind")
    if response.get("dimensionHeaders", []) != []:
        fail("Dimension breakdowns are prohibited")
    if response.get("metricHeaders") != [{"name": "activeUsers", "type": "TYPE_INTEGER"}]:
        fail("Only the activeUsers integer metric is allowed")
    meta = response.get("metadata")
    allowed_meta = {"dataLossFromOtherRow", "samplingMetadatas", "dataTruncationReasons",
                    "schemaRestrictionResponse", "currencyCode", "timeZone", "emptyReason", "subjectToThresholding"}
    if not isinstance(meta, dict) or set(meta) - allowed_meta or meta.get("timeZone") != timezone:
        fail("Unknown metadata or unverified property timezone")
    for flag in ("dataLossFromOtherRow", "subjectToThresholding"):
        if flag in meta and meta[flag] is not False:
            fail("Thresholded or lossy report needs operator review")
    for field in ("samplingMetadatas", "dataTruncationReasons", "emptyReason"):
        if meta.get(field):
            fail("Sampled, truncated or explicitly empty report needs operator review")
    restrictions = meta.get("schemaRestrictionResponse", {})
    if not isinstance(restrictions, dict) or set(restrictions) - {"activeMetricRestrictions"} or restrictions.get("activeMetricRestrictions"):
        fail("Restricted report needs operator review")
    rows = response.get("rows", [])
    row_count = response.get("rowCount", 0)
    if type(row_count) is not int or not isinstance(rows, list) or row_count != len(rows) or len(rows) > 1:
        fail("Expected at most one complete aggregate row")
    count = None
    if rows:
        row = rows[0]
        if not isinstance(row, dict) or set(row) - {"dimensionValues", "metricValues"} or row.get("dimensionValues", []) != []:
            fail("Unexpected row or prohibited dimension values")
        values = row.get("metricValues")
        if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], dict) or set(values[0]) != {"value"}:
            fail("Expected one metric value")
        value = values[0]["value"]
        if not isinstance(value, str) or not re.fullmatch(r"0|[1-9][0-9]{0,14}", value):
            fail("Metric must be a nonnegative integer string")
        count = int(value)
    # No exact count, identifiers, source hash, quota details, device or city fields survive.
    result = {
        "schema": "doseweek-monthly-aggregate-candidate-v1",
        "month": month,
        "metric": "GA activeUsers; not a count of distinct people",
        "status": "suppressed_or_no_data",
        "active_user_count_range": None,
        "privacy_review": "PENDING; threshold and bucketing do not establish anonymity",
        "long_term_storage_approved": False,
    }
    if count is not None and count >= MIN_COUNT:
        low = (count // BUCKET_SIZE) * BUCKET_SIZE
        result["status"] = "candidate_for_contextual_review"
        result["active_user_count_range"] = [low, low + BUCKET_SIZE - 1]
    return result


def write_new_private(path, payload):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def outside_repository(path):
    resolved = Path(path).expanduser().resolve()
    if any((parent / ".git").exists() for parent in (resolved, *resolved.parents)):
        fail("Credentials and aggregate archives must be outside Git repositories")
    return resolved


def read_access_token(path):
    """Read an existing short-lived token, never refresh, log or persist it."""
    path = Path(path).expanduser()
    outside_repository(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) & 0o077 or info.st_size > 8192):
            fail("Token must be a small owner-only regular file outside Git")
        value = os.read(fd, 8193).decode("ascii").strip()
    finally:
        os.close(fd)
    if not re.fullmatch(r"[A-Za-z0-9._~+/=-]{1,8192}", value):
        fail("Token file shape rejected; value is not echoed")
    return value


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_report(request, token):
    """One fixed HTTPS request, no proxies, redirects, retries or raw disk writes."""
    req = urllib.request.Request(REPORT_URL,
        data=json.dumps(request).encode("utf-8"), method="POST",
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json",
                 "Accept": "application/json"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(req, timeout=30) as reply:
            if reply.status != 200 or reply.geturl() != REPORT_URL:
                fail("Unexpected report endpoint or status; nothing stored")
            if reply.headers.get_content_type() != "application/json":
                fail("Unexpected report content type; nothing stored")
            raw = reply.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        # Never print provider error bodies, URLs, request headers or token data.
        code = exc.code
        exc.close()
        fail(f"Report HTTP {code}; no retry or upgrade attempted; nothing stored")
    except (urllib.error.URLError, TimeoutError, OSError):
        fail("Report transport failed; no retry attempted; nothing stored")
    if len(raw) > MAX_RESPONSE_BYTES:
        fail("Report exceeds local size limit; nothing stored")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)


def private_archive(path):
    source = Path(path).expanduser()
    if source.is_symlink():
        fail("Archive must not be a symbolic link")
    archive = outside_repository(source)
    archive.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = archive.stat()
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) & 0o077):
        fail("Archive must be an owner-only directory outside Git")
    return archive


def write_atomic_private(path, payload):
    """Only minimised output reaches disk. Publish without replacing any file."""
    fd, temporary = tempfile.mkstemp(prefix="." + path.stem + "-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)  # Atomic no-replace publication on a local filesystem.
        os.unlink(temporary)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def export_month(month, timezone, archive_dir, token_file=None, execute=False, today=None):
    request = month_request(month, timezone, today)
    if not execute:
        # Dry run does not read credentials, create directories or contact Google.
        return {"mode": "DRY_RUN", "remote_calls": 0, "written": False,
                "method": "POST", "url": REPORT_URL, "oauth_scope": READ_SCOPE,
                "body": request, "output_file": month + ".json",
                "privacy_review": "PENDING; not certified anonymous"}
    if not token_file:
        fail("Execution requires a separately prepared private access-token file")
    archive = private_archive(archive_dir)
    if Path(token_file).expanduser().resolve().is_relative_to(archive):
        fail("Keep the access-token file outside the aggregate archive")
    output = archive / (month + ".json")
    if os.path.lexists(output):
        fail("Month already exists; no overwrite or repeat query allowed")
    lock = archive / ("." + month + ".lock")
    lock_fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(lock_fd)
    try:
        if os.path.lexists(output):
            fail("Month already exists; no overwrite or repeat query allowed")
        token = read_access_token(token_file)
        response = fetch_report(request, token)
        result = sanitise(response, request, month, timezone, today)
        del token, response
        write_atomic_private(output, result)
        return {"written": True, "remote_calls": 1, "output_file": output.name,
                "privacy_review": "PENDING; not certified anonymous"}
    finally:
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    delete = sub.add_parser("deletion-dry-run")
    delete.add_argument("--identifier-file", required=True)
    plan = sub.add_parser("monthly-request")
    sanitise_parser = sub.add_parser("sanitise-month")
    export = sub.add_parser("export-month", help="Dry run by default; one readonly request only with --execute")
    for item in (plan, sanitise_parser, export):
        item.add_argument("--month", required=True)
        item.add_argument("--timezone", required=True, help="Read back the actual GA property timezone; do not assume it")
    sanitise_parser.add_argument("--request-file", required=True)
    sanitise_parser.add_argument("--response-file", required=True)
    sanitise_parser.add_argument("--output", required=True, help="New private candidate file; overwrite refused")
    export.add_argument("--archive-dir", required=True, help="One fixed owner-only archive outside all Git repositories")
    export.add_argument("--access-token-file", help="Existing short-lived OAuth token, owner-only file outside Git; never printed")
    export.add_argument("--execute", action="store_true", help="Explicitly enable one readonly Google API request")
    args = parser.parse_args()
    try:
        if args.command == "deletion-dry-run":
            result = deletion_plan(load_json(args.identifier_file))
        elif args.command == "monthly-request":
            result = {"mode": "OFFLINE_PLAN_ONLY", "method": "POST",
                      "url": REPORT_URL,
                      "oauth_scope": READ_SCOPE,
                      "body": month_request(args.month, args.timezone)}
        elif args.command == "export-month":
            result = export_month(args.month, args.timezone, args.archive_dir,
                                  args.access_token_file, args.execute)
        else:
            result = sanitise(load_json(args.response_file), load_json(args.request_file), args.month, args.timezone)
            write_new_private(args.output, result)
            result = {"written": True, "remote_calls": 0, "privacy_review": "PENDING"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError, UnicodeError) as exc:
        # JSONDecodeError text can include snippets; avoid printing arbitrary input data.
        print("Rejected: " + (str(exc) if type(exc) is ValueError else type(exc).__name__), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
