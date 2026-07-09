"""
NCL compliance engine.

Algorithm 1: Sliding-window velocity detection.
Algorithm 2: bounded DFS cycle detection over a recent transaction graph.
"""

from collections import defaultdict, deque
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
        self._log: Dict[str, deque] = defaultdict(deque)

    def check(self, sender_id: str, timestamp: float) -> bool:
        """Return True if the transaction should be BLOCKED."""
        cutoff = timestamp - self.W
        log = self._log[sender_id]
        while log and log[0] <= cutoff:
            log.popleft()
        count = len(log)
        log.append(timestamp)
        return count >= self.threshold


# ---------- Algorithm 2: DFS Cycle Detection (Algorithm 2) ----------

class GraphCycleDetector:
    """
    For edge (u, v): check if path v -> ... -> u exists with |P| <= k.
    """

    def __init__(self, max_depth: int, memory_seconds: int):
        self.max_depth = max_depth
        self.memory_seconds = memory_seconds
        self._adj: Dict[str, Dict[str, float]] = defaultdict(dict)
        self._edges = deque()

    def record_edge(self, sender: str, receiver: str, timestamp: float):
        self._adj[sender][receiver] = timestamp
        self._edges.append((timestamp, sender, receiver))

    def would_create_cycle(self, sender: str, receiver: str, timestamp: float) -> bool:
        """Return True if adding sender->receiver completes a cycle."""
        self._prune(timestamp)
        return self._dfs(origin=sender, current=receiver, depth=0, visited=set())

    def _prune(self, timestamp: float):
        cutoff = timestamp - self.memory_seconds
        while self._edges and self._edges[0][0] <= cutoff:
            old_ts, sender, receiver = self._edges.popleft()
            if self._adj.get(sender, {}).get(receiver) == old_ts:
                del self._adj[sender][receiver]
                if not self._adj[sender]:
                    del self._adj[sender]

    def _dfs(self, origin: str, current: str, depth: int, visited: Set[str]) -> bool:
        if current == origin and depth > 0:
            return True                         # cycle found
        if depth >= self.max_depth:
            return False
        if current in visited:
            return False
        visited.add(current)
        for neighbor in self._adj.get(current, {}):
            if self._dfs(origin, neighbor, depth + 1, visited):
                return True
        return False


# ---------- Composite Engine ----------

class ComplianceEngine:

    def __init__(self, window_size: int, tx_threshold: int,
                 max_cycle_depth: int, graph_memory_seconds: int):
        self.velocity = SlidingWindowDetector(window_size, tx_threshold)
        self.graph = GraphCycleDetector(max_cycle_depth, graph_memory_seconds)
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
        if self.graph.would_create_cycle(tx.sender_id, tx.receiver_id, tx.timestamp):
            tx.status = TxStatus.BLOCKED_CYCLE
            self.stats["cycle_blocks"] += 1
            return tx

        # Approved — record edge for future cycle detection
        self.graph.record_edge(tx.sender_id, tx.receiver_id, tx.timestamp)
        tx.status = TxStatus.APPROVED
        self.stats["approved"] += 1
        return tx
