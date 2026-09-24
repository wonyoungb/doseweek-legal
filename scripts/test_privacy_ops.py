import ast
from copy import deepcopy
import datetime as dt
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import urllib.error

import privacy_ops as ops


class PrivacyBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.today = dt.date(2026, 9, 23)
        self.month = "2026-08"
        self.tz = "Asia/Seoul"  # Synthetic fixture; real property timezone NOT verified.
        self.request = ops.month_request(self.month, self.tz, self.today)
        self.response = {
            "metricHeaders": [{"name": "activeUsers", "type": "TYPE_INTEGER"}],
            "rows": [{"metricValues": [{"value": "42"}]}],
            "rowCount": 1,
            "metadata": {"timeZone": self.tz},
        }

    def clean(self, response=None, request=None):
        return ops.sanitise(self.response if response is None else response,
                            self.request if request is None else request,
                            self.month, self.tz, self.today)

    def test_small_counts_and_zero_are_indistinguishable(self):
        results = []
        for number in (0, 1, 19):
            r = deepcopy(self.response)
            r["rows"][0]["metricValues"][0]["value"] = str(number)
            results.append(self.clean(r))
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[0], results[2])
        self.assertIsNone(results[0]["active_user_count_range"])

    def test_ranges_and_review_remain_pending(self):
        for number, expected in ((20, [20, 39]), (39, [20, 39]), (40, [40, 59]), (42, [40, 59])):
            r = deepcopy(self.response)
            r["rows"][0]["metricValues"][0]["value"] = str(number)
            result = self.clean(r)
            self.assertEqual(result["active_user_count_range"], expected)
            self.assertFalse(result["long_term_storage_approved"])
            self.assertIn("PENDING", result["privacy_review"])

    def test_empty_is_not_claimed_zero(self):
        r = deepcopy(self.response);r.pop("rows");r["rowCount"] = 0
        self.assertEqual(self.clean(r)["status"], "suppressed_or_no_data")

    def test_dimensions_rejected(self):
        for dimension in ("city", "deviceModel", "userId", "date", "streamId"):
            r = deepcopy(self.response);r["dimensionHeaders"] = [{"name": dimension}]
            with self.assertRaises(ValueError):self.clean(r)

    def test_hidden_row_dimension_rejected(self):
        r = deepcopy(self.response);r["rows"][0]["dimensionValues"] = [{"value": "private"}]
        with self.assertRaises(ValueError):self.clean(r)

    def test_extra_metric_and_field_rejected(self):
        for field in ("userId", "totals", "healthRecord"):
            r = deepcopy(self.response);r[field] = "private"
            with self.assertRaises(ValueError):self.clean(r)
        r = deepcopy(self.response);r["metricHeaders"].append({"name": "sessions", "type": "TYPE_INTEGER"})
        with self.assertRaises(ValueError):self.clean(r)

    def test_quality_flags_rejected(self):
        for name, value in (("subjectToThresholding", True), ("dataLossFromOtherRow", True),
                            ("samplingMetadatas", [{}]), ("dataTruncationReasons", [{}]),
                            ("emptyReason", "not available"), ("schemaRestrictionResponse", {"activeMetricRestrictions": [{}]})):
            r = deepcopy(self.response);r["metadata"][name] = value
            with self.assertRaises(ValueError):self.clean(r)

    def test_timezone_and_metadata_required(self):
        for meta in ({}, {"timeZone": "UTC"}, {"timeZone": self.tz, "unexpected": "private"}, None):
            r = deepcopy(self.response);r["metadata"] = meta
            with self.assertRaises(ValueError):self.clean(r)

    def test_truncated_or_invalid_row_count(self):
        for count in (2, "1", True, -1):
            r = deepcopy(self.response);r["rowCount"] = count
            with self.assertRaises(ValueError):self.clean(r)

    def test_malformed_counts(self):
        for value in ("-1", "1.5", "NaN", "1e3", "01", "secret", 42, True):
            r = deepcopy(self.response);r["rows"][0]["metricValues"][0]["value"] = value
            with self.assertRaises(ValueError):self.clean(r)

    def test_changed_query_rejected(self):
        for mutation in ({"dimensions": [{"name": "city"}]}, {"limit": "2"}, {"returnPropertyQuota": 1},
                         {"metrics": [{"name": "sessions"}]}, {"dateRanges": [{"startDate": "2026-08-02", "endDate": "2026-08-31"}]}):
            request = deepcopy(self.request);request.update(mutation)
            with self.assertRaises(ValueError):self.clean(request=request)

    def test_two_stream_filter_locked(self):
        request = deepcopy(self.request);request["dimensionFilter"]["filter"]["inListFilter"]["values"] = ["15827890246"]
        with self.assertRaises(ValueError):self.clean(request=request)

    def test_current_future_and_buffer_months_rejected(self):
        for month, today in (("2026-09", self.today), ("2026-10", self.today), ("2026-08", dt.date(2026, 9, 7))):
            with self.assertRaises(ValueError):ops.month_request(month, self.tz, today)
        ops.month_request("2026-08", self.tz, dt.date(2026, 9, 8))

    def test_leap_month_end(self):
        request = ops.month_request("2024-02", "UTC", self.today)
        self.assertEqual(request["dateRanges"][0]["endDate"], "2024-02-29")

    def test_deletion_plan_never_echoes_identifier(self):
        identifier = "SYNTHETIC_app_instance_001"
        result = ops.deletion_plan({"appInstanceId": identifier})
        self.assertFalse(result["submitted"])
        self.assertNotIn(identifier, json.dumps(result))
        self.assertIn("analytics.edit", result["oauth_scope"])
        self.assertNotIn("upsert", result["url"])

    def test_other_identifier_types_rejected(self):
        for payload in ({"userId": "synthetic"}, {"appInstanceId": "synthetic", "email": "example.invalid"},
                        {"appInstanceId": "with space"}, {"appInstanceId": ""}):
            with self.assertRaises(ValueError):ops.deletion_plan(payload)

    def test_private_write_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.json"
            ops.write_new_private(path, self.clean())
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            before = path.read_bytes()
            with self.assertRaises(FileExistsError):ops.write_new_private(path, {"other": True})
            self.assertEqual(path.read_bytes(), before)

    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.json";path.write_text('{"appInstanceId":"first","appInstanceId":"second"}')
            with self.assertRaises(ValueError):ops.load_json(path)

    def test_output_excludes_source_quota_and_exact_count(self):
        r = deepcopy(self.response);r["propertyQuota"] = {"synthetic_private": "do not retain"}
        result = self.clean(r)
        self.assertEqual(set(result), {"schema", "month", "metric", "status", "active_user_count_range", "privacy_review", "long_term_storage_approved"})
        self.assertNotIn("42", json.dumps(result))
        self.assertNotIn("do not retain", json.dumps(result))

    def test_runtime_has_only_bounded_standard_library_dependencies(self):
        tree = ast.parse(Path(ops.__file__).read_text())
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):imports.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):imports.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):self.assertNotIn(node.func.id, {"eval", "exec", "__import__"})
        self.assertLessEqual(imports, {"argparse", "calendar", "datetime", "json", "os", "pathlib", "re", "sys", "zoneinfo", "stat", "tempfile", "urllib"})


class MonthlyExportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.archive = self.root / "aggregate"
        self.token = self.root / "access-token"
        self.token.write_text("SYNTHETIC_TOKEN_DO_NOT_SEND\n")
        self.token.chmod(0o600)
        self.today = dt.date(2026, 9, 23)
        self.response = {"metricHeaders": [{"name": "activeUsers", "type": "TYPE_INTEGER"}],
                         "rows": [{"metricValues": [{"value": "42"}]}], "rowCount": 1,
                         "metadata": {"timeZone": "Asia/Seoul"},
                         "propertyQuota": {"synthetic_secret": "DO_NOT_STORE"}}

    def export(self, execute=True, **kwargs):
        return ops.export_month("2026-08", "Asia/Seoul", self.archive,
                                self.token, execute=execute, today=self.today, **kwargs)

    def test_default_dry_run_never_reads_token_contacts_network_or_writes(self):
        self.token.unlink()
        with patch.object(ops, "read_access_token", side_effect=AssertionError("no token read")), \
                patch.object(ops, "fetch_report", side_effect=AssertionError("no network")):
            result = self.export(execute=False)
        self.assertEqual(result["remote_calls"], 0)
        self.assertFalse(result["written"])
        self.assertFalse(self.archive.exists())
        self.assertEqual(result["output_file"], "2026-08.json")

    def test_execute_needs_explicit_token_without_automatic_auth(self):
        with patch.object(ops, "fetch_report") as fetch:
            with self.assertRaises(ValueError):
                ops.export_month("2026-08", "Asia/Seoul", self.archive, execute=True, today=self.today)
        fetch.assert_not_called()
        self.assertFalse(self.archive.exists())

    def test_one_request_persists_only_coarse_private_monthly_json(self):
        with patch.object(ops, "fetch_report", return_value=self.response) as fetch:
            result = self.export()
        fetch.assert_called_once_with(ops.month_request("2026-08", "Asia/Seoul", self.today),
                                      "SYNTHETIC_TOKEN_DO_NOT_SEND")
        output = self.archive / "2026-08.json"
        saved = json.loads(output.read_text())
        self.assertEqual(saved["active_user_count_range"], [40, 59])
        self.assertFalse(saved["long_term_storage_approved"])
        self.assertEqual(sorted(p.name for p in self.archive.iterdir()), ["2026-08.json"])
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(self.archive.stat().st_mode), 0o700)
        for private in ("42", "SYNTHETIC_TOKEN", "DO_NOT_STORE", "timeZone", "propertyQuota", "555488369"):
            self.assertNotIn(private, output.read_text())
        self.assertNotIn("range", json.dumps(result))

    def test_duplicate_month_stops_before_token_or_request_and_preserves_bytes(self):
        with patch.object(ops, "fetch_report", return_value=self.response): self.export()
        output = self.archive / "2026-08.json"
        before = output.read_bytes()
        with patch.object(ops, "read_access_token") as token, patch.object(ops, "fetch_report") as fetch:
            with self.assertRaises(ValueError): self.export()
        token.assert_not_called(); fetch.assert_not_called()
        self.assertEqual(output.read_bytes(), before)

    def test_existing_lock_prevents_concurrent_query_without_removing_other_lock(self):
        self.archive.mkdir(mode=0o700)
        lock = self.archive / ".2026-08.lock"; lock.write_text("")
        with patch.object(ops, "fetch_report") as fetch:
            with self.assertRaises(FileExistsError): self.export()
        fetch.assert_not_called(); self.assertTrue(lock.exists())

    def test_rejected_report_never_persists_raw_or_final_and_releases_lock(self):
        invalid = deepcopy(self.response); invalid["dimensionHeaders"] = [{"name": "city"}]
        with patch.object(ops, "fetch_report", return_value=invalid):
            with self.assertRaises(ValueError): self.export()
        self.assertEqual(list(self.archive.iterdir()), [])

    def test_transport_failure_does_not_retry_or_leave_output(self):
        with patch.object(ops, "fetch_report", side_effect=ValueError("Report transport failed")) as fetch:
            with self.assertRaises(ValueError): self.export()
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(list(self.archive.iterdir()), [])

    def test_small_counts_and_no_rows_have_identical_export_bytes(self):
        outputs=[]
        for i, number in enumerate((None, 0, 1, 19)):
            self.archive = self.root / str(i)
            response = deepcopy(self.response)
            if number is None: response.pop("rows"); response["rowCount"] = 0
            else: response["rows"][0]["metricValues"][0]["value"] = str(number)
            with patch.object(ops, "fetch_report", return_value=response): self.export()
            outputs.append((self.archive / "2026-08.json").read_bytes())
        self.assertEqual(len(set(outputs)), 1)

    def test_git_archive_and_token_rejected_before_network(self):
        (self.root / ".git").mkdir()
        with patch.object(ops, "fetch_report") as fetch:
            with self.assertRaises(ValueError): self.export()
        fetch.assert_not_called()
        with self.assertRaises(ValueError): ops.read_access_token(self.token)

    def test_shared_archive_and_symlink_rejected(self):
        self.archive.mkdir(mode=0o755)
        with self.assertRaises(ValueError): self.export()
        alias = self.root / "alias"; alias.symlink_to(self.archive, target_is_directory=True)
        with self.assertRaises(ValueError): ops.private_archive(alias)

    def test_token_in_archive_rejected(self):
        self.archive.mkdir(mode=0o700)
        self.token.rename(self.archive / "token")
        self.token = self.archive / "token"
        with patch.object(ops, "fetch_report") as fetch:
            with self.assertRaises(ValueError): self.export()
        fetch.assert_not_called()

    def test_insecure_symlink_directory_oversize_and_header_injection_token_rejected(self):
        self.token.chmod(0o644)
        with self.assertRaises(ValueError): ops.read_access_token(self.token)
        self.token.chmod(0o600)
        alias = self.root / "token-link"; alias.symlink_to(self.token)
        with self.assertRaises(OSError): ops.read_access_token(alias)
        with self.assertRaises(ValueError): ops.read_access_token(self.root)
        for content in ("a" * 8193, "token\nInjected: bad", "", "token\x00", "한글"):
            self.token.write_text(content)
            with self.assertRaises((ValueError, UnicodeError)): ops.read_access_token(self.token)

    def test_atomic_writer_refuses_existing_and_cleans_sanitised_temp(self):
        self.archive.mkdir(mode=0o700)
        final = self.archive / "2026-08.json"; final.write_text("EXISTING")
        with self.assertRaises(FileExistsError): ops.write_atomic_private(final, {"safe": True})
        self.assertEqual(final.read_text(), "EXISTING")
        self.assertEqual(list(self.archive.iterdir()), [final])

    def test_rejected_non_regular_token_closes_descriptor(self):
        with patch.object(ops.os, "close", wraps=os.close) as close:
            with self.assertRaises(ValueError): ops.read_access_token(self.root)
        close.assert_called_once()

    def test_publication_error_leaves_no_partial_final(self):
        with patch.object(ops, "fetch_report", return_value=self.response), \
                patch.object(ops.os, "link", side_effect=OSError("synthetic write failure")):
            with self.assertRaises(OSError): self.export()
        self.assertEqual(list(self.archive.iterdir()), [])

    def reply(self, raw=None):
        reply = MagicMock()
        reply.__enter__.return_value = reply
        reply.status = 200; reply.geturl.return_value = ops.REPORT_URL
        reply.headers.get_content_type.return_value = "application/json"
        reply.read.return_value = json.dumps(self.response).encode() if raw is None else raw
        return reply

    def test_transport_fixed_https_post_no_proxy_redirect_or_retry(self):
        reply = self.reply(); opener = MagicMock(); opener.open.return_value = reply
        request = ops.month_request("2026-08", "Asia/Seoul", self.today)
        with patch.object(ops.urllib.request, "build_opener", return_value=opener) as build:
            response = ops.fetch_report(request, "SYNTHETIC")
        self.assertEqual(response, self.response)
        self.assertEqual(build.call_args.args[0].proxies, {})
        self.assertIsInstance(build.call_args.args[1], ops.NoRedirect)
        sent = opener.open.call_args.args[0]
        self.assertEqual(sent.full_url, ops.REPORT_URL)
        self.assertEqual(sent.method, "POST")
        self.assertEqual(json.loads(sent.data), request)
        self.assertEqual(sent.get_header("Authorization"), "Bearer SYNTHETIC")
        self.assertEqual(opener.open.call_args.kwargs, {"timeout": 30})
        self.assertEqual(opener.open.call_count, 1)
        reply.read.assert_called_once_with(ops.MAX_RESPONSE_BYTES + 1)
        self.assertIsNone(ops.NoRedirect().redirect_request(None, None, 302, "", {}, "https://example.invalid"))

    def test_transport_rejects_nonjson_oversize_and_duplicate_payload(self):
        cases = [self.reply(b"{"), self.reply(b'{"rows":[],"rows":[]}'),
                 self.reply(b"x" * (ops.MAX_RESPONSE_BYTES + 1)), self.reply()]
        cases[-1].headers.get_content_type.return_value = "text/html"
        for reply in cases:
            opener = MagicMock(); opener.open.return_value = reply
            with patch.object(ops.urllib.request, "build_opener", return_value=opener):
                with self.assertRaises(ValueError): ops.fetch_report({}, "SYNTHETIC")

    def test_http_errors_redact_provider_body_and_do_not_retry(self):
        for code in (302, 401, 403, 429, 500, 503):
            opener = MagicMock()
            opener.open.side_effect = urllib.error.HTTPError(ops.REPORT_URL, code,
                "SENSITIVE_PROVIDER_TEXT", {}, io.BytesIO(b"SENSITIVE_BODY"))
            with patch.object(ops.urllib.request, "build_opener", return_value=opener):
                with self.assertRaises(ValueError) as caught: ops.fetch_report({}, "SYNTHETIC_SECRET")
            self.assertNotIn("SENSITIVE", str(caught.exception))
            self.assertNotIn("SYNTHETIC", str(caught.exception))
            self.assertIn(str(code), str(caught.exception))
            self.assertEqual(opener.open.call_count, 1)

    def test_cli_default_is_dry_and_no_token_or_response_in_stdout(self):
        argv = ["privacy_ops.py", "export-month", "--month", "2026-08", "--timezone", "Asia/Seoul",
                "--archive-dir", str(self.archive), "--access-token-file", str(self.token)]
        with patch.object(ops.sys, "argv", argv), patch.object(ops, "fetch_report") as fetch, \
                patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(ops.main(), 0)
        fetch.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())["mode"], "DRY_RUN")
        self.assertFalse(self.archive.exists())
        self.assertNotIn("SYNTHETIC_TOKEN", output.getvalue())

    def test_cli_malformed_json_does_not_echo_response(self):
        argv = ["privacy_ops.py", "export-month", "--month", "2026-08", "--timezone", "Asia/Seoul",
                "--archive-dir", str(self.archive), "--access-token-file", str(self.token), "--execute"]
        with patch.object(ops.sys, "argv", argv), \
                patch.object(ops, "fetch_report", side_effect=json.JSONDecodeError("SENSITIVE", "SENSITIVE", 0)), \
                patch("sys.stderr", new_callable=io.StringIO) as output:
            self.assertEqual(ops.main(), 2)
        self.assertNotIn("SENSITIVE", output.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
