# -*- coding: utf-8 -*-
"""GPU PC 2: what this machine can run. Reads only; installs and changes nothing.

    python reproductions/pc2_check.py

Writes reproductions/out/PC2_ENVIRONMENT.txt (and .json): Python, PyTorch, CUDA and the GPU (with a
short real GPU test), Git, Docker, MATLAB, free disk and RAM, and the repository state. No user
name, machine name or path outside the repository is written.
"""
from __future__ import annotations

import ctypes
import glob
import json
import os
import platform
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out")


def run(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=REPO)
        return p.returncode, (p.stdout or p.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, f"{type(e).__name__}"


def ram_gb():
    if os.name == "nt":
        class MS(ctypes.Structure):
            _fields_ = [("len", ctypes.c_ulong), ("load", ctypes.c_ulong), ("total", ctypes.c_ulonglong),
                        ("avail", ctypes.c_ulonglong), ("tp", ctypes.c_ulonglong), ("ap", ctypes.c_ulonglong),
                        ("tv", ctypes.c_ulonglong), ("av", ctypes.c_ulonglong), ("ext", ctypes.c_ulonglong)]
        m = MS()
        m.len = ctypes.sizeof(MS)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
            return round(m.total / 2**30, 1), round(m.avail / 2**30, 1)
    try:
        pages, size = os.sysconf("SC_PHYS_PAGES"), os.sysconf("SC_PAGE_SIZE")
        return round(pages * size / 2**30, 1), None
    except (ValueError, OSError, AttributeError):
        return None, None


def torch_info():
    try:
        import torch
    except ImportError:
        return {"installed": False}
    info = {"installed": True, "version": torch.__version__, "cuda_build": torch.version.cuda,
            "cuda_available": torch.cuda.is_available()}
    if info["cuda_available"]:
        p = torch.cuda.get_device_properties(0)
        info.update(gpu=p.name, gpu_memory_gb=round(p.total_memory / 2**30, 1), gpu_count=torch.cuda.device_count())
        x = torch.randn(4096, 4096, device="cuda")
        torch.cuda.synchronize()
        t0 = time.time()
        for _ in range(20):
            y = x @ x
        torch.cuda.synchronize()
        info["gpu_test"] = f"20 matrix products 4096x4096 in {time.time() - t0:.2f} s, finite: {bool(torch.isfinite(y).all())}"
    return info


def matlab_paths():
    found = []
    w = shutil.which("matlab")
    if w:
        found.append(w)
    for pat in (r"C:\Program Files\MATLAB\*\bin\matlab.exe", "/usr/local/MATLAB/*/bin/matlab",
                "/Applications/MATLAB_*.app/bin/matlab"):
        found += glob.glob(pat)
    return sorted(set(found))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    r = {"made": time.strftime("%Y-%m-%d %H:%M"), "os": platform.platform(), "python": sys.version.split()[0],
         "python_ok": sys.version_info >= (3, 11)}
    for mod in ("numpy", "scipy"):
        try:
            r[mod] = __import__(mod).__version__
        except ImportError:
            r[mod] = "NOT INSTALLED"
    r["torch"] = torch_info()
    rc, v = run(["git", "--version"])
    r["git"] = v if rc == 0 else "NOT FOUND"
    rc, v = run(["docker", "--version"])
    r["docker"] = v if rc == 0 else "NOT FOUND"
    if rc == 0:
        rc2, _ = run(["docker", "info"], timeout=30)
        r["docker_running"] = rc2 == 0
    m = matlab_paths()
    r["matlab"] = [os.path.basename(os.path.dirname(os.path.dirname(p))) for p in m] or "NOT FOUND"
    r["disk_free_gb"] = round(shutil.disk_usage(REPO).free / 2**30, 1)
    r["ram_total_gb"], r["ram_free_gb"] = ram_gb()
    rc, head = run(["git", "rev-parse", "--short", "HEAD"])
    rc2, status = run(["git", "status", "--porcelain"])
    r["repo_commit"] = head if rc == 0 else "?"
    r["repo_clean"] = rc2 == 0 and status == ""

    t = r["torch"]
    can = {
        "PyTorch on GPU (Yu et al. seq2seq, DeepOP, our encoders)": bool(t.get("cuda_available")),
        "Docker (TMLCN: Conpot honeypot)": r.get("docker_running", False),
        "MATLAB (Co-ADAM)": r["matlab"] != "NOT FOUND",
        "Python 3.11+ with numpy and scipy (Kuwano, Shell Attack Evolution, HoneyGPT tables)":
            r["python_ok"] and "NOT" not in r["numpy"] + r["scipy"],
        "Disk >= 50 GB free (raw honeypot logs)": r["disk_free_gb"] >= 50,
    }
    r["can_run"] = can
    L = ["GPU PC 2: ENVIRONMENT", f"made {r['made']}", "",
         f"OS            {r['os']}", f"Python        {r['python']}  numpy {r['numpy']}  scipy {r['scipy']}",
         f"PyTorch       {t.get('version', 'NOT INSTALLED')}  CUDA build {t.get('cuda_build')}  "
         f"CUDA available {t.get('cuda_available')}",
         f"GPU           {t.get('gpu', '-')}  {t.get('gpu_memory_gb', '-')} GB  x{t.get('gpu_count', 0)}",
         f"GPU test      {t.get('gpu_test', '-')}",
         f"Git           {r['git']}", f"Docker        {r['docker']}  running {r.get('docker_running', '-')}",
         f"MATLAB        {r['matlab']}", f"Disk free     {r['disk_free_gb']} GB",
         f"RAM           {r['ram_total_gb']} GB total, {r['ram_free_gb']} GB free",
         f"Repository    commit {r['repo_commit']}, clean {r['repo_clean']}", "", "CAN THIS PC RUN ..."]
    L += [f"  {'YES' if ok else 'NO '}  {k}" for k, ok in can.items()]
    text = "\n".join(L) + "\n"
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "PC2_ENVIRONMENT.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    with open(os.path.join(OUT, "PC2_ENVIRONMENT.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(r, fh, indent=1)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
