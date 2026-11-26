#!/usr/bin/env python3
"""Controlled preflight and simulation harness for the author-released Foureye-2 code.

No experiment in this program is fabricated. The original repo is NOT distributed
with this kit; provide it as --source. All compatibility changes are applied to a COPY.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import random
import shutil
import subprocess
import sys
import time
import traceback

GITHUB_URL = "https://github.com/Wan-ZL/Foureye-2-simulation"
SOURCE_FILES = (
    "main.py", "game_function.py", "graph_function.py", "attacker_function.py",
    "defender_function.py", "ML_train_strat_sep.py", "ML_training.py", "README.md",
)
# decision_scheme: 0 random, 1 hypergame utility, 2 ML
SCHEMES = {
    "DD-Random": (True, True, True, 0),
    "No-DD-Random": (False, True, True, 0),
    "DD-IPI": (True, True, True, 1),
    "DD-ML-IPI": (True, True, True, 2),
    "No-DD-IPI": (False, True, True, 1),
    "DD-PI": (True, False, False, 1),
    "DD-ML-PI": (True, False, False, 2),
    "No-DD-PI": (False, False, False, 1),
}
AAPS = (0.05, 0.1, 0.2, 0.3, 0.4, 0.5)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(2**20), b""):
            h.update(block)
    return h.hexdigest()


def source_revision(directory: Path) -> str | None:
    p = subprocess.run(["git", "-C", str(directory), "rev-parse", "HEAD"],
                       capture_output=True, text=True, check=False)
    return p.stdout.strip() if p.returncode == 0 else None


def json_dump(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def get_version(modname: str) -> str | None:
    try:
        m = importlib.import_module(modname)
        return getattr(m, "__version__", "installed")
    except Exception:
        return None


def required_models(directory: Path, scheme: str, variation: str = "fixed") -> list[Path]:
    if not scheme.startswith("DD-ML-"):
        return []
    who = "IPI" if scheme.endswith("IPI") else "PI"
    basename = f"trained_classi_model_ML_collect_data_{who}.pkl"
    if variation == "aap":
        return [directory / "data_vary" / f"AAP={aap}" / "trained_ML_model" / basename
                for aap in AAPS]
    return [directory / "data" / "trained_ML_model" / basename]


def preflight(source: Path) -> dict:
    source = source.resolve()
    files = {p: {"present": (source / p).is_file(),
                 "sha256": sha256_file(source / p) if (source / p).is_file() else None}
             for p in SOURCE_FILES}
    main_txt = (source / "main.py").read_text(encoding="utf-8", errors="replace") if (source / "main.py").exists() else ""
    graph_txt = (source / "graph_function.py").read_text(encoding="utf-8", errors="replace") if (source / "graph_function.py").exists() else ""
    game_txt = (source / "game_function.py").read_text(encoding="utf-8", errors="replace") if (source / "game_function.py").exists() else ""
    models = {scheme: [str(p.relative_to(source)) for p in required_models(source, scheme)]
              for scheme in ("DD-ML-IPI", "DD-ML-PI")}
    missing = {s: [v for v in p if not (source / v).is_file()] for s, p in models.items()}
    issues = []
    if not all(x["present"] for x in files.values()):
        issues.append("Some core author files are missing")
    if "from networkx import nx" in graph_txt + game_txt:
        issues.append("Legacy 'from networkx import nx' requires a compatibility patch in modern NetworkX")
    if "from game_function import *" in main_txt and "from main import display" in graph_txt:
        issues.append("Circular display import; prepare command safely initializes display first")
    if any(missing.values()):
        issues.append("Original ML models missing for ML-assisted published baselines")
    if not (source / "requirements.txt").is_file():
        issues.append("No pinned requirements.txt; version equivalence to published Python 3.6/sklearn 0.19.1 not established")
    return {
        "original_repository": GITHUB_URL, "source_path": str(source),
        "source_revision": source_revision(source), "original_files": files,
        "model_file_expectations": models, "missing_models": missing,
        "available_environment": {"python": platform.python_version(),
                                  "networkx": get_version("networkx"),
                                  "numpy": get_version("numpy"),
                                  "sklearn": get_version("sklearn"),
                                  "matplotlib": get_version("matplotlib")},
        "issues": issues,
        "reproduction_ready": (not issues),
        "note": "Readiness here is a conservative preflight, not proof of published-table reproduction"
    }


def prepare(source: Path, destination: Path) -> dict:
    source, destination = source.resolve(), destination.resolve()
    if not source.is_dir():
        raise FileNotFoundError(f"Original source does not exist: {source}")
    if source == destination or source in destination.parents:
        raise ValueError("Destination must not be inside the original source tree")
    if destination.exists():
        raise FileExistsError(f"Destination already exists; choose a new path: {destination}")
    for filename in SOURCE_FILES[:5]:
        if not (source / filename).is_file():
            raise FileNotFoundError(f"Required original source file missing: {filename}")
    shutil.copytree(source, destination)
    fixes = []
    for name in ("graph_function.py", "game_function.py"):
        p = destination / name
        txt = p.read_text(encoding="utf-8")
        patched = txt.replace("from networkx import nx", "import networkx as nx")
        if patched != txt:
            p.write_text(patched, encoding="utf-8")
            fixes.append({"file": name, "change": "from networkx import nx -> import networkx as nx",
                          "old_sha256": sha256_file(source / name), "new_sha256": sha256_file(p)})
    main = destination / "main.py"
    text = main.read_text(encoding="utf-8")
    if "from game_function import *" in text:
        # Minimal import-order repair; does not alter simulation functions or parameters.
        patched = text.replace("from game_function import *",
                               "display = False  # compatibility: defined before cyclic import\nfrom game_function import *", 1)
        if patched != text:
            main.write_text(patched, encoding="utf-8")
            fixes.append({"file": "main.py", "change": "Initialize display before game_function import",
                          "old_sha256": sha256_file(source / "main.py"), "new_sha256": sha256_file(main)})
    record = {"source": str(source), "destination": str(destination),
              "original_revision": source_revision(source), "fixes": fixes,
              "not_reproduced": True, "warning": "Compatibility port, not the unmodified historical runtime"}
    json_dump(destination / "COMPATIBILITY_PATCHES.json", record)
    return record


def float_array(values) -> list[float]:
    """Flatten nested/ragged histories without fabricating missing values."""
    import numpy as np
    flat = []
    def visit(v):
        if v is None:
            return
        if isinstance(v, (list, tuple, np.ndarray)):
            for item in v:
                visit(item)
        else:
            try:
                x = float(v)
            except (TypeError, ValueError):
                return
            if np.isfinite(x):
                flat.append(x)
    visit(values)
    return flat


def handle_worker(a: argparse.Namespace) -> None:
    # Only invoked in an isolated subprocess.
    source = Path(a.source).resolve()
    os.chdir(source)
    sys.path.insert(0, str(source))
    import contextlib
    import numpy as np
    import random
    random.seed(a.seed)
    np.random.seed(a.seed)
    model_args = SCHEMES[a.scheme]
    with Path(a.trace).open("w", encoding="utf-8") as f, contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
        import main
        kwargs = {"simulation_id": a.seed, "DD_using": model_args[0],
                  "uncertain_scheme_att": model_args[1], "uncertain_scheme_def": model_args[2],
                  "decision_scheme": model_args[3], "scheme_name": a.scheme}
        if a.aap is not None:
            kwargs.update(att_arr_prob=a.aap, vary_name="AAP", vary_value=a.aap)
        model = main.game_start(**kwargs)
    result = {"scheme": a.scheme, "seed": a.seed, "aap": a.aap,
              "lifetime": int(model.lifetime),
              "TPR_history": float_array(model.TPR_history),
              "FPR_history": float_array(model.FPR_history),
              "HNE_equilibrium_matching": [bool(x) for x in model.hitting_result],
              "SysFail": [bool(x) for x in model.SysFail]}
    print(json.dumps(result, allow_nan=False))


def safe_mean(values) -> float | None:
    return sum(values) / len(values) if values else None


def aggregate(results: list[dict]) -> list[dict]:
    groups = {}
    for r in results:
        if r.get("status") != "ok":
            continue
        d = r["outcome"]
        groups.setdefault((d["scheme"], d["aap"]), []).append(d)
    rows = []
    for (scheme, aap), data in sorted(groups.items(), key=lambda kv:(kv[0][0],kv[0][1] or 0)):
        all_tpr = [safe_mean(r["TPR_history"]) for r in data]
        all_fpr = [safe_mean(r["FPR_history"]) for r in data]
        all_hne = [safe_mean([float(x) for x in r["HNE_equilibrium_matching"]]) for r in data]
        rows.append({"scheme": scheme, "aap": aap, "successful_runs": len(data),
                     "MTTSF": safe_mean([r["lifetime"] for r in data]),
                     "mean_TPR": safe_mean([x for x in all_tpr if x is not None]),
                     "mean_FPR": safe_mean([x for x in all_fpr if x is not None]),
                     "mean_HNE_equilibrium_matching": safe_mean([x for x in all_hne if x is not None])})
    return rows


def evaluate(a: argparse.Namespace) -> dict:
    source, output = Path(a.source).resolve(), Path(a.output).resolve()
    if not (source / "main.py").is_file():
        raise FileNotFoundError("main.py missing from source; use prepare first")
    output.mkdir(parents=True, exist_ok=True)
    variations = [None] if a.variation == "fixed" else list(AAPS)
    selected = list(SCHEMES) if a.scheme == "all" else [a.scheme]
    for scheme in selected:
        for p in required_models(source, scheme, a.variation):
            if not p.is_file():
                raise FileNotFoundError(f"ML model is required but absent: {p}. Run non-ML schemes first; don't substitute heuristic checkpoints.")
    all_runs = []
    manifest = {"repo": GITHUB_URL, "source": str(source), "revision": source_revision(source),
                "python": sys.version, "runner": "Foureye2 independent evaluation harness",
                "original_function": "main.game_start", "samples_per_condition": a.runs,
                "seed_start": a.seed_start, "schemes": selected, "variation": a.variation,
                "timeout_seconds_per_run": a.timeout, "note": "Original simulation, new harness aggregation; not proof of paper table matching"}
    json_dump(output / "manifest.json", manifest)
    for scheme in selected:
        for aap in variations:
            for j in range(a.runs):
                seed = a.seed_start + j
                name = f"{scheme}__AAP-{str(aap).replace('.', 'p') if aap is not None else 'fixed'}__seed-{seed}"
                logfile = output / f"{name}.simulation.log"
                cmd = [sys.executable, str(Path(__file__).resolve()), "worker", "--source", str(source),
                       "--scheme", scheme, "--seed", str(seed), "--trace", str(logfile)]
                if aap is not None:
                    cmd += ["--aap", str(aap)]
                started = time.monotonic()
                try:
                    run = subprocess.run(cmd, cwd=str(source), capture_output=True, text=True,
                                         timeout=a.timeout, check=False)
                    if run.returncode == 0:
                        outcome = json.loads(run.stdout.strip().splitlines()[-1])
                        record = {"status": "ok", "outcome": outcome}
                    else:
                        record = {"status": "failed", "exit_code": run.returncode,
                                  "error": run.stderr[-8000:], "stdout": run.stdout[-2000:]}
                except subprocess.TimeoutExpired as e:
                    record = {"status": "timeout", "error": str(e)}
                except Exception as e:
                    record = {"status": "error", "error": repr(e)}
                record.update({"scheme": scheme, "aap": aap, "seed": seed,
                               "elapsed_seconds": round(time.monotonic() - started, 3),
                               "trace_file": logfile.name})
                all_runs.append(record)
                json_dump(output / "run_records.json", all_runs)
                print(f"{scheme}, AAP={aap}, seed={seed}: {record['status']}", flush=True)
                if record["status"] != "ok" and a.stop_on_error:
                    break
            if a.stop_on_error and all_runs[-1]["status"] != "ok":
                break
        if a.stop_on_error and all_runs[-1]["status"] != "ok":
            break
    summary = aggregate(all_runs)
    json_dump(output / "summary.json", summary)
    with (output / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        if summary:
            writer = csv.DictWriter(f, fieldnames=list(summary[0]))
            writer.writeheader()
            writer.writerows(summary)
    return {"total_runs": len(all_runs), "successful_runs": sum(x["status"] == "ok" for x in all_runs),
            "summary": summary, "output": str(output)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Foureye-2 provenance, compatibility and experiment runner")
    sp = parser.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("audit", help="Inspect the author source and missing model assets")
    p.add_argument("--source", required=True)
    p.add_argument("--output", default="audit.json")
    p = sp.add_parser("prepare", help="Copy the author source, preserving originals, and apply minimal compatibility fixes")
    p.add_argument("--source", required=True)
    p.add_argument("--destination", required=True)
    p = sp.add_parser("run", help="Run original main.game_start for predefined schemes/seeds")
    p.add_argument("--source", required=True)
    p.add_argument("--output", default="output/fixed")
    p.add_argument("--scheme", choices=["all", *SCHEMES], default="DD-IPI")
    p.add_argument("--runs", type=int, default=1)
    p.add_argument("--seed-start", type=int, default=10000)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--variation", choices=["fixed", "aap"], default="fixed")
    p.add_argument("--stop-on-error", action="store_true")
    p = sp.add_parser("worker", help=argparse.SUPPRESS)
    p.add_argument("--source", required=True)
    p.add_argument("--scheme", choices=list(SCHEMES), required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--aap", type=float, default=None)
    p.add_argument("--trace", required=True)
    a = parser.parse_args()
    if a.cmd == "audit":
        result = preflight(Path(a.source))
        json_dump(Path(a.output), result)
    elif a.cmd == "prepare":
        result = prepare(Path(a.source), Path(a.destination))
    elif a.cmd == "run":
        if a.runs <= 0 or a.timeout <= 0:
            parser.error("--runs and --timeout must be positive")
        result = evaluate(a)
    else:
        handle_worker(a)
        return
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(2)
