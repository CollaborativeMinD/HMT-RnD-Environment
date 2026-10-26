"""Authenticated endpoint proofs; host provisions trust roots."""
import hashlib
import hmac

from .custody_database import CustodyFault
from .custody_models import Proof


def sign(proof: Proof, key: bytes) -> str:
    if len(key) < 32:
        raise CustodyFault("ENDPOINT_KEY_INVALID")
    unsigned = proof.model_copy(update={"signature": "0" * 64})
    return hmac.new(key, unsigned.model_dump_json().encode(), hashlib.sha256).hexdigest()


def verify(proof: Proof, key: bytes) -> None:
    if not hmac.compare_digest(sign(proof, key), proof.signature):
        raise CustodyFault("PROOF_SIGNATURE_INVALID")
