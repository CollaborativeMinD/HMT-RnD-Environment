"""A missing valid-root descendant is drift; an unavailable root is a scope denial."""
from pathlib import Path

import pytest

from hmt_rnd.lane_drift import source_changed


def test_missing_root_is_not_missing_source_drift(tmp_path):
    root = tmp_path / "missing-root"
    with pytest.raises(PermissionError, match="LANE_ARTIFACT_SCOPE"):
        source_changed(root / "source", "a" * 64, root)


@pytest.mark.parametrize("scope", ["directory", "filesystem-root"])
def test_missing_descendant_below_valid_root_is_drift(tmp_path, scope):
    root = tmp_path if scope == "directory" else Path(tmp_path.anchor)
    assert source_changed(tmp_path / "missing-directory" / "source", "a" * 64, root)
