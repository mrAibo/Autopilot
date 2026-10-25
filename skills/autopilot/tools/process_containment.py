#!/usr/bin/env python3
"""Fail-closed ownership of a Windows Job Object for a gated child tree.

Windows: CreateJobObject with KILL_ON_JOB_CLOSE; gate stays inert until the
supervisor assigns it to the job and sends START. The job handle is owned
solely by the supervisor. A parent crash closes it in the kernel.
Non-Windows: POSIX process-group cancellation; parent death containment is
NOT claimed. No silent Windows fallback.
"""
import ctypes
import os


class ContainmentError(OSError):
    pass


if os.name == "nt":
    from ctypes import wintypes

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [(k, ctypes.c_ulonglong) for k in (
            "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
            "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

    class BASIC_LIMITS(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class EXTENDED_LIMITS(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", BASIC_LIMITS),
            ("IoInfo", IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel.SetInformationJobObject.restype = wintypes.BOOL
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    kernel.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel.TerminateJobObject.restype = wintypes.BOOL

    JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    PROCESS_SET_QUOTA = 0x0100
    PROCESS_TERMINATE = 0x0001


class OwnedJob:
    """Close is irrevocable: only its owner may assign/kill/close this job."""

    def __init__(self):
        self.handle = None
        if os.name == "nt":
            handle = kernel.CreateJobObjectW(None, None)
            if not handle:
                raise ContainmentError(ctypes.get_last_error(), "CreateJobObjectW failed")
            self.handle = handle
            info = EXTENDED_LIMITS()
            info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            if not kernel.SetInformationJobObject(
                    handle, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
                    ctypes.byref(info), ctypes.sizeof(info)):
                error = ctypes.get_last_error()
                self.close()
                raise ContainmentError(error, "SetInformationJobObject failed")

    @property
    def mode(self):
        return "windows-kill-on-job-close" if os.name == "nt" else "posix-session-only"

    def assign(self, process):
        if os.name != "nt":
            return
        if self.handle is None:
            raise ContainmentError("Job Object is closed")
        handle = kernel.OpenProcess(PROCESS_SET_QUOTA | PROCESS_TERMINATE,
                                    False, process.pid)
        if not handle:
            raise ContainmentError(ctypes.get_last_error(), "OpenProcess failed")
        try:
            if not kernel.AssignProcessToJobObject(self.handle, handle):
                raise ContainmentError(ctypes.get_last_error(),
                                       "AssignProcessToJobObject denied; NO execution")
        finally:
            kernel.CloseHandle(handle)

    def terminate(self):
        if os.name == "nt" and self.handle is not None:
            if not kernel.TerminateJobObject(self.handle, 23):
                raise ContainmentError(ctypes.get_last_error(), "TerminateJobObject failed")

    def close(self):
        if self.handle is not None:
            kernel.CloseHandle(self.handle)
            self.handle = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
