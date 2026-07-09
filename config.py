"""
Nepal Compliance Ledger (NCL) configuration.

The checked-in defaults run a deterministic 100k-transaction simulation that is
large enough to stress the detection and ledger paths while still being quick on
a laptop.
"""

# --- Simulation Parameters ---
NUM_AGENTS = 10_000
TARGET_TRANSACTIONS = 100_000
MALICIOUS_RATIO = 0.05
SIMULATION_DURATION = 3_600
RANDOM_SEED = 42

# --- Compliance Thresholds ---
SLIDING_WINDOW_SIZE = 300
TX_COUNT_THRESHOLD = 5
MAX_CYCLE_DEPTH = 3
GRAPH_MEMORY_SECONDS = 900

# --- Permissioned Blockchain Parameters ---
BLOCK_SIZE = 512
POLICY_VERSION = "NCL-POLICY-2026.02"
VALIDATOR_QUORUM = 4
VALIDATORS = [
    "NRB-Regulator",
    "Nabil-Bank-Node",
    "Global-IME-Node",
    "NIC-Asia-Node",
    "Sanima-Node",
]

# --- Banking Environment ---
BANKS = [
    "Nabil Bank",
    "Global IME Bank",
    "NIC Asia Bank",
    "Sanima Bank",
    "Machhapuchchhre Bank",
    "Nepal SBI Bank",
    "Everest Bank",
]

# --- Transaction Mix ---
HONEST_TX_SHARE = 0.55
STRUCTURING_TX_SHARE = 0.30
RING_TX_SHARE = 0.15

# --- Agent Behavior ---
HONEST_TX_AMOUNT = (5_000, 500_000)
MALICIOUS_TX_AMOUNT = (500, 9_500)
RING_TX_AMOUNT = (10_000, 50_000)

# --- Malicious Agent Distribution ---
STRUCTURER_RATIO = 0.70
