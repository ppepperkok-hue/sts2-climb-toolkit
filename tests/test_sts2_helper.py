import contextlib
import io
import json
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import sts2_helper  # noqa: E402

REQUESTS = []


class FakeApiHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _write(self, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        REQUESTS.append({"method": self.command, "path": self.path, "body": None})
        if self.path == "/state":
            self._write(
                {
                    "ok": True,
                    "data": {"screen": "MAP", "available_actions": [], "run": {}},
                }
            )
        else:
            self._write(
                {
                    "ok": False,
                    "error": {"code": "not_found", "message": "Route not found."},
                }
            )

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length)
        body = json.loads(raw.decode("utf-8")) if raw else None
        REQUESTS.append({"method": self.command, "path": self.path, "body": body})
        self._write(
            {
                "ok": True,
                "data": {
                    "action": (body or {}).get("action"),
                    "status": "completed",
                    "message": "Action completed.",
                    "state": {"screen": "MAP"},
                },
            }
        )


class HelperCliTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeApiHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.original_base = sts2_helper.BASE
        sts2_helper.BASE = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        sts2_helper.BASE = cls.original_base
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self):
        REQUESTS.clear()

    def run_cli(self, *args):
        old_argv = sys.argv
        stdout = io.StringIO()
        stderr = io.StringIO()
        code = 0
        sys.argv = ["sts2_helper.py", *args]
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                sts2_helper.main()
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
        finally:
            sys.argv = old_argv
        return code, stdout.getvalue(), stderr.getvalue()

    def test_state_rejects_extra_argument_before_network(self):
        code, _, err = self.run_cli("state", "--bogus")

        self.assertEqual(code, 2)
        self.assertEqual(REQUESTS, [])
        self.assertIn("unexpected argument: --bogus", err)

    def test_map_rejects_extra_argument_before_network(self):
        code, _, err = self.run_cli("map", "--bogus")

        self.assertEqual(code, 2)
        self.assertEqual(REQUESTS, [])
        self.assertIn("unexpected argument: --bogus", err)

    def test_bare_misspelled_command_is_not_posted(self):
        code, _, err = self.run_cli("stae")

        self.assertEqual(code, 2)
        self.assertEqual(REQUESTS, [])
        self.assertIn("unknown command or action: 'stae'", err)

    def test_bare_action_remains_supported(self):
        code, out, _ = self.run_cli("end_turn")

        self.assertEqual(code, 0)
        self.assertEqual(len(REQUESTS), 1)
        request = REQUESTS[0]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/action")
        self.assertEqual(
            request["body"],
            {
                "action": "end_turn",
                "card_index": None,
                "option_index": None,
                "target_index": None,
                "client_context": {"source": "codex", "tool_name": "end_turn"},
            },
        )
        self.assertEqual(json.loads(out)["action"], "end_turn")

    def test_bare_play_card_sends_card_and_target_indices(self):
        code, _, _ = self.run_cli("play_card", "--index", "0", "--target", "0")

        self.assertEqual(code, 0)
        self.assertEqual(len(REQUESTS), 1)
        body = REQUESTS[0]["body"]
        self.assertEqual(body["action"], "play_card")
        self.assertEqual(body["card_index"], 0)
        self.assertIsNone(body["option_index"])
        self.assertEqual(body["target_index"], 0)

    def test_act_play_card_sends_card_and_target_indices(self):
        code, _, _ = self.run_cli(
            "act", "play_card", "--index", "0", "--target", "0"
        )

        self.assertEqual(code, 0)
        self.assertEqual(len(REQUESTS), 1)
        body = REQUESTS[0]["body"]
        self.assertEqual(body["action"], "play_card")
        self.assertEqual(body["card_index"], 0)
        self.assertIsNone(body["option_index"])
        self.assertEqual(body["target_index"], 0)

    def test_negative_index_is_rejected_before_network(self):
        code, _, err = self.run_cli("act", "play_card", "--index", "-1")

        self.assertEqual(code, 2)
        self.assertEqual(REQUESTS, [])
        self.assertIn("--index expects a non-negative integer", err)

    def test_negative_target_is_rejected_before_network(self):
        code, _, err = self.run_cli("play_card", "--target", "-1")

        self.assertEqual(code, 2)
        self.assertEqual(REQUESTS, [])
        self.assertIn("--target expects a non-negative integer", err)

    def test_non_integer_index_is_rejected_before_network(self):
        code, _, err = self.run_cli("act", "play_card", "--index", "abc")

        self.assertEqual(code, 2)
        self.assertEqual(REQUESTS, [])
        self.assertIn("--index expects an integer", err)

    def test_missing_index_value_is_rejected_before_network(self):
        code, _, err = self.run_cli("act", "play_card", "--index")

        self.assertEqual(code, 2)
        self.assertEqual(REQUESTS, [])
        self.assertIn("--index requires a value", err)


if __name__ == "__main__":
    unittest.main()
