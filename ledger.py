"""
NCL Immutable Ledger - Simulates Hyperledger Fabric append-only log
Hash-chained blocks ensure tamper-evident audit trail.
"""

import hashlib
import json

from models import Transaction


class ImmutableLedger:

    def __init__(self):
        self._blocks = []
        self._prev_hash = "0" * 64      # genesis hash

    def commit(self, tx: Transaction) -> str:
        """Append a transaction to the ledger and return the block hash."""
        entry = {
            "index": len(self._blocks),
            "tx_hash": tx.tx_hash,
            "timestamp": tx.timestamp,
            "sender": tx.sender_id,
            "receiver": tx.receiver_id,
            "amount": tx.amount,
            "status": tx.status.value,
            "prev_hash": self._prev_hash,
        }
        block_hash = hashlib.sha256(
            json.dumps(entry, sort_keys=True).encode()
        ).hexdigest()
        entry["block_hash"] = block_hash
        self._blocks.append(entry)
        self._prev_hash = block_hash
        return block_hash

    def verify_integrity(self) -> bool:
        """Walk the chain and verify every hash link is intact."""
        for i in range(1, len(self._blocks)):
            block = self._blocks[i]
            prev_block = self._blocks[i - 1]
            if block["prev_hash"] != prev_block["block_hash"]:
                return False
            entry = {k: v for k, v in prev_block.items() if k != "block_hash"}
            expected = hashlib.sha256(
                json.dumps(entry, sort_keys=True).encode()
            ).hexdigest()
            if prev_block["block_hash"] != expected:
                return False
        return True

    @property
    def size(self) -> int:
        return len(self._blocks)

    @property
    def blocks(self):
        return list(self._blocks)
