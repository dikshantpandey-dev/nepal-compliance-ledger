"""
NCL data models.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class AgentType(Enum):
    HONEST = "HONEST"
    MALICIOUS = "MALICIOUS"


class TxStatus(Enum):
    APPROVED = "CLEAN"
    BLOCKED_VELOCITY = "FLAGGED:VELOCITY"
    BLOCKED_CYCLE = "FLAGGED:CYCLE"


@dataclass
class Agent:
    id: str
    agent_type: AgentType
    bank: str
    attack_type: str = "benign"


@dataclass
class Transaction:
    tx_hash: str
    timestamp: float
    sender_id: str
    receiver_id: str
    amount: float
    status: TxStatus = TxStatus.APPROVED
    is_malicious: bool = False
    attack_type: str = "benign"


@dataclass
class LedgerBlock:
    index: int
    timestamp: float
    prev_hash: str
    merkle_root: str
    tx_count: int
    policy_hash: str
    proposer: str
    validator_signatures: Dict[str, str]
    block_hash: str


@dataclass
class LedgerReceipt:
    block_index: int
    block_hash: str
    tx_hashes: List[str]
