#!/usr/bin/env python3
"""Generate paired two-hop relational-binding prompts.

THIS IS A METHOD EVALUATION. The narrow relational-binding task generated here
is an *instrument* for evaluating an interpretability method. It is not circuit
discovery, and no output of this script is evidence about any model's internal
mechanism.

WHAT IT WRITES
--------------
    <out>/dev.jsonl        10 pairs   (40 records)  -- develop against this
    <out>/heldout.jsonl    40 pairs  (160 records)  -- DO NOT LOOK AT THIS
    <out>/manifest.json    seed, model/revision, counts, content hashes
    <out>/tokenization_report.json   the audit that justifies the vocabulary

HELD-OUT DISCIPLINE
-------------------
`heldout.jsonl` is never tuned on and must not be inspected during development.
No threshold, no template edit, no vocabulary change, and no hyperparameter may
be chosen by looking at it. This script deliberately never prints held-out
content to stdout -- only counts and a hash -- so that running it does not by
itself break the discipline. Dev and held-out pairs are drawn from the same
seeded stream and are disjoint by index (dev = pairs 0..9, held-out = 10..49).

DETERMINISM
-----------
One fixed seed, recorded in every record and in the manifest. No timestamps are
written anywhere, so the same seed reproduces byte-identical files.

EVERY NUMBER THIS SCRIPT PRODUCES IS agent-unverified.

Usage (ARC login node -- tokenizer only, no model, no GPU):

    source /scratch/djjay/mats12/venv/bin/activate
    export HF_HOME=/scratch/djjay/mats12/hf-cache
    python src/make_dataset.py --out /scratch/djjay/mats12/dataset-wip/data

    python src/make_dataset.py --self-test    # no tokenizer needed
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import task_templates as tt  # noqa: E402

MODEL_ID = "Qwen/Qwen3.5-4B"
REVISION = "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a"
DEFAULT_SEED = 20260827
N_DEV = 10
N_HELDOUT = 40

# Order is fixed so that JSON serialisation is byte-stable.
RECORD_FIELDS = (
    "pair_id", "record_id", "template_id", "lexicon", "fact_order", "variant",
    "cell", "shot", "seed", "prompt", "prompt_n_tokens",
    "person_q", "person_d",
    "intermediate", "answer", "alt_intermediate", "alt_answer",
    "intermediate_id", "answer_id", "alt_intermediate_id", "alt_answer_id",
)

DEV_HEADER = (
    "DEV split. Method evaluation, not circuit discovery. Develop, tune and "
    "debug against this file only."
)
HELDOUT_HEADER = (
    "HELD-OUT split. Method evaluation, not circuit discovery. This file is "
    "never tuned on and must not be inspected during development: no "
    "threshold, template, vocabulary item or hyperparameter may be chosen by "
    "looking at it. Read it once, at evaluation time, after the method is "
    "frozen."
)


# --------------------------------------------------------------------------
# Stub tokenizer -- structural self-test only, never used for real output
# --------------------------------------------------------------------------

class StubTokenizer:
    """A whitespace/punctuation tokenizer with the same surface API.

    Exists so the generator's structure can be exercised without downloading a
    model. It treats every space-prefixed word as one token, which is exactly
    the property the real filter is checking for, so it verifies the plumbing
    while proving nothing about Qwen BPE. Real output must be built with the
    real tokenizer; `--self-test` refuses to write a dataset.
    """

    padding_side = "right"

    def __init__(self) -> None:
        self._vocab: dict[str, int] = {}

    def _id(self, piece: str) -> int:
        return self._vocab.setdefault(piece, len(self._vocab) + 1000)

    def encode(self, text: str, add_special_tokens: bool = False) -> list[int]:
        ids: list[int] = []
        for i, chunk in enumerate(text.split(" ")):
            if chunk == "":
                continue
            core = chunk.rstrip(".?:")
            tail = chunk[len(core):]
            if core:
                ids.append(self._id(("Ġ" if i else "") + core))
            for ch in tail:
                ids.append(self._id(ch))
        return ids


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def load_tokenizer(model_id: str, revision: str) -> Any:
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(model_id, revision=revision)


def pair_to_records(tok: Any, pair: tt.Pair, prompt_n_tokens: int) -> list[dict]:
    recs = []
    for v in pair.variants:
        row = {
            "pair_id": pair.pair_id,
            "record_id": f"{pair.pair_id}-{v.variant}{v.fact_order}",
            "template_id": pair.template_id,
            "lexicon": pair.lexicon,
            "fact_order": v.fact_order,
            "variant": v.variant,
            "cell": v.cell,
            "shot": pair.shot,
            "seed": pair.seed,
            "prompt": v.prompt,
            "prompt_n_tokens": prompt_n_tokens,
            "person_q": pair.person_q,
            "person_d": pair.person_d,
            "intermediate": v.intermediate,
            "answer": v.answer,
            "alt_intermediate": v.alt_intermediate,
            "alt_answer": v.alt_answer,
            "intermediate_id": tt.single_token_id(tok, v.intermediate),
            "answer_id": tt.single_token_id(tok, v.answer),
            "alt_intermediate_id": tt.single_token_id(tok, v.alt_intermediate),
            "alt_answer_id": tt.single_token_id(tok, v.alt_answer),
        }
        assert set(row) == set(RECORD_FIELDS), sorted(set(row) ^ set(RECORD_FIELDS))
        recs.append({k: row[k] for k in RECORD_FIELDS})
    return recs


def build_split(tok: Any, *, lexicons: list[str], n_pairs: int, seed: int,
                start_index: int, shot: str) -> tuple[list[tt.Pair], list[dict]]:
    """Build `n_pairs` pairs, cycling the lexicon across pairs.

    Cycling keeps the requested pair counts exact while still covering more
    than one familiarity condition.
    """
    pairs: list[tt.Pair] = []
    for k in range(n_pairs):
        lex = lexicons[k % len(lexicons)]
        idx = start_index + k
        built = tt.build_pairs(tok, n_pairs=1, seed=seed + idx, lexicon=lex,
                               shot=shot, start_index=idx)
        pairs.extend(built)

    records: list[dict] = []
    for p in pairs:
        info = tt.verify_pair_tokenization(tok, p)
        records.extend(pair_to_records(tok, p, info["prompt_n_tokens"]))
    return pairs, records


def dumps(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def write_jsonl(path: str, header: str, records: list[dict], meta: dict) -> str:
    """Write JSONL with a leading `_meta` record carrying the split header."""
    lines = [dumps({"_meta": True, "header": header, **meta})]
    lines += [dumps(r) for r in records]
    blob = "\n".join(lines) + "\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(blob)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="data")
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--n-dev", type=int, default=N_DEV)
    ap.add_argument("--n-heldout", type=int, default=N_HELDOUT)
    ap.add_argument("--lexicons", default="real",
                    help="comma-separated; cycled across pairs. "
                         f"known: {','.join(sorted(tt.LEXICONS))}")
    ap.add_argument("--shot", default="zero", choices=("zero", "few"))
    ap.add_argument("--model", default=MODEL_ID)
    ap.add_argument("--revision", default=REVISION)
    ap.add_argument("--show-dev", type=int, default=0,
                    help="print this many DEV prompts (never held-out)")
    ap.add_argument("--self-test", action="store_true",
                    help="structural check with a stub tokenizer; writes nothing")
    args = ap.parse_args(argv)

    lexicons = [s.strip() for s in args.lexicons.split(",") if s.strip()]

    if args.self_test:
        tok = StubTokenizer()
        for lex in sorted(tt.LEXICONS):
            _, recs = build_split(tok, lexicons=[lex], n_pairs=6,
                                  seed=args.seed, start_index=0, shot="zero")
            assert len(recs) == 6 * 4, len(recs)
            for r in recs:
                assert set(r) == set(RECORD_FIELDS)
            print(f"self-test  lexicon={lex:7s} pairs=6 records={len(recs)} OK")
        try:
            tt.build_pairs(tok, n_pairs=1, seed=0, lexicon="nonce")
        except tt.LexiconError:
            print("self-test  lexicon='nonce' correctly refused")
        else:
            raise AssertionError("lexicon 'nonce' should have been refused")
        # determinism
        a = build_split(tok, lexicons=["real"], n_pairs=5, seed=1,
                        start_index=0, shot="zero")[1]
        b = build_split(StubTokenizer(), lexicons=["real"], n_pairs=5, seed=1,
                        start_index=0, shot="zero")[1]
        assert [r["prompt"] for r in a] == [r["prompt"] for r in b]
        print("self-test  determinism OK")
        # left-padding guard fires
        try:
            tt.assert_left_padding(tok)
        except tt.PaddingSideError:
            print("self-test  left-padding guard correctly refused padding_side='right'")
        else:
            raise AssertionError("padding guard did not fire")
        print("self-test  PASSED (structure only; proves nothing about Qwen BPE)")
        return 0

    tok = load_tokenizer(args.model, args.revision)
    os.makedirs(args.out, exist_ok=True)

    audit = {lex: tt.audit_lexicon(tok, lex) for lex in sorted(tt.LEXICONS)}
    dead = {
        "NONCE_PEOPLE": tt.DEAD_NONCE_PEOPLE,
        "NONCE_PLACES": tt.DEAD_NONCE_PLACES,
        "NONCE_OBJECTS": tt.DEAD_NONCE_OBJECTS,
    }
    dead_audit = {}
    for name, words in dead.items():
        kept = tt.filter_single_token(tok, words)
        dead_audit[name] = {"n_candidates": len(words), "n_survived": len(kept),
                            "survivors": kept}

    dev_pairs, dev_recs = build_split(
        tok, lexicons=lexicons, n_pairs=args.n_dev, seed=args.seed,
        start_index=0, shot=args.shot)
    ho_pairs, ho_recs = build_split(
        tok, lexicons=lexicons, n_pairs=args.n_heldout, seed=args.seed,
        start_index=args.n_dev, shot=args.shot)

    assert not (set(p.pair_id for p in dev_pairs) &
                set(p.pair_id for p in ho_pairs)), "dev/held-out overlap"

    common = {"seed": args.seed, "model": args.model, "revision": args.revision,
              "lexicons": lexicons, "shot": args.shot,
              "framing": "method evaluation, not circuit discovery"}
    dev_path = os.path.join(args.out, "dev.jsonl")
    ho_path = os.path.join(args.out, "heldout.jsonl")
    dev_hash = write_jsonl(dev_path, DEV_HEADER, dev_recs,
                           {**common, "split": "dev", "n_pairs": len(dev_pairs)})
    ho_hash = write_jsonl(ho_path, HELDOUT_HEADER, ho_recs,
                          {**common, "split": "heldout", "n_pairs": len(ho_pairs)})

    report = {
        "framing": "method evaluation, not circuit discovery",
        "provenance": "agent-unverified",
        "tokenizer_class": type(tok).__name__,
        "vocab_size": getattr(tok, "vocab_size", None),
        "len_tokenizer": len(tok),
        "padding_side_default": getattr(tok, "padding_side", None),
        "model": args.model, "revision": args.revision,
        "space_prefix_demo": {
            "Ralph": tok.convert_ids_to_tokens(
                tok.encode("Ralph", add_special_tokens=False)),
            " Ralph": tok.convert_ids_to_tokens(
                tok.encode(" Ralph", add_special_tokens=False)),
        },
        "registered_lexicons": audit,
        "removed_nonce_lists": dead_audit,
        "prompt_n_tokens": sorted({r["prompt_n_tokens"] for r in dev_recs + ho_recs}),
    }
    rep_path = os.path.join(args.out, "tokenization_report.json")
    with open(rep_path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(report, ensure_ascii=False, indent=2,
                            sort_keys=True) + "\n")

    manifest = {
        "framing": "method evaluation, not circuit discovery",
        "provenance": "agent-unverified",
        "seed": args.seed, "model": args.model, "revision": args.revision,
        "lexicons": lexicons, "shot": args.shot,
        "n_dev_pairs": len(dev_pairs), "n_dev_records": len(dev_recs),
        "n_heldout_pairs": len(ho_pairs), "n_heldout_records": len(ho_recs),
        "records_per_pair": len(tt.FACT_ORDERS) * len(tt.BINDING_VARIANTS),
        "templates": [t.tid for t in tt.TEMPLATES],
        "preamble": tt.PREAMBLE,
        "sha256": {"dev.jsonl": dev_hash, "heldout.jsonl": ho_hash},
        "heldout_policy": HELDOUT_HEADER,
    }
    with open(os.path.join(args.out, "manifest.json"), "w",
              encoding="utf-8") as fh:
        fh.write(json.dumps(manifest, ensure_ascii=False, indent=2,
                            sort_keys=True) + "\n")

    print(f"seed={args.seed} lexicons={','.join(lexicons)} "
          f"templates={len(tt.TEMPLATES)}")
    print(f"dev      {len(dev_pairs):3d} pairs {len(dev_recs):4d} records  "
          f"sha256={dev_hash[:16]}  {dev_path}")
    print(f"heldout  {len(ho_pairs):3d} pairs {len(ho_recs):4d} records  "
          f"sha256={ho_hash[:16]}  {ho_path}  (NOT INSPECTED)")
    print(f"report   {rep_path}")
    for lex in sorted(audit):
        a = audit[lex]
        print(f"audit    {lex:7s} people {a['people']['n_survived']}/"
              f"{a['people']['n_candidates']}  places "
              f"{a['places']['n_survived']}/{a['places']['n_candidates']}  "
              f"objects {a['objects']['n_survived']}/"
              f"{a['objects']['n_candidates']}")
    for name, d in dead_audit.items():
        print(f"audit    {name:14s} {d['n_survived']}/{d['n_candidates']} "
              f"survived  (removed from LEXICONS)")
    if args.show_dev:
        print("--- DEV samples ---")
        for r in dev_recs[:args.show_dev]:
            print(f"[{r['record_id']}] {r['prompt']}")
            print(f"    -> intermediate={r['intermediate']}({r['intermediate_id']}) "
                  f"answer={r['answer']}({r['answer_id']}) "
                  f"alt={r['alt_answer']}({r['alt_answer_id']}) "
                  f"n_tok={r['prompt_n_tokens']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
