"""Offline child-process dispatch, cancellation, receipt and Git integration."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                        "skills" / "autopilot" / "tools"))
import offline_supervisor
import test_ap


class OfflineSupervisorRealGit(unittest.TestCase):
    def setUp(self):
        h = test_ap.Run("test_init_creates_run")
        h.setUp()
        self.h = h
        self.addCleanup(h.tearDown)
        h.plan(strict=True, isolated=True)
        self.assertEqual(h.ap("tickets")[0], 0)
        cap = Path(h.a) / "model-capabilities.json"
        cap.write_text(json.dumps({
            "provider": "anthropic", "model_selection": True,
            "models": {"haiku": ["low"]}
        }), encoding="utf-8")
        for tid in ("01", "02"):
            rc, out = h.ap("ticket", tid, "route", "--provider", "anthropic",
                           "--model", "haiku", "--effort", "low",
                           "--reason", "offline-no-provider",
                           "--capabilities", str(cap))
            self.assertEqual(rc, 0, out)
        h.git("config", "user.email", "test@example.invalid")
        h.git("config", "user.name", "Autopilot Offline Process Tests")
        core = Path(h.root) / "src" / "core"
        bot = Path(h.root) / "src" / "bot"
        core.mkdir(parents=True)
        bot.mkdir(parents=True)
        (core / "calc.py").write_text(
            "def add(a, b):\n    return a - b\n", encoding="utf-8")
        (bot / "calc.py").write_text(
            "def mul(a, b):\n    return a + b\n", encoding="utf-8")
        for folder, name, expected in (("core", "add", 5), ("bot", "mul", 6)):
            (Path(h.root) / ("test_" + folder + ".py")).write_text(
                "import unittest\n"
                + f"from src.{folder}.calc import {name}\n"
                + f"class T(unittest.TestCase):\n"
                + f" def test_calc(self): self.assertEqual({name}(2, 3), {expected})\n",
                encoding="utf-8")
        h.git("add", "src", "test_core.py", "test_bot.py", ".gitignore")
        h.commit("offline fixture baseline")
        (Path(h.a) / "offline-test-consent").write_text(
            offline_supervisor.MARKER, encoding="utf-8")
        for tool in ("offline_supervisor.py", "offline_fixture_worker.py",
                     "host_loop.py", "process_containment.py", "process_gate.py"):
            shutil.copy(Path(offline_supervisor.__file__).parent / tool,
                        Path(h.a) / tool)

    def invoke(self, *args, timeout=70):
        h = self.h
        result = subprocess.run(
            [sys.executable, str(Path(h.a) / "offline_supervisor.py"),
             "--root", h.root, "--ticket", "01", *args],
            cwd=h.root, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout)
        self.assertTrue(result.stdout.strip(), result.stderr)
        return result.returncode, json.loads(result.stdout)

    def host(self, *options):
        h = self.h
        result = subprocess.run(
            [sys.executable, str(Path(h.a) / "host_loop.py"),
             "--root", h.root, *options], cwd=h.root,
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=65)
        self.assertTrue(result.stdout.strip(), result.stderr)
        return result.returncode, json.loads(result.stdout)

    def start_first(self):
        rc, out = self.host("--advance")
        self.assertEqual(rc, 0, out)
        self.assertEqual([x["action"] for x in out["completed"]],
                         ["prepare", "start"])
        self.assertEqual(out["status"], "paused")

    def test_real_offline_dispatch_accept_and_cancel_second(self):
        h = self.h
        self.start_first()
        rc, preview = self.invoke("--fixture", "calc-add")
        self.assertEqual(rc, 0, preview)
        self.assertEqual(preview["status"], "dry-run")
        self.assertFalse((Path(h.a) / "offline-worker").exists())
        rc, denied = self.invoke("--fixture", "calc-add", "--execute")
        self.assertEqual(rc, 2, denied)
        self.assertFalse((Path(h.a) / "offline-worker").exists())
        rc, result = self.invoke(
            "--fixture", "calc-add", "--execute",
            "--approve-offline-ticket", "01")
        self.assertEqual(rc, 0, result)
        self.assertEqual(result["status"], "completed")
        self.assertFalse(result["model_invoked"])
        receipt = offline_supervisor.read_receipt(h.root, "01")
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["fixture"], "calc-add")
        rc, repeat = self.invoke("--fixture", "calc-add",
                                 "--execute", "--approve-offline-ticket", "01")
        self.assertEqual(rc, 2, repeat)
        self.assertEqual(repeat["status"], "blocked")

        rc, accepted = self.host("--advance", "--suite", "01=test_core.py")
        self.assertEqual(rc, 0, accepted)
        self.assertEqual([x["action"] for x in accepted["completed"]],
                         ["verify", "finalize", "land", "accept", "release",
                          "prepare", "start"])
        self.assertEqual(h.state()["tickets"][0]["status"], "done")

        cmd = [sys.executable, str(Path(h.a) / "offline_supervisor.py"),
               "--root", h.root, "--ticket", "02",
               "--fixture", "calc-mul", "--execute",
               "--approve-offline-ticket", "02", "--delay", "10"]
        child = subprocess.Popen(cmd, cwd=h.root,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 text=True, encoding="utf-8", errors="replace")
        try:
            until = time.monotonic() + 12
            while time.monotonic() < until:
                try:
                    receipt = offline_supervisor.read_receipt(h.root, "02")
                except (OSError, ValueError):
                    receipt = None  # May still be claiming a fresh receipt.
                if receipt and receipt["status"] == "running":
                    break
                if child.poll() is not None:
                    self.fail("Supervisor exited before cancellation")
                time.sleep(0.05)
            else:
                self.fail("Supervisor never started offline fixture")
            cancel = subprocess.run(
                [sys.executable, str(Path(h.a) / "offline_supervisor.py"),
                 "--root", h.root, "--ticket", "02", "--cancel"],
                cwd=h.root, capture_output=True, text=True,
                encoding="utf-8", timeout=15)
            self.assertEqual(cancel.returncode, 0, cancel.stdout + cancel.stderr)
            self.assertEqual(json.loads(cancel.stdout)["status"], "cancel-requested")
            stdout, stderr = child.communicate(timeout=25)
            self.assertEqual(child.returncode, 0, stdout + stderr)
            self.assertEqual(json.loads(stdout)["status"], "cancelled")
        finally:
            if child.poll() is None:
                child.kill()
                child.communicate(timeout=10)
        record = offline_supervisor.read_receipt(h.root, "02")
        self.assertEqual(record["status"], "cancelled")
        self.assertTrue(record["cancel_acknowledged_at"])
        self.assertEqual(len(record["claim_id"]), 32)
        wt = Path(h.state()["tickets"][1]["worktree"]["cwd"])
        self.assertEqual((wt / "src" / "bot" / "calc.py").read_text(encoding="utf-8"),
                         "def mul(a, b):\n    return a + b\n")
        self.assertEqual(h.state()["tickets"][1]["status"], "in-progress")
        self.assertFalse(h.state()["usageEvents"])
        # No retry, and no fabricated test success or acceptance.
        rc, denied = subprocess_run_cancelled_replay(h, "02")
        self.assertEqual(rc, 2, denied)
        self.assertEqual(denied["status"], "blocked")

    def test_failed_worker_has_non_replayable_receipt(self):
        self.start_first()
        rc, result = self.invoke("--fixture", "calc-add", "--execute",
                                  "--approve-offline-ticket", "01", "--fail")
        self.assertEqual(rc, 2, result)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(offline_supervisor.read_receipt(self.h.root, "01")
                         ["status"], "failed")
        rc, denied = self.invoke("--fixture", "calc-add", "--execute",
                                 "--approve-offline-ticket", "01")
        self.assertEqual(rc, 2, denied)
        self.assertEqual(denied["status"], "blocked")
        self.assertFalse(self.h.state()["usageEvents"])

    def test_worker_timeout_is_non_replayable(self):
        self.start_first()
        rc, result = self.invoke("--fixture", "calc-add", "--execute",
                                  "--approve-offline-ticket", "01",
                                  "--delay", "5", "--timeout", "2")
        self.assertEqual(rc, 2, result)
        self.assertEqual(result["status"], "timed-out")
        self.assertEqual(offline_supervisor.read_receipt(self.h.root, "01")
                         ["status"], "timed-out")
        rc, denied = self.invoke("--fixture", "calc-add", "--execute",
                                 "--approve-offline-ticket", "01")
        self.assertEqual(rc, 2, denied)

    def test_crash_after_durable_claim_never_replays(self):
        self.start_first()
        summary = offline_supervisor.preflight(
            self.h.root, "01", "calc-add", timeout=3)
        with offline_supervisor.controller.controller_lock(
                Path(self.h.root)):
            path, claimed = offline_supervisor.claim(
                Path(self.h.root), "01", summary)
        self.assertTrue(path.is_file())
        self.assertEqual(claimed["status"], "invocation-uncertain")
        rc, denied = self.invoke("--fixture", "calc-add", "--execute",
                                 "--approve-offline-ticket", "01")
        self.assertEqual(rc, 2, denied)
        self.assertEqual(denied["status"], "blocked")
        self.assertEqual(self.h.state()["tickets"][0]["status"], "in-progress")

    def test_cancel_absent_receipt_does_not_create_one(self):
        self.start_first()
        rc, out = self.invoke("--cancel")
        self.assertEqual(rc, 2, out)
        self.assertEqual(out["status"], "blocked")
        self.assertFalse((Path(self.h.a) / "offline-worker").exists())

    @unittest.skipUnless(sys.platform == "win32", "Requires Windows Job Objects")
    def test_windows_parent_kill_terminates_child_tree(self):
        """Open the gate handle before killing parent to avoid PID reuse races."""
        import ctypes
        from ctypes import wintypes

        self.start_first()
        cmd = [sys.executable, str(Path(self.h.a) / "offline_supervisor.py"),
               "--root", self.h.root, "--ticket", "01",
               "--fixture", "calc-add", "--execute",
               "--approve-offline-ticket", "01", "--delay", "15",
               "--timeout", "30"]
        supervisor = subprocess.Popen(
            cmd, cwd=self.h.root, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace")
        handle = None
        try:
            limit = time.monotonic() + 12
            while time.monotonic() < limit:
                rec = offline_supervisor.read_receipt(self.h.root, "01")
                if rec and rec["status"] == "running":
                    break
                if supervisor.poll() is not None:
                    out, err = supervisor.communicate(timeout=5)
                    self.fail("Supervisor exited before job assignment, exit=%d, stderr=%r, stdout=%r" %
                              (supervisor.returncode, err[-1000:], out[-700:]))
                time.sleep(0.05)
            else:
                self.fail("Worker gate never became contained")
            self.assertEqual(rec["containment"], "windows-kill-on-job-close")
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL,
                                          wintypes.DWORD]
            kernel.OpenProcess.restype = wintypes.HANDLE
            kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE,
                                                    wintypes.DWORD]
            kernel.WaitForSingleObject.restype = wintypes.DWORD
            kernel.CloseHandle.argtypes = [wintypes.HANDLE]
            handle = kernel.OpenProcess(0x00100000, False, rec["child_pid"])
            self.assertTrue(handle, "Must hold genuine gate process handle")
            self.assertEqual(kernel.WaitForSingleObject(handle, 0), 0x102)
            supervisor.kill()
            supervisor.communicate(timeout=10)
            self.assertEqual(kernel.WaitForSingleObject(handle, 5000), 0,
                             "Windows kernel must kill child when parent job closes")
            self.assertEqual(
                (Path(rec["cwd"]) / "src" / "core" / "calc.py")
                .read_text(encoding="utf-8"),
                "def add(a, b):\n    return a - b\n")
            # The receipt is intentionally not 'completed': no replay.
            rc, denied = self.invoke("--fixture", "calc-add",
                                     "--execute", "--approve-offline-ticket", "01")
            self.assertEqual(rc, 2, denied)
            self.assertEqual(denied["status"], "blocked")
            rc, state = self.invoke("--status")
            self.assertEqual(rc, 0, state)
            self.assertTrue(state["manual_reconciliation_required"])
        finally:
            if handle is not None:
                kernel.CloseHandle(handle)
            if supervisor.poll() is None:
                supervisor.kill()
            supervisor.communicate(timeout=10)

    def test_receipt_status_and_cancel_ack(self):
        self.start_first()
        rc, before = self.invoke("--status")
        self.assertEqual(rc, 0, before)
        self.assertEqual(before["status"], "no-attempt")
        rc, result = self.invoke("--fixture", "calc-add",
                                  "--execute", "--approve-offline-ticket", "01")
        self.assertEqual(rc, 0, result)
        rc, state = self.invoke("--status")
        self.assertEqual(rc, 0, state)
        self.assertEqual(state["recorded_status"], "completed")
        self.assertFalse(state["manual_reconciliation_required"])

    def test_invalid_preflight_cannot_claim_or_launch(self):
        self.start_first()
        rc, bad = self.invoke("--fixture", "calc-mul", "--execute",
                              "--approve-offline-ticket", "01")
        self.assertEqual(rc, 2, bad)
        self.assertEqual(bad["status"], "blocked")
        self.assertFalse((Path(self.h.a) / "offline-worker").exists())
        (Path(self.h.a) / "offline-test-consent").unlink()
        rc, denied = self.invoke("--fixture", "calc-add", "--execute",
                                 "--approve-offline-ticket", "01")
        self.assertEqual(rc, 2, denied)
        self.assertFalse((Path(self.h.a) / "offline-worker").exists())


def subprocess_run_cancelled_replay(h, ticket):
    proc = subprocess.run(
        [sys.executable, str(Path(h.a) / "offline_supervisor.py"),
         "--root", h.root, "--ticket", ticket,
         "--fixture", "calc-mul", "--execute",
         "--approve-offline-ticket", ticket],
        cwd=h.root, capture_output=True, text=True, timeout=12)
    return proc.returncode, json.loads(proc.stdout)


if __name__ == "__main__":
    unittest.main()
