"""Provenance record for every run whose output is ever cited.

THE RULE this enforces: the persistent kernel is a scratchpad, never the
record. Explore in it freely -- but before any number it produced is cited
anywhere, the code that produced it moves into a committed .py that runs
top-to-bottom from a COLD kernel, and that run writes one of these
directories. If a number exists only as kernel history, it does not exist.

Usage is one line:

    from runlog import start_run
    run = start_run("eligibility-screen", seed=1234,
                    model_repo=MODEL_ID, model_revision=MODEL_REV)
    ...
    json.dump(payload, open(run.outputs / "eligibility-screen.json", "w"))

`start_run` creates ``results/runs/<UTC>-<slug>/`` containing
``command.txt``, ``manifest.json``, ``stdout.log`` and ``outputs/``, tees
stdout+stderr into the log, and finalises the manifest at interpreter exit
(including on an exception, which is recorded rather than hidden).

Honesty rule: this module never invents a field. Anything it cannot
determine is recorded as null with the reason, not omitted and not guessed.
Do not hand-write a manifest for work that ran before the record existed --
put a plain NOTE.md in the run directory saying so instead. An honest gap in
the record is fine; a manufactured one is not.
"""

from __future__ import annotations

import atexit
import json
import os
import platform
import socket
import subprocess
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _repo_root(start: Path | None = None) -> Path:
    p = (start or Path(__file__).resolve()).parent
    for cand in [p, *p.parents]:
        if (cand / ".git").exists():
            return cand
    return Path.cwd()


def _sh(*args: str, cwd: Path | None = None) -> str | None:
    try:
        out = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                             timeout=30)
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:
        return None


def _git(root: Path) -> dict[str, Any]:
    sha = _sh("git", "rev-parse", "HEAD", cwd=root)
    status = _sh("git", "status", "--porcelain", cwd=root)
    branch = _sh("git", "rev-parse", "--abbrev-ref", "HEAD", cwd=root)
    dirty = None if status is None else bool(status.strip())
    return {
        "sha": sha,
        "branch": branch,
        "dirty": dirty,
        # The list matters: "dirty" alone hides WHICH files differed from the
        # committed state, which is exactly what a reviewer needs to judge
        # whether the run is reproducible from the commit.
        "dirty_files": (status.splitlines() if status else []),
        "note": None if sha else "git metadata unavailable (not a repo?)",
    }


def _versions() -> dict[str, Any]:
    v: dict[str, Any] = {"python": sys.version.split()[0]}
    for mod in ("torch", "transformers", "numpy"):
        try:
            v[mod] = __import__(mod).__version__
        except Exception:
            v[mod] = None
    return v


def _gpu() -> dict[str, Any]:
    try:
        import torch
        if not torch.cuda.is_available():
            return {"available": False, "name": None,
                    "note": "torch.cuda.is_available() is False"}
        return {
            "available": True,
            "name": torch.cuda.get_device_name(0),
            "count": torch.cuda.device_count(),
            "capability": list(torch.cuda.get_device_capability(0)),
        }
    except Exception as e:
        return {"available": None, "name": None, "note": f"probe failed: {e}"}


class _Tee:
    """Duplicate a stream to a file without swallowing the original."""

    def __init__(self, stream, fh):
        self._stream, self._fh = stream, fh

    def write(self, data):
        self._stream.write(data)
        self._fh.write(data)
        self._fh.flush()
        return len(data)

    def flush(self):
        self._stream.flush()
        self._fh.flush()

    def isatty(self):
        return getattr(self._stream, "isatty", lambda: False)()


@dataclass
class Run:
    slug: str
    dir: Path
    outputs: Path
    manifest: dict[str, Any] = field(default_factory=dict)
    _fh: Any = None
    _finished: bool = False

    def note(self, text: str) -> None:
        """Record a plain-language caveat in the run directory."""
        with open(self.dir / "NOTE.md", "a") as f:
            f.write(text.rstrip() + "\n")

    def finish(self, status: str = "ok", error: str | None = None) -> None:
        if self._finished:
            return
        self._finished = True
        self.manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
        self.manifest["status"] = status
        if error:
            self.manifest["error"] = error
        self.manifest["outputs"] = sorted(
            p.name for p in self.outputs.iterdir()
        ) if self.outputs.exists() else []
        with open(self.dir / "manifest.json", "w") as f:
            json.dump(self.manifest, f, indent=2)
        sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
        if self._fh:
            self._fh.close()


def start_run(slug: str, *, root: Path | None = None, **params: Any) -> Run:
    """Open a provenance-recorded run directory. See module docstring."""
    repo = _repo_root(root)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rdir = repo / "results" / "runs" / f"{ts}-{slug}"
    outputs = rdir / "outputs"
    # Snapshot git state BEFORE creating the run directory. Otherwise the run
    # dirties the tree with its own output paths and every manifest reports
    # dirty=true, which makes the flag useless as a warning.
    git = _git(repo)
    outputs.mkdir(parents=True, exist_ok=True)

    with open(rdir / "command.txt", "w") as f:
        f.write(" ".join([sys.executable, *sys.argv]) + "\n")
        f.write(f"# cwd: {Path.cwd()}\n")

    manifest: dict[str, Any] = {
        "slug": slug,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "argv": sys.argv,
        "cwd": str(Path.cwd()),
        "git": git,
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "slurm": {
            k: os.environ.get(k)
            for k in ("SLURM_JOB_ID", "SLURM_JOB_NAME", "SLURM_JOB_ACCOUNT",
                      "SLURM_JOB_PARTITION", "SLURM_JOB_NODELIST",
                      "SLURM_JOB_GPUS")
        },
        "gpu": _gpu(),
        "versions": _versions(),
        "params": params,
        "status": "running",
    }
    with open(rdir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    fh = open(rdir / "stdout.log", "a", buffering=1)
    sys.stdout = _Tee(sys.__stdout__, fh)
    sys.stderr = _Tee(sys.__stderr__, fh)

    run = Run(slug=slug, dir=rdir, outputs=outputs, manifest=manifest, _fh=fh)

    def _atexit():
        if run._finished:
            return
        exc = sys.exc_info()[1]
        if exc is not None:
            run.finish("error", "".join(traceback.format_exception(exc)))
        else:
            run.finish("ok")

    atexit.register(_atexit)
    print(f"[runlog] {rdir.relative_to(repo)}  git={manifest['git']['sha']}"
          f"{' DIRTY' if manifest['git']['dirty'] else ''}"
          f"  slurm={manifest['slurm']['SLURM_JOB_ID']}", flush=True)
    return run
