#!/usr/bin/env python3
"""Shared rig for the week 6 probes.

The code under test is the code students run: mkprewritten.py lifts the
pre-written cells out of the two notebooks, and every probe execs that. The
guards below exist because this project has already thrown away 234 runs to a
measurement that ran while something else was rewriting its inputs, and
because a week 6 run with no API key returns a tidy row of Nones that reads
exactly like a model answering.

  assert_world()  the endpoint serves the model, the key works, and one real
                  call comes back with a non-zero token count. A probe that
                  cannot prove a call reached the model does not start.
  digests()       sha256 of every corpus email, both notebooks and the rig
                  source, written INTO the result file. Compare before
                  quoting any number out of it.
"""
import hashlib
import io
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BUILDER = ROOT / "builder"
EMAILS = BUILDER / "corpus/emails/teaching"
NOTEBOOKS = [BUILDER / "lab/notebooks/w6-lab.ipynb",
             BUILDER / "instructor/solutions/w6-lab-solution.ipynb"]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digests(rig_path):
    """Everything whose bytes could change an answer, hashed."""
    out = {"emails": {}, "notebooks": {}, "rig": {}}
    for eml in sorted(EMAILS.glob("*.eml")):
        out["emails"][eml.name] = sha256(eml)
    for nb in NOTEBOOKS:
        out["notebooks"][nb.name] = sha256(nb)
    out["rig"][Path(rig_path).name] = sha256(rig_path)
    return out


def quiet(fn, *args, **kwargs):
    """Run something with the notebook's own printing swallowed."""
    keep = sys.stdout
    sys.stdout = io.StringIO()
    try:
        return fn(*args, **kwargs)
    finally:
        sys.stdout = keep


def load(rig_path, model=None, base_url=None):
    """Exec one extracted rig and hand back its globals."""
    if model:
        os.environ["ITSY1377_MODEL"] = model
    if base_url:
        os.environ["ITSY1377_BASE_URL"] = base_url
    if not os.environ.get("ITSY1377_API_KEY"):
        sys.exit("ITSY1377_API_KEY is not set. Refusing to run: without it "
                 "every verdict comes back None and the summary still fills in.")
    # The corpus path walk in cell 1 looks upward for corpus/emails/teaching.
    os.chdir(BUILDER)
    g = {"__name__": "__main__"}
    quiet(exec, compile(Path(rig_path).read_text(), "rig", "exec"), g)
    g["SHOW_CALL_TOKENS"] = False
    return g


def assert_world(g, model):
    """Prove the endpoint, the model and the key before measuring anything."""
    import requests
    base = g["BASE_URL"].rstrip("/")
    head = {"Authorization": "Bearer " + g["API_KEY"]}
    served = requests.get(base + "/models", headers=head, timeout=30).json()
    names = [m["id"] for m in served.get("data", [])]
    if model not in names:
        sys.exit("model %r is not served. Served: %s" % (model, names))
    g["start_run"]()
    reply = quiet(g["ask_model"], "Reply with the word ready and nothing else.")
    spent = g["RUN_USAGE"]["total"]
    if spent <= 0:
        sys.exit("a live call reported 0 tokens. The call did not reach the "
                 "model; every number after this would be a zero that reads "
                 "like data. Reply was: %r" % (reply,))
    g["start_run"]()
    return {"models_served": names, "probe_reply": str(reply)[:80],
            "probe_tokens": spent}


class Result:
    """A result file that is written after every trial, not at the end."""

    def __init__(self, path, meta):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.doc = dict(meta)
        self.doc["runs"] = []
        self.doc["failed_runs"] = 0
        self.write()

    def add(self, row):
        self.doc["runs"].append(row)
        if row.get("error"):
            self.doc["failed_runs"] += 1
        self.write()

    def summarize(self, summary):
        self.doc["summary"] = summary
        self.doc["usable"] = len(self.doc["runs"]) - self.doc["failed_runs"]
        if self.doc["failed_runs"]:
            self.doc["WARNING"] = ("%d of %d runs failed. Read usable before "
                                   "quoting anything."
                                   % (self.doc["failed_runs"],
                                      len(self.doc["runs"])))
        self.write()

    def write(self):
        self.path.write_text(json.dumps(self.doc, indent=1, sort_keys=True))


def start(name, rig_name, model, argv_note=""):
    """Everything a probe does before its first measured call."""
    rig = Path(os.environ.get("W6_RIG_DIR", "/tmp")) / rig_name
    g = load(rig, model=model)
    world = assert_world(g, model)
    meta = {"probe": name, "model": model, "base_url": g["BASE_URL"],
            "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "note": argv_note, "world": world, "digests": digests(rig)}
    return g, meta
