"""
Nepal Compliance Ledger (NCL) - Configuration
Algorithmic Supervision of High-Frequency Financial Flows
"""

# --- Simulation Parameters ---
NUM_AGENTS = 1000
MALICIOUS_RATIO = 0.05              # 5% malicious agents
SIMULATION_DURATION = 3600          # 1 hour in seconds
RANDOM_SEED = 42

# --- Compliance Thresholds ---
SLIDING_WINDOW_SIZE = 300           # W = 300 seconds (Eq. 2)
TX_COUNT_THRESHOLD = 5              # Max transactions in window before flagging
MAX_CYCLE_DEPTH = 3                 # k = 3 hops for cycle detection (Eq. 3)

# --- Banking Environment ---
BANKS = [
    "Nabil Bank",
    "Global IME Bank",
    "NIC Asia Bank",
    "Sanima Bank",
    "Machhapuchchhre Bank",
]

# --- Agent Behavior ---
HONEST_TX_INTERVAL = (600, 1400)    # Seconds between honest transactions
HONEST_TX_AMOUNT = (5000, 500000)   # NPR range for honest transactions

MALICIOUS_TX_INTERVAL = (15, 55)    # Seconds between structuring transactions
MALICIOUS_TX_AMOUNT = (500, 9500)   # NPR (below reporting threshold)

RING_TX_INTERVAL = (10, 40)         # Seconds between layering transactions
RING_TX_AMOUNT = (10000, 50000)     # NPR range for layering

# --- Malicious Agent Distribution ---
STRUCTURER_RATIO = 0.70             # 70% structurers, 30% form trading rings
