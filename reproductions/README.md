# Reproductions (GPU PC 2)

Reproduce the comparator papers **one by one**, then compare them with TEMARL under Idea 01, 02 and 03.
GPU PC 1 keeps running our own studies (CasinoLimit) at the same time.

## The standard

Every reproduction must meet [STANDARD.md](STANDARD.md): ten requirements at the level a Q1 journal
expects of a reproducibility study. In short:

1. **Targets first.** The paper's numbers are written into `TARGETS.csv` and committed before any
   result exists. `audit.py` proves the order from the git history and fails the reproduction if a
   target was added or changed afterwards.
2. **Gaps decided first**, in writing, and **the authors are asked** about each one.
3. **Every number is reported**, with a fixed verdict: MATCH, CLOSE, NO MATCH or NOT ATTEMPTED.
   A failed reproduction is reported as failed.
4. **Variance:** deterministic methods must give identical outputs on two machines; stochastic
   methods need at least 10 training seeds and a 95% CI.
5. **The right word:** *reproduced* = with the authors' own code or data; *replicated* = rebuilt
   from the paper (ACM terms). A method enters an Idea 01/02/03 comparison only after this.

Each paper gets `reproductions/<paper>/`, started from `TEMPLATE/`. Check all of them with
`python reproductions/audit.py` (writes `AUDIT.txt`).

Kuwano (`kuwano_repro/`) was done before this standard was written. It will be checked against it,
and any gap listed, before it enters a comparison.

## Two GPU PCs at the same time

| | GPU PC 1 | GPU PC 2 |
|---|---|---|
| runs | `casinolimit_encoder/` and later MAPPO | `reproductions/` only |
| writes | `casinolimit_encoder/out/` | `reproductions/<paper>/out/` |

Each PC only writes its own folders, so the two never conflict. Always pull before pushing:
`git pull --no-rebase` (merge, never rebase: rebasing would break the frozen-file hashes' history).
`COADAM_repro/` belongs to teammate Tushit Roy: do not edit it without them.

## The papers (from the finalised comparator list)

| # | paper | can we reproduce it? | what it needs | GPU? | feeds |
|---|---|---|---|---|---|
| 1 | **Kuwano et al. 2023**, J. Inf. Process. | **DONE** 2026-11-02: Prediction/TP/FP/FN 48/48 rows, TN 44/48 (`kuwano_repro/`) | nothing; optional re-run on PC 2 (seconds) | no | Idea 01: sealed predictions ready (`idea01_kuwano/`) |
| 2 | **Shell Attack Evolution**, SRDS 2025 | **YES**: data CC BY 4.0, pipeline MIT, already downloaded once | Python only | no | Idea 02: our model on their real-attacker sessions. Open check first: can per-command labels be re-derived (Q3)? |
| 3 | **Yu et al. 2022**, attention seq2seq (10.1155/2022/6012232) | **UNKNOWN**: the paper describes public ATT&CK sequence data and a generator; code not yet checked | the PDF; their data/tool | **yes** | Idea 01 (only with a target-format change, so stated as adapted) / Idea 02 separate test |
| 4 | **Lin et al. 2026**, IEEE TMLCN (tabular Q-learning) | **REIMPLEMENT**: Algorithm 1 and all hyperparameters published; no code | Conpot as a native Python install (PC 2 has no Docker, decided 2026-11-12); attack scripts by email (D. Sudyana). If Conpot will not install natively on Windows: NOT ATTEMPTED, reason stated | no | Idea 03: closest purpose match (engagement, depth) |
| 5 | **Co-ADAM**, Sci Rep 2026 | harness exists (`COADAM_repro/`, Tushit), never executed; our audit found the paper's tables built from one frozen policy | MATLAB R2025b + Statistics toolbox | no | Idea 03: zones + per-step attacker |
| 6 | **HoneyGPT**, Comput. Netw. 2026 | **PARTIAL**: their tables can be recomputed from released CSVs; the live LLM honeypot cannot be rerun as published | Python; (LLM API only for a live rerun, not planned) | no | citation for #2's data; fails all three ideas |
| 7 | **HoneyFactory 2024**, Electronics | **REIMPLEMENT ONLY** (HMM over traffic stages; container honeynet, no package) | the PDF (MDPI blocks automatic download) | no | Idea 03 after rebuilding |
| 8 | **DeepOP 2025**, Electronics | **UNKNOWN**: data release unknown | the PDF; author reply | yes, if possible | Idea 01 |
| 9 | **ASD-TGXAI 2026**, Ain Shams Eng. J. | **NO** with the materials found: no runnable package, no ordered per-step ATT&CK labels | — | — | closed unless the PDF shows code |
| 10 | **Q-Cowrie 2026**, Int. J. Inf. Secur. | **BLOCKED**: 400,000 sessions available by email only | author reply | no | Idea 03 / 02 if data arrives |

**PC 2 (2026-11-12):** RTX 4080 SUPER 16 GB, PyTorch 2.6 + CUDA, no Docker, no MATLAB.

**Order on PC 2** (ready first): 2 → 3 → 6 → 4 (native Conpot attempt) → 7, 8. Co-ADAM (5) stays with Tushit: PC 2 has no MATLAB
when their PDFs are in `PDF/`. 9 and 10 stay closed or blocked until something new arrives.

## Start PC 2

```powershell
git clone https://github.com/roy601/TEMARL.git; cd TEMARL; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install numpy==2.4.6 scipy==1.17.1; pip install torch --index-url https://download.pytorch.org/whl/cu124; python reproductions/pc2_check.py; git add reproductions/out; git commit -m "PC2 environment"; git pull --no-rebase; git push origin main
```

`pc2_check.py` only reads: it reports Python, PyTorch + CUDA (with a short GPU test), Docker, MATLAB,
disk and RAM, and which papers this PC can run.
