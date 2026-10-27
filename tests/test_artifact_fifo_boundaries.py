"""Regular bytes, limits, symlinks and descriptor replacement keep exact oracles."""
import hashlib
import os

import pytest
from test_artifact_fifo_support import observe

MODES = ["digest", "snapshot"]


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", [0, 16777216, 16777217])
def test_exact_regular_file_bounds(tmp_path, mode, size):
    path = tmp_path / "source"
    body = b"x" * size
    path.write_bytes(body)
    if size > 16777216:
        reason = "LANE_ARTIFACT_BOUND" if mode == "digest" else "LANE_SNAPSHOT_TOTAL_BOUND"
        with pytest.raises(PermissionError, match=reason):
            observe(mode, path, tmp_path, body)
    else:
        assert observe(mode, path, tmp_path, body) == hashlib.sha256(body).hexdigest()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("kind", ["missing", "directory", "symlink", "parent_link", "escape"])
def test_scope_and_file_type_are_closed(tmp_path, mode, kind):
    root = tmp_path / "scope"
    root.mkdir()
    real = root / "real"
    real.mkdir()
    (real / "source").write_bytes(b"data")
    path = root / "source"
    if kind == "directory":
        path.mkdir()
    if kind == "symlink":
        path.symlink_to(real / "source")
    if kind == "parent_link":
        path.symlink_to(real, target_is_directory=True)
        path = path / "source"
    if kind == "escape":
        path = tmp_path / "outside"
        path.write_bytes(b"data")
    reason = "LANE_ARTIFACT_SCOPE" if mode == "digest" else "LANE_SNAPSHOT_SCOPE"
    with pytest.raises(PermissionError, match=reason):
        observe(mode, path, root, b"data")


@pytest.mark.parametrize("mode", MODES)
def test_read_remains_bound_to_opened_descriptor(tmp_path, mode, monkeypatch):
    path = tmp_path / "source"
    path.write_bytes(b"original")
    native_fstat = os.fstat

    def replace_after_open(descriptor):
        if path.is_file():
            path.unlink()
            os.mkfifo(path)
        return native_fstat(descriptor)

    monkeypatch.setattr(os, "fstat", replace_after_open)
    assert observe(mode, path, tmp_path, b"original") == hashlib.sha256(b"original").hexdigest()
