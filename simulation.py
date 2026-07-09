"""
NCL simulation engine.
"""

import json
import random
import time
from pathlib import Path

from config import (
    BLOCK_SIZE,
    GRAPH_MEMORY_SECONDS,
    MALICIOUS_RATIO,
    MAX_CYCLE_DEPTH,
    NUM_AGENTS,
    POLICY_VERSION,
    RANDOM_SEED,
    SIMULATION_DURATION,
    SLIDING_WINDOW_SIZE,
    TARGET_TRANSACTIONS,
    TX_COUNT_THRESHOLD,
    VALIDATOR_QUORUM,
    VALIDATORS,
)
from models import TxStatus
from agents import AgentPool
from compliance_engine import ComplianceEngine
from ledger import PermissionedBlockchainLedger


RESULTS_DIR = Path(__file__).resolve().parent / "results"


class NCLSimulation:

    def __init__(self):
        self.rng = random.Random(RANDOM_SEED)
        self.pool = AgentPool(self.rng)
        self.engine = ComplianceEngine(
            SLIDING_WINDOW_SIZE,
            TX_COUNT_THRESHOLD,
            MAX_CYCLE_DEPTH,
            GRAPH_MEMORY_SECONDS,
        )
        self.ledger = PermissionedBlockchainLedger()
        self.results = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}
        self.summary = {}

    def run(self):
        self._print_header()

        t0 = time.perf_counter()
        transactions = self.pool.generate_transactions(TARGET_TRANSACTIONS)
        gen_time = time.perf_counter() - t0

        print(f">>> GENERATED {len(transactions)} TRANSACTIONS  ({gen_time:.2f}s)")
        print(">>> PROCESSING TRANSACTIONS THROUGH COMPLIANCE + BLOCK LEDGER...")
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

            self.ledger.commit(tx)
            if tx.status != TxStatus.APPROVED and len(flagged_samples) < 5:
                flagged_samples.append(tx)

        self.ledger.finalize()
        proc_time = time.perf_counter() - t0

        self._print_flagged_samples(flagged_samples)
        self.summary = self._build_summary(len(transactions), gen_time, proc_time)
        self._print_results()
        self._write_results()

    # ---- output formatting ----

    def _print_header(self):
        print()
        print("=" * 56)
        print("    NEPAL COMPLIANCE LEDGER (NCL) - PROTOTYPE v2.0")
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
        print(f"    Target Txns:      {TARGET_TRANSACTIONS}")
        print(f"    Block Size:       {BLOCK_SIZE}")
        print(f"    Validator Quorum: {VALIDATOR_QUORUM}/{len(VALIDATORS)}")
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

    def _build_summary(self, total_tx, gen_time, proc_time):
        tp = self.results["TP"]
        fp = self.results["FP"]
        fn = self.results["FN"]
        tn = self.results["TN"]

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = (2 * precision * recall / (precision + recall)
              if (precision + recall) > 0 else 0)
        throughput = total_tx / proc_time if proc_time else 0
        intact = self.ledger.verify_integrity()
        return {
            "agents": NUM_AGENTS,
            "target_transactions": TARGET_TRANSACTIONS,
            "total_transactions": total_tx,
            "simulation_duration_seconds": SIMULATION_DURATION,
            "generation_time_seconds": round(gen_time, 4),
            "processing_time_seconds": round(proc_time, 4),
            "throughput_tx_per_second": round(throughput, 2),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "velocity_flags": self.engine.stats["velocity_blocks"],
            "cycle_flags": self.engine.stats["cycle_blocks"],
            "approved": self.engine.stats["approved"],
            "blocks": self.ledger.size,
            "block_size": BLOCK_SIZE,
            "validator_quorum": VALIDATOR_QUORUM,
            "validator_count": len(VALIDATORS),
            "policy_version": POLICY_VERSION,
            "last_block_hash": self.ledger.last_block_hash,
            "chain_integrity": intact,
        }

    def _print_results(self):
        s = self.summary
        print("=" * 56)
        print(f"    AGENT-BASED SIMULATION RESULTS (N={NUM_AGENTS})")
        print("=" * 56)
        print(f"  Total Transactions Processed: {s['total_transactions']}")
        print("-" * 56)
        print("  [CONFUSION MATRIX]")
        print(f"   > True Positives  (Blocked Criminals):  {s['true_positives']}")
        print(f"   > False Positives (Blocked Honest):     {s['false_positives']}")
        print(f"   > False Negatives (Missed Criminals):   {s['false_negatives']}")
        print(f"   > True Negatives  (Allowed Honest):     {s['true_negatives']}")
        print("-" * 56)
        print("  [PERFORMANCE METRICS]")
        print(f"   > Precision: {s['precision']:.4f}")
        print(f"   > Recall:    {s['recall']:.4f}")
        print(f"   > F1 Score:  {s['f1_score']:.4f}")
        print(f"   > Throughput:{s['throughput_tx_per_second']:,.2f} tx/s")
        print("-" * 56)
        print("  [DETECTION BREAKDOWN]")
        print(f"   > Velocity Flags: {s['velocity_flags']}")
        print(f"   > Cycle Flags:    {s['cycle_flags']}")
        print(f"   > Approved:       {s['approved']}")
        print("-" * 56)
        print("  [PERMISSIONED LEDGER]")
        print(f"   > Committed Blocks: {s['blocks']}")
        print(f"   > Block Size:       {s['block_size']}")
        print(f"   > Validator Quorum: {s['validator_quorum']}/{s['validator_count']}")
        print(f"   > Last Block Hash:  {s['last_block_hash'][:24]}...")
        status = "INTACT" if s["chain_integrity"] else "COMPROMISED"
        print(f"   > Chain Integrity:  {status}")
        print(f"   > Processing Time:  {s['processing_time_seconds']:.3f}s")
        print("=" * 56)
        print()

    def _write_results(self):
        RESULTS_DIR.mkdir(exist_ok=True)
        json_path = RESULTS_DIR / "ncl_run_summary.json"
        txt_path = RESULTS_DIR / "ncl_run_summary.txt"
        json_path.write_text(json.dumps(self.summary, indent=2), encoding="utf-8")
        lines = [
            "Nepal Compliance Ledger - Reproducible Run Summary",
            f"Transactions: {self.summary['total_transactions']}",
            f"Precision: {self.summary['precision']:.4f}",
            f"Recall: {self.summary['recall']:.4f}",
            f"F1 Score: {self.summary['f1_score']:.4f}",
            f"Throughput: {self.summary['throughput_tx_per_second']:,.2f} tx/s",
            f"Blocks: {self.summary['blocks']}",
            f"Chain Integrity: {self.summary['chain_integrity']}",
        ]
        txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
