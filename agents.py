"""
NCL agent-based model.

Agent types:
  - Honest:      stochastic legitimate transactions
  - Structurers: high-frequency micro-transactions below reporting thresholds
  - Ring traders: circular layering in fixed groups of three
"""

import hashlib
from typing import List

from config import BANKS, HONEST_TX_AMOUNT, MALICIOUS_RATIO, MALICIOUS_TX_AMOUNT, NUM_AGENTS
from config import RING_TX_AMOUNT, SIMULATION_DURATION, STRUCTURER_RATIO
from config import HONEST_TX_SHARE, RING_TX_SHARE, STRUCTURING_TX_SHARE
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
        num_structurers = int(num_malicious * STRUCTURER_RATIO)

        for i in range(NUM_AGENTS):
            agent_type = AgentType.MALICIOUS if i < num_malicious else AgentType.HONEST
            attack_type = "benign"
            if agent_type == AgentType.MALICIOUS:
                attack_type = "structuring" if i < num_structurers else "ring"
            agent = Agent(
                id=f"AGENT-{i:04d}",
                agent_type=agent_type,
                bank=self.rng.choice(BANKS),
                attack_type=attack_type,
            )
            self.agents.append(agent)
            if agent_type == AgentType.MALICIOUS:
                self.malicious_ids.add(agent.id)

        self.rng.shuffle(self.agents)

    # ---- transaction generation ----

    def generate_transactions(self, target_transactions: int) -> List[Transaction]:
        txs: List[Transaction] = []
        honest = [a for a in self.agents if a.agent_type == AgentType.HONEST]
        structurers = [
            a for a in self.agents
            if a.agent_type == AgentType.MALICIOUS and a.attack_type == "structuring"
        ]
        ring_pool = [
            a for a in self.agents
            if a.agent_type == AgentType.MALICIOUS and a.attack_type == "ring"
        ]
        rings = [
            ring_pool[i:i + 3]
            for i in range(0, len(ring_pool) - 2, 3)
        ]
        ring_offsets = {idx: 0 for idx in range(len(rings))}

        weights = [
            ("honest", HONEST_TX_SHARE),
            ("structuring", STRUCTURING_TX_SHARE),
            ("ring", RING_TX_SHARE),
        ]
        total_weight = sum(weight for _, weight in weights)
        timestamp = 0.0

        for _ in range(target_transactions):
            timestamp += self.rng.expovariate(target_transactions / SIMULATION_DURATION)
            timestamp = min(timestamp, SIMULATION_DURATION)
            draw = self.rng.random() * total_weight
            if draw < weights[0][1]:
                txs.append(self._honest_tx(honest, timestamp))
            elif draw < weights[0][1] + weights[1][1]:
                txs.append(self._structuring_tx(structurers, timestamp))
            else:
                txs.append(self._ring_tx(rings, ring_offsets, timestamp))

        return txs

    # ---- helpers ----

    def _honest_tx(self, honest: List[Agent], timestamp: float) -> Transaction:
        sender = self.rng.choice(honest)
        receiver = self._pick_receiver(sender.id)
        amount = round(self.rng.uniform(*HONEST_TX_AMOUNT), 2)
        return self._make_tx(sender.id, receiver, amount, timestamp, False, "benign")

    def _structuring_tx(self, structurers: List[Agent], timestamp: float) -> Transaction:
        sender = self.rng.choice(structurers)
        receiver = self._pick_receiver(sender.id)
        amount = round(self.rng.uniform(*MALICIOUS_TX_AMOUNT), 2)
        return self._make_tx(sender.id, receiver, amount, timestamp, True, "structuring")

    def _ring_tx(self, rings: List[List[Agent]], ring_offsets: dict, timestamp: float) -> Transaction:
        ring_idx = self.rng.randrange(len(rings))
        ring = rings[ring_idx]
        offset = ring_offsets[ring_idx]
        sender = ring[offset % 3]
        receiver = ring[(offset + 1) % 3]
        ring_offsets[ring_idx] = offset + 1
        amount = round(self.rng.uniform(*RING_TX_AMOUNT), 2)
        return self._make_tx(sender.id, receiver.id, amount, timestamp, True, "ring")

    def _pick_receiver(self, sender_id: str) -> str:
        while True:
            agent = self.rng.choice(self.agents)
            if agent.id != sender_id:
                return agent.id

    @staticmethod
    def _make_tx(sender: str, receiver: str, amount: float,
                 timestamp: float, is_malicious: bool, attack_type: str) -> Transaction:
        raw = f"{sender}:{receiver}:{amount}:{timestamp}"
        tx_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return Transaction(
            tx_hash=tx_hash,
            timestamp=round(timestamp, 2),
            sender_id=sender,
            receiver_id=receiver,
            amount=amount,
            is_malicious=is_malicious,
            attack_type=attack_type,
        )
