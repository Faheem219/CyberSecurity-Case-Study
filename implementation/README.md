# NHI lab — scoped delegation, identity-aware IDS and forensic logging

A small, purely defensive simulation for the Group 04 Cyber Security CA-2 case study.
All events are synthetic and tool names are abstract labels; nothing is executed against any system.

```
python3 run_experiment.py --runs 50   # 50 seeds × {baseline shared key, NHI + scoped delegation} → results/
python3 make_figures.py               # charts and architecture diagram → figures/
```

| File | What it does |
|---|---|
| `nhi_lab/identity.py` | Agent/human identities; HMAC-SHA256 delegation tokens that can only narrow; shared-key baseline |
| `nhi_lab/gateway.py` | Single enforcement point for every tool call; writes each decision to the audit log |
| `nhi_lab/audit.py` | SHA-256 hash-chained audit log with `verify()` and `timeline()` |
| `nhi_lab/ids.py` | Identity-aware rules: R1 tempo, R2 probing, R3 multi-tactic chain per delegation grant |
| `nhi_lab/workload.py` | Synthetic benign agents and an abstract misuse delegation tree |
| `run_experiment.py` | Runs the comparison, scores alerts against ground-truth labels, tamper test, overhead benchmark |
| `make_figures.py` | Blue/black charts used in the report and slides |

Requirements: Python 3.9+, matplotlib.
