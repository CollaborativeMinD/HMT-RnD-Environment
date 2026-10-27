"""Drift classification preserves original scope, parent and regular-file policy."""
import hashlib
import os

import pytest

from hmt_rnd.lane_drift import source_changed
from hmt_rnd.lane_evidence import digest_file


@pytest.mark.parametrize("kind", ["outside_link", "outside_dangling", "parent_inside",
                                  "parent_outside", "path_parent", "root_parent",
                                  "root_link", "root_file", "directory", "fifo"])
def test_disallowed_sources_are_not_missing_source_drift(tmp_path, kind):
    root, outside = tmp_path / "root", tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    nested = root / "nested"
    nested.mkdir()
    path = root / "source"
    path.write_bytes(b"valid")
    (nested / "source").write_bytes(b"valid")
    (outside / "source").write_bytes(b"other")
    if kind.startswith("outside_"):
        path.unlink()
        path.symlink_to(outside / ("absent" if kind.endswith("dangling") else "source"))
    elif kind.startswith("parent_") or kind == "root_link":
        link = root / "link"
        link.symlink_to(outside if kind == "parent_outside" else nested)
        path = link / "source"
        if kind == "root_link":
            root = link
    elif kind == "path_parent":
        path = nested / ".." / "source"
    elif kind == "root_parent":
        root = nested / ".."
    elif kind == "root_file":
        root, path = path, path / "source"
    else:
        path.unlink()
        path.mkdir() if kind == "directory" else os.mkfifo(path)
    with pytest.raises(PermissionError, match="LANE_ARTIFACT_SCOPE"):
        digest_file(path, root)
    with pytest.raises(PermissionError, match="LANE_ARTIFACT_SCOPE"):
        source_changed(path, hashlib.sha256(b"valid").hexdigest(), root)


def test_normal_regular_sources_keep_unchanged_and_changed_controls(tmp_path):
    path = tmp_path / "source"
    path.write_bytes(b"original")
    expected = hashlib.sha256(b"original").hexdigest()
    assert source_changed(path, expected, tmp_path) is False
    path.write_bytes(b"changed")
    assert source_changed(path, expected, tmp_path) is True


def test_unavailable_normalization_context_is_scope_denial(tmp_path, monkeypatch):
    from hmt_rnd import lane_reader

    def unavailable_cwd(path):
        raise FileNotFoundError("controlled unavailable cwd")

    with monkeypatch.context() as patch:
        patch.setattr(lane_reader.os.path, "abspath", unavailable_cwd)
        with pytest.raises(PermissionError, match="LANE_ARTIFACT_SCOPE") as caught:
            source_changed(tmp_path / "source", "a" * 64, tmp_path)
    assert not isinstance(caught.value.__cause__, FileNotFoundError)
