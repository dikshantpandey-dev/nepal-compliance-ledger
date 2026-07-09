# Nepal Compliance Ledger (NCL)

Agent-based simulation of a compliance ledger for supervising high-frequency financial flows in Nepal.

The project models a permissioned compliance environment where transactions are evaluated before settlement using:

- Sliding-window velocity detection for structuring or smurfing behavior
- Graph cycle detection for circular layering patterns
- Hash-chained immutable ledger entries for tamper-evident auditability
- Agent-based simulation with honest users, structurers, and ring traders

## Repository Contents

- `main.py` - simulation entry point
- `simulation.py` - orchestration, metrics, and reporting
- `agents.py` - agent pool and transaction generation
- `compliance_engine.py` - velocity and graph-cycle detection algorithms
- `ledger.py` - hash-chained append-only ledger
- `models.py` - data models and transaction status enums
- `config.py` - simulation and compliance parameters
- `ncl.pdf` - research manuscript snapshot

## Run

No external Python packages are required.

```bash
python main.py
```

## Current Reproducible Run

Using the checked-in configuration:

- Agents: 1,000
- Simulation duration: 3,600 seconds
- Transactions processed: 9,639
- True positives: 5,515
- False positives: 103
- False negatives: 225
- True negatives: 3,796
- Precision: 0.9817
- Recall: 0.9608
- F1 score: 0.9711
- Ledger integrity: intact

## Method Note

The included PDF is a manuscript snapshot. The code in this repository is the reproducible implementation state; if metrics differ from the PDF, prefer rerunning `python main.py` and reporting the current reproducible output.
