"""
NCL permissioned blockchain ledger.

This is a deterministic simulation of the parts of a permissioned ledger that
matter for an AML compliance prototype: ordered blocks, Merkle roots, validator
quorum signatures, policy-version binding, and end-to-end chain verification.
"""

import hashlib
import json
from typing import Dict, List

from config import BLOCK_SIZE, POLICY_VERSION, VALIDATOR_QUORUM, VALIDATORS
from models import LedgerBlock, LedgerReceipt, Transaction


class PermissionedBlockchainLedger:

    def __init__(self):
        self._blocks: List[LedgerBlock] = []
        self._pending: List[Dict] = []
        self._prev_hash = "0" * 64
        self._policy_hash = hashlib.sha256(POLICY_VERSION.encode()).hexdigest()

    def commit(self, tx: Transaction) -> LedgerReceipt | None:
        """Append a transaction decision and seal a block when the batch is full."""
        self._pending.append(self._canonical_tx(tx))
        if len(self._pending) >= BLOCK_SIZE:
            return self._seal_block()
        return None

    def finalize(self) -> LedgerReceipt | None:
        """Seal the final partial block."""
        if self._pending:
            return self._seal_block()
        return None

    def _canonical_tx(self, tx: Transaction) -> Dict:
        return {
            "tx_hash": tx.tx_hash,
            "timestamp": tx.timestamp,
            "sender": tx.sender_id,
            "receiver": tx.receiver_id,
            "amount": tx.amount,
            "status": tx.status.value,
            "is_malicious": tx.is_malicious,
            "attack_type": tx.attack_type,
        }

    def _seal_block(self) -> LedgerReceipt:
        txs = self._pending
        self._pending = []
        merkle_root = self._merkle_root(txs)
        header = {
            "index": len(self._blocks),
            "timestamp": txs[-1]["timestamp"],
            "prev_hash": self._prev_hash,
            "merkle_root": merkle_root,
            "tx_count": len(txs),
            "policy_hash": self._policy_hash,
            "proposer": VALIDATORS[0],
        }
        block_hash = self._hash_json(header)
        signatures = self._collect_signatures(block_hash)
        block = LedgerBlock(
            **header,
            validator_signatures=signatures,
            block_hash=block_hash,
        )
        block._txs = txs  # internal audit payload, intentionally not in dataclass
        self._blocks.append(block)
        self._prev_hash = block_hash
        return LedgerReceipt(
            block_index=block.index,
            block_hash=block.block_hash,
            tx_hashes=[tx["tx_hash"] for tx in txs],
        )

    def verify_integrity(self) -> bool:
        """Verify hash links, block hashes, Merkle roots, and validator quorum."""
        prev_hash = "0" * 64
        for block in self._blocks:
            if block.prev_hash != prev_hash:
                return False
            if self._merkle_root(block._txs) != block.merkle_root:
                return False
            header = self._block_header(block)
            if self._hash_json(header) != block.block_hash:
                return False
            if not self._verify_quorum(block.block_hash, block.validator_signatures):
                return False
            prev_hash = block.block_hash
        return True

    def _block_header(self, block: LedgerBlock) -> Dict:
        return {
            "index": block.index,
            "timestamp": block.timestamp,
            "prev_hash": block.prev_hash,
            "merkle_root": block.merkle_root,
            "tx_count": block.tx_count,
            "policy_hash": block.policy_hash,
            "proposer": block.proposer,
        }

    def _collect_signatures(self, block_hash: str) -> Dict[str, str]:
        signatures = {}
        for validator in VALIDATORS[:VALIDATOR_QUORUM]:
            signatures[validator] = hashlib.sha256(
                f"{validator}:{block_hash}".encode()
            ).hexdigest()
        return signatures

    def _verify_quorum(self, block_hash: str, signatures: Dict[str, str]) -> bool:
        valid = 0
        for validator, signature in signatures.items():
            expected = hashlib.sha256(f"{validator}:{block_hash}".encode()).hexdigest()
            if validator in VALIDATORS and signature == expected:
                valid += 1
        return valid >= VALIDATOR_QUORUM

    @staticmethod
    def _hash_json(payload: Dict) -> str:
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    def _merkle_root(self, txs: List[Dict]) -> str:
        if not txs:
            return hashlib.sha256(b"").hexdigest()
        layer = [self._hash_json(tx) for tx in txs]
        while len(layer) > 1:
            if len(layer) % 2:
                layer.append(layer[-1])
            layer = [
                hashlib.sha256((layer[i] + layer[i + 1]).encode()).hexdigest()
                for i in range(0, len(layer), 2)
            ]
        return layer[0]

    @property
    def size(self) -> int:
        return len(self._blocks)

    @property
    def transaction_count(self) -> int:
        return sum(block.tx_count for block in self._blocks) + len(self._pending)

    @property
    def last_block_hash(self) -> str:
        return self._prev_hash

    @property
    def blocks(self) -> List[LedgerBlock]:
        return list(self._blocks)


class ImmutableLedger(PermissionedBlockchainLedger):
    """Backward-compatible alias for earlier NCL code."""

    pass
