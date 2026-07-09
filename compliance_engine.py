"""
NCL Compliance Engine
  Algorithm 1: Sliding Window Velocity Protocol  (Section 2.2)
  Algorithm 2: Graph Cycle Detection via DFS     (Section 2.3)
"""

from collections import defaultdict
from typing import Dict, List, Set

from models import Transaction, TxStatus


# ---------- Algorithm 1: Sliding Window (Eq. 2) ----------

class SlidingWindowDetector:
    """
    Count = Sum_i  I(T_now - t_i < W)
    Block if Count >= threshold.
    """

    def __init__(self, window_size: int, threshold: int):
        self.W = window_size
        self.threshold = threshold
        self._log: Dict[str, List[float]] = defaultdict(list)

    def check(self, sender_id: str, timestamp: float) -> bool:
        """Return True if the transaction should be BLOCKED."""
        cutoff = timestamp - self.W
        log = self._log[sender_id]
        # Prune entries outside the window
        self._log[sender_id] = [t for t in log if t > cutoff]
        count = len(self._log[sender_id])
        self._log[sender_id].append(timestamp)
        return count >= self.threshold


# ---------- Algorithm 2: DFS Cycle Detection (Algorithm 2) ----------

class GraphCycleDetector:
    """
    For edge (u, v): check if path v -> ... -> u exists with |P| <= k.
    """

    def __init__(self, max_depth: int):
        self.max_depth = max_depth
        self._adj: Dict[str, Set[str]] = defaultdict(set)

    def record_edge(self, sender: str, receiver: str):
        self._adj[sender].add(receiver)

    def would_create_cycle(self, sender: str, receiver: str) -> bool:
        """Return True if adding sender->receiver completes a cycle."""
        return self._dfs(origin=sender, current=receiver, depth=0)

    def _dfs(self, origin: str, current: str, depth: int) -> bool:
        if current == origin and depth > 0:
            return True                         # cycle found
        if depth >= self.max_depth:
            return False
        for neighbor in self._adj.get(current, set()):
            if self._dfs(origin, neighbor, depth + 1):
                return True
        return False


# ---------- Composite Engine ----------

class ComplianceEngine:

    def __init__(self, window_size: int, tx_threshold: int, max_cycle_depth: int):
        self.velocity = SlidingWindowDetector(window_size, tx_threshold)
        self.graph = GraphCycleDetector(max_cycle_depth)
        self.stats = {
            "velocity_blocks": 0,
            "cycle_blocks": 0,
            "approved": 0,
        }

    def validate(self, tx: Transaction) -> Transaction:
        # Check 1 — velocity
        if self.velocity.check(tx.sender_id, tx.timestamp):
            tx.status = TxStatus.BLOCKED_VELOCITY
            self.stats["velocity_blocks"] += 1
            return tx

        # Check 2 — cycle
        if self.graph.would_create_cycle(tx.sender_id, tx.receiver_id):
            tx.status = TxStatus.BLOCKED_CYCLE
            self.stats["cycle_blocks"] += 1
            return tx

        # Approved — record edge for future cycle detection
        self.graph.record_edge(tx.sender_id, tx.receiver_id)
        tx.status = TxStatus.APPROVED
        self.stats["approved"] += 1
        return tx
