"""Descriptor-bound regular-file reads; every traversed component rejects symlinks."""
import os
import stat
from pathlib import Path


def scoped_descriptor(path: Path, root: Path) -> int:
    absolute = Path(os.path.abspath(path))
    scope = Path(os.path.abspath(root))
    if absolute == scope or not absolute.is_relative_to(scope):
        raise OSError("outside artifact root")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    directory = os.open(absolute.anchor, flags)
    try:
        for name in absolute.parts[1:-1]:
            child = os.open(name, flags, dir_fd=directory)
            os.close(directory)
            directory = child
        return os.open(absolute.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                       dir_fd=directory)
    finally:
        os.close(directory)


def read_regular(path: Path, root: Path, limit: int, scope_reason: str,
                 bound_reason: str) -> bytes:
    try:
        descriptor = scoped_descriptor(path, root)
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise OSError("artifact is not a regular file")
            with os.fdopen(descriptor, "rb", closefd=False) as stream:
                body = stream.read(limit + 1)
        finally:
            os.close(descriptor)
    except OSError as error:
        raise PermissionError(scope_reason) from error
    if len(body) > limit:
        raise PermissionError(bound_reason)
    return body
