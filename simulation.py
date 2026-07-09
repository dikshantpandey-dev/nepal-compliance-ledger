"""
NCL Simulation Engine — orchestrates the Agent-Based Model.
"""

import random
import time

from config import (
    MALICIOUS_RATIO,
    MAX_CYCLE_DEPTH,
    NUM_AGENTS,
    RANDOM_SEED,
    SIMULATION_DURATION,
    SLIDING_WINDOW_SIZE,
    TX_COUNT_THRESHOLD,
)
from models import TxStatus
from agents import AgentPool
from compliance_engine import ComplianceEngine
from ledger import ImmutableLedger


class NCLSimulation:

    def __init__(self):
        self.rng = random.Random(RANDOM_SEED)
        self.pool = AgentPool(self.rng)
        self.engine = ComplianceEngine(
            SLIDING_WINDOW_SIZE, TX_COUNT_THRESHOLD, MAX_CYCLE_DEPTH
        )
        self.ledger = ImmutableLedger()
        self.results = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}

    def run(self):
        self._print_header()

        t0 = time.perf_counter()
        transactions = self.pool.generate_transactions()
        gen_time = time.perf_counter() - t0

        print(f">>> GENERATED {len(transactions)} TRANSACTIONS  ({gen_time:.2f}s)")
        print(">>> PROCESSING TRANSACTIONS...")
        print()

        t0 = time.perf_counter()
        flagged_samples = []

        for tx in transactions:
            self.engine.validate(tx)

            blocked = tx.status != TxStatus.APPROVED
            malicious = tx.is_malicious

            if blocked and malicious:
                self.results["TP"] += 1
            elif blocked and not malicious:
                self.results["FP"] += 1
            elif not blocked and malicious:
                self.results["FN"] += 1
            else:
                self.results["TN"] += 1

            if tx.status == TxStatus.APPROVED:
                self.ledger.commit(tx)
            elif len(flagged_samples) < 5:
                flagged_samples.append(tx)

        proc_time = time.perf_counter() - t0

        self._print_flagged_samples(flagged_samples)
        self._print_results(len(transactions), proc_time)

    # ---- output formatting ----

    def _print_header(self):
        print()
        print("=" * 56)
        print("    NEPAL COMPLIANCE LEDGER (NCL) - PROTOTYPE v1.0")
        print("=" * 56)
        print()
        honest_n = int(NUM_AGENTS * (1 - MALICIOUS_RATIO))
        mal_n = int(NUM_AGENTS * MALICIOUS_RATIO)
        print(f"--- INITIALIZING AGENT-BASED MODEL ({NUM_AGENTS} AGENTS) ---")
        print(f"    Honest Agents:    {honest_n}")
        print(f"    Malicious Agents: {mal_n}")
        print(f"    Window Size (W):  {SLIDING_WINDOW_SIZE}s")
        print(f"    Tx Threshold:     {TX_COUNT_THRESHOLD}")
        print(f"    Cycle Depth (k):  {MAX_CYCLE_DEPTH}")
        print(f"    Sim Duration:     {SIMULATION_DURATION}s")
        print()

    def _print_flagged_samples(self, samples):
        if not samples:
            return
        print("-" * 56)
        print("  [SAMPLE FLAGGED TRANSACTIONS]")
        for tx in samples:
            print(
                f"   {tx.tx_hash}  {tx.sender_id} -> {tx.receiver_id}"
                f"  NPR {tx.amount:>10,.2f}  [{tx.status.value}]"
            )
        print()

    def _print_results(self, total_tx, proc_time):
        tp = self.results["TP"]
        fp = self.results["FP"]
        fn = self.results["FN"]
        tn = self.results["TN"]

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = (2 * precision * recall / (precision + recall)
              if (precision + recall) > 0 else 0)

        print("=" * 56)
        print(f"    AGENT-BASED SIMULATION RESULTS (N={NUM_AGENTS})")
        print("=" * 56)
        print(f"  Total Transactions Processed: {total_tx}")
        print("-" * 56)
        print("  [CONFUSION MATRIX]")
        print(f"   > True Positives  (Blocked Criminals):  {tp}")
        print(f"   > False Positives (Blocked Honest):     {fp}")
        print(f"   > False Negatives (Missed Criminals):   {fn}")
        print(f"   > True Negatives  (Allowed Honest):     {tn}")
        print("-" * 56)
        print("  [PERFORMANCE METRICS]")
        print(f"   > Precision: {precision:.4f}")
        print(f"   > Recall:    {recall:.4f}")
        print(f"   > F1 Score:  {f1:.4f}")
        print("-" * 56)
        print("  [DETECTION BREAKDOWN]")
        print(f"   > Velocity Flags: {self.engine.stats['velocity_blocks']}")
        print(f"   > Cycle Flags:    {self.engine.stats['cycle_blocks']}")
        print(f"   > Approved:       {self.engine.stats['approved']}")
        print("-" * 56)
        print("  [LEDGER INTEGRITY]")
        print(f"   > Committed Blocks: {self.ledger.size}")
        intact = self.ledger.verify_integrity()
        status = "INTACT" if intact else "COMPROMISED"
        print(f"   > Chain Integrity:  {status}")
        print(f"   > Processing Time:  {proc_time:.3f}s")
        print("=" * 56)
        print()
