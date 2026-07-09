# Nepal Compliance Ledger (NCL)

Agent-based simulation of a permissioned compliance ledger for supervising high-frequency financial flows in Nepal.

The project models a permissioned compliance environment where transactions are evaluated before settlement using:

- Sliding-window velocity detection for structuring or smurfing behavior
- Graph cycle detection for circular layering patterns
- Hash-chained immutable ledger entries for tamper-evident auditability
- Merkle-root block sealing with simulated 4-of-5 validator quorum
- Agent-based simulation with honest users, structurers, and ring traders

## Repository Contents

- `main.py` - simulation entry point
- `simulation.py` - orchestration, metrics, and reporting
- `agents.py` - agent pool and transaction generation
- `compliance_engine.py` - velocity and graph-cycle detection algorithms
- `ledger.py` - permissioned block ledger with Merkle roots and quorum verification
- `ncl.tex` - LaTeX source for the research manuscript
- `models.py` - data models and transaction status enums
- `config.py` - simulation and compliance parameters
- `architecture.png` - hub-and-spoke architecture figure used in the PDF
- `simulation_results.png` - generated 100k-run terminal-style result figure
- `ncl.pdf` - research manuscript snapshot

## Run

No external Python packages are required.

```bash
python main.py
```

## Current Reproducible Run

Using the checked-in configuration:

- Agents: 10,000
- Simulation duration: 3,600 seconds
- Transactions processed: 100,000
- True positives: 38,566
- False positives: 39
- False negatives: 6,601
- True negatives: 54,794
- Precision: 0.9990
- Recall: 0.8539
- F1 score: 0.9207
- Sealed blocks: 196
- Validator quorum: 4/5
- Ledger integrity: intact

## Method Note

The included PDF is generated from `ncl.tex` and reflects the current reproducible 100k-transaction implementation.
