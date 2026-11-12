# The standard every reproduction here must meet

Written 2026-11-12, before the first reproduction on GPU PC 2. `audit.py` checks the mechanical
parts automatically; the rest is a checklist in each paper's `REPORT.md`.

## 1. Say exactly what kind of result it is (ACM Artifact Review and Badging v1.1)

| term | meaning | our papers |
|---|---|---|
| **Reproduced** | a different team, using the authors' own artifacts (their code or data) | Shell Attack Evolution, HoneyGPT tables, Co-ADAM |
| **Replicated** | a different team, with independently built artifacts (rebuilt from the paper) | Kuwano (done), Lin et al. (TMLCN), Yu et al., HoneyFactory |
| **Not reproducible** | the materials needed do not exist or were not provided | stated with the missing item named, and the request we sent |

Never write "reproduced" for a rebuild, and never write either word for a partial match.

## 2. The ten requirements

1. **Targets first.** Every published number we try to match is in `TARGETS.csv`, with its table or
   figure and a tolerance, committed **before** any result. Git history proves the order; `audit.py`
   fails the reproduction if a target was added or changed after the first result was committed.
2. **Gaps decided first.** Where the paper is silent, `DECISIONS.md` records the choice and the
   reason before the run. No search over settings to make numbers match. A decision made after a run
   is dated, marked "after results", and its effect on every target is reported.
3. **Authors asked.** Every gap is sent to the authors. `AUTHOR_CONTACT.md` logs date, question and
   reply (or "no reply after N days"). A paper is called "not reproducible" only after this.
4. **Exact sources.** `SOURCES.md`: paper version read, code URL and commit, data DOI and checksum,
   licence. Licences are followed and the originals cited.
5. **Variance.** Deterministic method: run on two machines, outputs byte-identical (SHA-256).
   Stochastic method: at least 10 independent training seeds, mean and 95% CI. The verdict uses the
   CI, not the best seed.
6. **Every number reported.** `REPORT.md` lists every target with the published value, ours, the
   difference and a verdict. Failures stay in the report.
7. **Environment recorded.** Hardware, OS, library versions and the repository commit are written
   by the run itself (`out/ENVIRONMENT.json`).
8. **One command, from public inputs.** `run.py` rebuilds everything from the public sources and
   writes only to `out/`. Raw outputs are saved with their SHA-256.
9. **Tested.** Rebuilt code has unit tests for each rule taken from the paper.
10. **Then, a fair comparison.** A method enters an Idea 01/02/03 comparison only after its own
    paper's numbers were checked (requirement 6). In the comparison: the published hyperparameters
    are used; if something must be tuned on our data, it gets the same validation-only budget as our
    model; every adaptation is declared; both sides use the same splits and the same metric code;
    and the comparison protocol is frozen before any test score (as protocols 1.2 and CL 1.0).

## 3. Verdicts (fixed wording)

| per target | rule |
|---|---|
| **MATCH** | inside the tolerance written in `TARGETS.csv` |
| **CLOSE** | outside the tolerance, inside twice the tolerance (or, for a stochastic method, the published value is inside our 95% CI) |
| **NO MATCH** | anything else |
| **NOT ATTEMPTED** | with the reason (for example: needs the physical testbed) |

Per paper: "reproduced / replicated" needs every primary target MATCH; "partially" names the
targets that are not; "not" is said plainly. Primary targets are marked in `TARGETS.csv` before
the run.

## 4. What this standard cannot do

It makes each reproduction honest, checkable and at the level reviewers of a Q1 journal expect of a
reproducibility study. It cannot make a paper reproducible if its materials are missing, and it
cannot promise acceptance. A documented "not reproducible, here is what is missing and what we
asked" is a valid, reportable result.

## References

- ACM, *Artifact Review and Badging*, Version 1.1 (2020): https://www.acm.org/publications/policies/artifact-review-and-badging-current
- Pineau et al., "Improving Reproducibility in Machine Learning Research (A Report from the NeurIPS
  2019 Reproducibility Program)", *JMLR* 22(164):1–20, 2021: https://jmlr.org/papers/v22/20-303.html
