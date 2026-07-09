"""
NCL Data Models - Agent, Transaction
"""

from dataclasses import dataclass
from enum import Enum


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


@dataclass
class Transaction:
    tx_hash: str
    timestamp: float
    sender_id: str
    receiver_id: str
    amount: float
    status: TxStatus = TxStatus.APPROVED
    is_malicious: bool = False      # ground truth label for evaluation
