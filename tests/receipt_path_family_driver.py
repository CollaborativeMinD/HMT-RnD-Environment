"""One declared causal arm on its own source copy; verification-only compensation."""
import json
import sys
from pathlib import Path

import pytest
from receipt_path_worker import perform
from test_receipt_path_support import prepare
from test_revision_issuance_support import snapshot


def main(root, arm):
    root.mkdir()
    with pytest.MonkeyPatch.context() as patch:
        scope, host, owner, request, store, first, candidate, seen, other = prepare(
            root, patch, True, True)
        before = snapshot(host)
        patch.chdir(root if arm == "alternate_on" else other)
        actual = perform(scope, "verify")
        after = snapshot(host)
        expected = "LANE_ARTIFACT_SCOPE" if arm in {"delete", "alternate_off"} else None
        record = {"arm": arm, "actual": actual, "expected_error": expected,
                  "issuer_cwd_restored": arm == "alternate_on",
                  "persisted_absolute": first.candidate.artifact.is_absolute(),
                  "tables_unchanged_by_verification": before == after,
                  "receipt_immutable": store.receipt("first") == first,
                  "claim_limit": "Alternate-on compensates the read only; its relative receipt "
                                 "still violates the new persistence contract and is not promoted."}
        print(json.dumps(record))
        assert actual.get("error") == expected
        assert before == after and store.receipt("first") == first
        if arm in {"intact", "restore", "sham"}:
            assert first.candidate.artifact.is_absolute()
        else:
            assert not first.candidate.artifact.is_absolute()


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2])
