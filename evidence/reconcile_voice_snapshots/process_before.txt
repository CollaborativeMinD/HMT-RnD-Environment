"""Bound POSIX subprocess lifetime and combined pipe output; no shell invocation."""
import os
import selectors
import signal
import subprocess
import time

from .voice_models import ProcessResult


def terminate(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=1)


def drain(process: subprocess.Popen[bytes], timeout: float, limit: int) -> bytes:
    deadline, total, output = time.monotonic() + timeout, 0, bytearray()
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ, True)
        selector.register(process.stderr, selectors.EVENT_READ, False)
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("VOICE_PROCESS_TIMEOUT")
            for key, _ in selector.select(remaining):
                chunk = os.read(key.fd, 4096)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                total += len(chunk)
                if total > limit:
                    raise ValueError("VOICE_OUTPUT_LIMIT")
                if key.data:
                    output.extend(chunk)
        process.wait(timeout=max(0.001, deadline - time.monotonic()))
    return bytes(output)


def run_local(command: list[str], timeout: float, limit: int) -> ProcessResult:
    if os.name != "posix":
        raise ValueError("VOICE_PROCESS_PLATFORM_UNQUALIFIED")
    with subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, start_new_session=True,
                          env={"LANG": "C.UTF-8"}) as process:
        try:
            output = drain(process, timeout, limit)
        except BaseException:
            terminate(process)
            raise
        assert process.returncode is not None
        return ProcessResult(returncode=process.returncode, stdout=output)
