"""Endpoint dedup never accepts another payload under prior identity."""
import pytest
from test_custody_support import setup

from hmt_rnd.custody_database import CustodyFault


def test_same_reservation_changed_payload_rejected(tmp_path):
    store, endpoint, _ = setup(tmp_path)
    reserved = store.reserve("alice", "effect1")
    endpoint.apply(reserved)
    changed = reserved.model_copy(update={
        "intent": reserved.intent.model_copy(update={"payload_digest": "b" * 64})})
    with pytest.raises(CustodyFault, match="RESERVATION_COLLISION"):
        endpoint.apply(changed)


def test_new_reservation_cannot_change_existing_effect_payload(tmp_path):
    store, endpoint, _ = setup(tmp_path)
    reserved = store.reserve("alice", "effect1")
    endpoint.apply(reserved)
    changed = reserved.model_copy(update={
        "reservation_id": "different-reservation",
        "intent": reserved.intent.model_copy(update={"payload_digest": "b" * 64})})
    with pytest.raises(CustodyFault, match="INTENT_COLLISION"):
        endpoint.apply(changed)
