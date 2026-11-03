"""run_contained: a timeout kills the whole descendant tree, not just the child."""
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"))
import process_containment

# The child starts a grandchild that sleeps for a minute and writes its pid, then sleeps itself.
GRANDCHILD = "import os, sys, time; open(sys.argv[1], 'w').write(str(os.getpid())); time.sleep(60)"
CHILD = ("import subprocess, sys, time; "
         "subprocess.Popen([sys.executable, '-c', sys.argv[2], sys.argv[1]]); time.sleep(60)")


def alive(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    try:                                   # a zombie still answers kill(0)
        with open("/proc/%d/stat" % pid) as stat:
            return stat.read().rsplit(")", 1)[1].split()[0] != "Z"
    except OSError:
        return True


class RunContainedTests(unittest.TestCase):
    def test_success_returns_completed_process_with_text_output(self):
        done = process_containment.run_contained(
            [sys.executable, "-c", "import sys; print('hello'); print('err', file=sys.stderr); sys.exit(3)"],
            timeout=30)
        self.assertEqual((done.returncode, done.stdout.strip(), done.stderr.strip()), (3, "hello", "err"))

    def test_cwd_and_env_are_passed(self):
        with tempfile.TemporaryDirectory() as cwd:
            done = process_containment.run_contained(
                [sys.executable, "-c", "import os; print(os.getcwd()); print(os.environ['AP_X'])"],
                timeout=30, cwd=cwd, env=dict(os.environ, AP_X="42"))
        self.assertEqual(done.stdout.split(), [os.path.realpath(cwd), "42"])

    def test_timeout_raises_after_killing_the_child(self):
        started = time.monotonic()
        with self.assertRaises(subprocess.TimeoutExpired):
            process_containment.run_contained(
                [sys.executable, "-c", "import time; time.sleep(60)"], timeout=1)
        self.assertLess(time.monotonic() - started, 20)

    def test_failing_terminate_still_kills_the_child_and_keeps_the_timeout_in_the_chain(self):
        procs, real_popen = [], subprocess.Popen

        def spy(*args, **kwargs):
            procs.append(real_popen(*args, **kwargs))
            return procs[-1]

        boom = process_containment.ContainmentError("boom")
        with mock.patch.object(process_containment.subprocess, "Popen", spy), \
                mock.patch.object(process_containment.OwnedJob, "terminate", side_effect=boom),                 mock.patch.object(process_containment.OwnedJob, "close"):  # Job close would kill it on Windows
            with self.assertRaises(process_containment.ContainmentError) as caught:
                process_containment.run_contained(
                    [sys.executable, "-c", "import time; time.sleep(60)"], timeout=1)
        self.assertIsNotNone(procs[0].wait(timeout=10), "child survived a failing terminate")
        self.assertIsInstance(caught.exception.__context__, subprocess.TimeoutExpired)

    @unittest.skipUnless(os.name == "posix" and os.path.isdir("/proc"),
                         "grandchild liveness check uses POSIX /proc")
    def test_timeout_kills_the_grandchild_too(self):
        with tempfile.TemporaryDirectory() as tmp:
            pid_file = Path(tmp) / "grandchild.pid"
            with self.assertRaises(subprocess.TimeoutExpired):
                process_containment.run_contained(
                    [sys.executable, "-c", CHILD, str(pid_file), GRANDCHILD], timeout=2)
            deadline = time.monotonic() + 5
            while not pid_file.exists() and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertTrue(pid_file.exists(), "the grandchild never started")
            pid = int(pid_file.read_text())
            for _ in range(100):
                if not alive(pid):
                    break
                time.sleep(0.05)
            self.assertFalse(alive(pid), "grandchild survived the timeout")


class OwnedJobPosixTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "posix", "killpg is POSIX only")
    def test_terminate_kills_the_process_group(self):
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
                                start_new_session=True)
        with process_containment.OwnedJob() as job:
            job.assign(proc)
            job.terminate()
        self.assertEqual(proc.wait(timeout=10), -9)

    @unittest.skipUnless(os.name == "posix", "killpg is POSIX only")
    def test_terminate_never_signals_our_own_group(self):
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])  # same group
        self.addCleanup(proc.wait)
        self.addCleanup(proc.kill)
        with process_containment.OwnedJob() as job:
            job.assign(proc)
            job.terminate()                      # must be a no-op, and we must survive it
        self.assertIsNone(proc.poll())


if __name__ == "__main__":
    unittest.main()
