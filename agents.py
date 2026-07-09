"""
NCL Agent-Based Model — Agent creation and transaction generation.

Agent types:
  - Honest (95%):     low-frequency, random legitimate transactions
  - Structurers:      high-frequency micro-transactions (smurfing)
  - Ring Traders:     circular layering in groups of 3
"""

import hashlib
from typing import List

from config import (
    BANKS,
    HONEST_TX_AMOUNT,
    HONEST_TX_INTERVAL,
    MALICIOUS_TX_AMOUNT,
    MALICIOUS_TX_INTERVAL,
    MALICIOUS_RATIO,
    NUM_AGENTS,
    RING_TX_AMOUNT,
    RING_TX_INTERVAL,
    SIMULATION_DURATION,
    STRUCTURER_RATIO,
)
from models import Agent, AgentType, Transaction


class AgentPool:

    def __init__(self, rng):
        self.rng = rng
        self.agents: List[Agent] = []
        self.malicious_ids: set = set()
        self._create_agents()

    # ---- agent creation ----

    def _create_agents(self):
        num_malicious = int(NUM_AGENTS * MALICIOUS_RATIO)

        for i in range(NUM_AGENTS):
            agent_type = AgentType.MALICIOUS if i < num_malicious else AgentType.HONEST
            agent = Agent(
                id=f"AGENT-{i:04d}",
                agent_type=agent_type,
                bank=self.rng.choice(BANKS),
            )
            self.agents.append(agent)
            if agent_type == AgentType.MALICIOUS:
                self.malicious_ids.add(agent.id)

        self.rng.shuffle(self.agents)

    # ---- transaction generation ----

    def generate_transactions(self) -> List[Transaction]:
        txs: List[Transaction] = []

        malicious = [a for a in self.agents if a.agent_type == AgentType.MALICIOUS]
        honest = [a for a in self.agents if a.agent_type == AgentType.HONEST]

        # -- honest transactions --
        for agent in honest:
            t = self.rng.uniform(0, 120)
            while t < SIMULATION_DURATION:
                receiver = self._pick_receiver(agent.id)
                amount = round(self.rng.uniform(*HONEST_TX_AMOUNT), 2)
                txs.append(self._make_tx(agent.id, receiver, amount, t, False))
                t += self.rng.uniform(*HONEST_TX_INTERVAL)

        # -- malicious: structurers --
        num_struct = int(len(malicious) * STRUCTURER_RATIO)
        structurers = malicious[:num_struct]
        ring_pool = malicious[num_struct:]

        for agent in structurers:
            t = self.rng.uniform(0, 60)
            while t < SIMULATION_DURATION:
                receiver = self._pick_receiver(agent.id)
                amount = round(self.rng.uniform(*MALICIOUS_TX_AMOUNT), 2)
                txs.append(self._make_tx(agent.id, receiver, amount, t, True))
                t += self.rng.uniform(*MALICIOUS_TX_INTERVAL)

        # -- malicious: ring traders (groups of 3) --
        for i in range(0, len(ring_pool) - 2, 3):
            ring = [ring_pool[i], ring_pool[i + 1], ring_pool[i + 2]]
            t = self.rng.uniform(0, 60)
            while t < SIMULATION_DURATION:
                for j in range(3):
                    sender = ring[j]
                    receiver = ring[(j + 1) % 3]
                    amount = round(self.rng.uniform(*RING_TX_AMOUNT), 2)
                    txs.append(
                        self._make_tx(sender.id, receiver.id, amount, t + j * 2, True)
                    )
                t += self.rng.uniform(*RING_TX_INTERVAL)

        txs.sort(key=lambda tx: tx.timestamp)
        return txs

    # ---- helpers ----

    def _pick_receiver(self, sender_id: str) -> str:
        while True:
            agent = self.rng.choice(self.agents)
            if agent.id != sender_id:
                return agent.id

    @staticmethod
    def _make_tx(sender: str, receiver: str, amount: float,
                 timestamp: float, is_malicious: bool) -> Transaction:
        raw = f"{sender}:{receiver}:{amount}:{timestamp}"
        tx_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return Transaction(
            tx_hash=tx_hash,
            timestamp=round(timestamp, 2),
            sender_id=sender,
            receiver_id=receiver,
            amount=amount,
            is_malicious=is_malicious,
        )
