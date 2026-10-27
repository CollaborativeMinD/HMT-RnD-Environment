"""Late final-component and parent-directory replacement cannot follow a symlink."""
import os

import pytest
from test_artifact_fifo_support import observe


@pytest.mark.parametrize("mode", ["digest", "snapshot"])
@pytest.mark.parametrize("component", ["file", "directory"])
def test_late_symlink_replacement_rejects_scope(tmp_path, mode, component, monkeypatch):
    root, outside = tmp_path / "root", tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    folder = root / "folder"
    folder.mkdir()
    target = folder / "source"
    target.write_bytes(b"public")
    (outside / "source").write_bytes(b"private")
    native_open = os.open
    replaced = []

    def substitute(path, flags, mode=0o777, *, dir_fd=None):
        selected = "source" if component == "file" else "folder"
        if str(path) == selected and not replaced:
            if component == "file":
                target.unlink()
                target.symlink_to(outside / "source")
            else:
                folder.rename(root / "retained")
                folder.symlink_to(outside, target_is_directory=True)
            replaced.append(component)
        return native_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(os, "open", substitute)
    reason = "LANE_ARTIFACT_SCOPE" if mode == "digest" else "LANE_SNAPSHOT_SCOPE"
    with pytest.raises(PermissionError, match=reason):
        observe(mode, target, root, b"public")
    assert replaced == [component]
