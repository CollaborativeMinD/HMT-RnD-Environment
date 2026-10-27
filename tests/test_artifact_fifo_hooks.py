"""Deterministic target replacement immediately before the actual open syscall."""
import json
import os
import sqlite3
from pathlib import Path


def install_swap(target: Path, database: Path) -> None:
    original_path_open, original_os_open = Path.open, os.open
    swapped = False

    def swap() -> None:
        nonlocal swapped
        if swapped:
            return
        swapped = True
        assert target.is_file()
        target.unlink()
        os.mkfifo(target)
        locked = False
        with sqlite3.connect(database, timeout=0) as other:
            try:
                other.execute("BEGIN IMMEDIATE")
            except sqlite3.OperationalError as error:
                assert "locked" in str(error)
                locked = True
        print(json.dumps({"race": "regular-to-FIFO", "shared_host_locked": locked}), flush=True)
        assert locked

    def path_open(path, *args, **kwargs):
        if path == target:
            swap()
        return original_path_open(path, *args, **kwargs)

    def os_open(path, flags, mode=0o777, *, dir_fd=None):
        if str(path) in (str(target), target.name):
            swap()
        return original_os_open(path, flags, mode, dir_fd=dir_fd)

    Path.open, os.open = path_open, os_open
