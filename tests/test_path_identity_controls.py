"""Parent traversal rejects before normalization; canonical and relative paths retain parity."""
import hashlib
from pathlib import Path

import pytest
from test_artifact_fifo_support import observe
from test_lane_tracer import setup_host
from test_path_identity_support import INSIDE, OUTSIDE, alias_fixture, candidate_for, gate_for

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_reader import scoped_descriptor
from hmt_rnd.lane_store import LaneStore


@pytest.mark.parametrize("mode", ["digest", "snapshot"])
@pytest.mark.parametrize("component", ["path", "root"])
@pytest.mark.parametrize("kind", ["directory", "jump"])
def test_parent_component_is_explicitly_rejected(tmp_path, mode, component, kind):
    root, _ = alias_fixture(tmp_path)
    (root / "directory").mkdir()
    path = root / "source"
    if component == "path":
        path = root / kind / ".." / "source"
    else:
        root = root / kind / ".."
    expected = OUTSIDE if component == "path" and kind == "jump" else INSIDE
    assert path.read_bytes() == expected
    reason = "LANE_ARTIFACT_SCOPE" if mode == "digest" else "LANE_SNAPSHOT_SCOPE"
    with pytest.raises(PermissionError, match=reason):
        observe(mode, path, root, INSIDE)


@pytest.mark.parametrize("component", ["path", "root"])
def test_rejection_precedes_normalization_and_open(tmp_path, component, monkeypatch):
    from hmt_rnd import lane_reader

    def forbidden(*args, **kwargs):
        raise AssertionError("normalization/open reached for parent traversal")

    monkeypatch.setattr(lane_reader.os.path, "abspath", forbidden)
    monkeypatch.setattr(lane_reader.os, "open", forbidden)
    path, root = tmp_path / "source", tmp_path
    if component == "path":
        path = tmp_path / "jump" / ".." / "source"
    else:
        root = tmp_path / "jump" / ".."
    with pytest.raises(OSError, match="parent traversal"):
        scoped_descriptor(path, root)


@pytest.mark.parametrize("relative", [False, True])
def test_valid_path_evaluator_digest_and_snapshot_match(tmp_path, relative, monkeypatch):
    root, _ = alias_fixture(tmp_path)
    host, identity, request = setup_host(root)
    store, evaluated = LaneStore(host), []
    path = root / "source"
    if relative:
        monkeypatch.chdir(tmp_path)
        path = Path("scope/source")
        for mode in ("digest", "snapshot"):
            assert observe(mode, path, Path("scope"), INSIDE) == hashlib.sha256(INSIDE).hexdigest()
    receipt = store.submit(identity, request, candidate_for(path), lambda: Clock(now=10.0),
                           lambda context: gate_for(context, root, evaluated))
    assert receipt.gate.outcome == "SEALED" and evaluated == [INSIDE.hex()]
    assert LaneStore(host).snapshot(receipt.candidate.artifact_sha256) == INSIDE
