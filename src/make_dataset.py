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

SHARED CLOSED VOCABULARY (`--vocab-pool N`, default 6)
-----------------------------------------------------
Every pair draws its intermediates -- and the objects paired with them -- from
ONE shared pool of N words rather than from fresh words per pair. Two reasons,
and only the first is a bug fix:

1.  Leave-one-pair-out needs class support outside the held-out pair. With
    private vocabulary per pair, 14 distinct intermediate classes fell across
    10 pairs and 9 of them appeared in exactly one pair, so holding that pair
    out deleted the only support for its classes: the stage-1 run scored 12 of
    40 records and returned `class_unseen_in_fit` for the other 28. A shared
    pool gives every class at least `--min-pairs-per-class` pairs of support.

2.  It removes a possible class-identity shortcut. If a class only ever
    appeared as the CORRECT intermediate, a difference-in-means fit could reach
    a high in-sample number by recognising the class rather than the binding.
    (Measured on the pre-change dev split this shortcut was already absent --
    the A/B construction puts both places of a pair in both roles, so every
    class had equal correct and alternative counts. The self-check below now
    ASSERTS that property instead of leaving it to be re-derived.)

A shared pool also makes the arm-3 promise in section 2.5 checkable at all:
h_bar and mu are fitted on dev and applied UNCHANGED to held-out, which is only
meaningful if the two splits share a class vocabulary. They now do.

The place->object pairing is still drawn per pair. Fixing it globally would make
the intermediate and the answer perfectly co-linear across the dataset, and arm
3 would stop distinguishing "the intermediate is linearly present" from "the
answer is linearly present".

SELF-CHECK
----------
Before anything is written, both splits are checked for
  * every intermediate class present in >= `--min-pairs-per-class` pairs, and
  * every intermediate class present in BOTH roles (correct and alternative),
  * no duplicate prompt strings within a split.
A failure prints the per-class table and exits 3 WITHOUT writing, so a dataset
that cannot support leave-one-pair-out is never emitted silently.
`--allow-thin-classes` downgrades the failure to a warning; it exists so the
pre-change dataset can be reproduced deliberately, not so the check can be
skipped by accident.

DETERMINISM
-----------
One fixed seed, recorded in every record and in the manifest. No timestamps are
written anywhere, so the same seed reproduces byte-identical files. The shared
pool is sampled once from the same seed and is IDENTICAL for dev and held-out.

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
from collections import Counter, defaultdict
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import task_templates as tt  # noqa: E402

MODEL_ID = "Qwen/Qwen3.5-4B"
REVISION = "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a"
DEFAULT_SEED = 20260827
N_DEV = 10
N_HELDOUT = 40
# 6 places over the round-robin schedule gives every class >= 3 of the 10 dev
# pairs; see `round_robin_schedule` in task_templates for why the prefix of the
# schedule is balanced and `itertools.combinations` would not be.
DEFAULT_VOCAB_POOL = 6
DEFAULT_MIN_PAIRS_PER_CLASS = 3

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
                start_index: int, shot: str,
                vocab_pool: int = 0) -> tuple[list[tt.Pair], list[dict]]:
    """Build `n_pairs` pairs, cycling the lexicon across pairs.

    Cycling keeps the requested pair counts exact while still covering more
    than one familiarity condition.

    `vocab_pool` is forwarded with `pool_seed=seed` -- the BASE seed, not the
    per-pair `seed + idx`. That is what makes the shared pool identical for dev
    and held-out, which is in turn what makes "fit mu on dev, apply unchanged to
    held-out" mean anything.
    """
    pairs: list[tt.Pair] = []
    for k in range(n_pairs):
        lex = lexicons[k % len(lexicons)]
        idx = start_index + k
        built = tt.build_pairs(tok, n_pairs=1, seed=seed + idx, lexicon=lex,
                               shot=shot, start_index=idx,
                               vocab_pool=vocab_pool, pool_seed=seed)
        pairs.extend(built)

    records: list[dict] = []
    for p in pairs:
        info = tt.verify_pair_tokenization(tok, p)
        records.extend(pair_to_records(tok, p, info["prompt_n_tokens"]))
    return pairs, records


def class_support(records: list[dict], min_pairs: int) -> dict:
    """Per-intermediate-class pair counts and correct/alternative role counts.

    A "class" is an intermediate token. `n_pairs` counts the DISTINCT pairs the
    class occurs in, in either role, because that is what leave-one-pair-out
    actually consumes: the fold that holds out pair P still contains the class
    iff the class occurs in some pair other than P.
    """
    pairs: dict[str, set] = defaultdict(set)
    correct: Counter = Counter()
    alternative: Counter = Counter()
    for r in records:
        pairs[r["intermediate"]].add(r["pair_id"])
        pairs[r["alt_intermediate"]].add(r["pair_id"])
        correct[r["intermediate"]] += 1
        alternative[r["alt_intermediate"]] += 1

    rows = [
        {"intermediate": c,
         "intermediate_id": next(r["intermediate_id"] for r in records
                                 if r["intermediate"] == c) if correct[c] else None,
         "n_pairs": len(pairs[c]),
         "n_correct": correct[c],
         "n_alternative": alternative[c]}
        for c in sorted(pairs, key=lambda c: (-len(pairs[c]), c))
    ]
    thin = [r["intermediate"] for r in rows if r["n_pairs"] < min_pairs]
    single_role = [r["intermediate"] for r in rows
                   if r["n_correct"] == 0 or r["n_alternative"] == 0]
    prompts = [r["prompt"] for r in records]
    dupes = sorted({p for p in prompts if prompts.count(p) > 1})
    return {
        "n_records": len(records),
        "n_pairs": len({r["pair_id"] for r in records}),
        "n_classes": len(rows),
        "min_pairs_per_class_observed": min((r["n_pairs"] for r in rows),
                                            default=0),
        "min_pairs_per_class_required": min_pairs,
        "rows": rows,
        "thin_classes": thin,
        "single_role_classes": single_role,
        "n_duplicate_prompts": len(dupes),
        "ok": not thin and not single_role and not dupes,
    }


def print_class_support(name: str, rep: dict, *, detail: bool) -> None:
    print(f"classes  {name:8s} n_classes={rep['n_classes']:3d} "
          f"min_pairs/class={rep['min_pairs_per_class_observed']:2d} "
          f"(need >= {rep['min_pairs_per_class_required']})  "
          f"thin={len(rep['thin_classes'])} single_role="
          f"{len(rep['single_role_classes'])} dup_prompts="
          f"{rep['n_duplicate_prompts']}  "
          f"{'OK' if rep['ok'] else 'FAIL'}")
    if not detail:
        return
    for r in rep["rows"]:
        print(f"  class  {r['intermediate']:12s} pairs={r['n_pairs']:2d}  "
              f"correct={r['n_correct']:3d}  alternative={r['n_alternative']:3d}")


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
    ap.add_argument("--vocab-pool", type=int, default=DEFAULT_VOCAB_POOL,
                    help="draw intermediates and their paired objects for ALL "
                         "pairs from one shared pool of this many words. "
                         "0 disables pooling (fresh words per pair) and will "
                         "fail the class-support self-check.")
    ap.add_argument("--min-pairs-per-class", type=int,
                    default=DEFAULT_MIN_PAIRS_PER_CLASS,
                    help="every intermediate class must occur in at least this "
                         "many pairs, or nothing is written")
    ap.add_argument("--allow-thin-classes", action="store_true",
                    help="downgrade a failed class-support self-check to a "
                         "warning and write anyway. For deliberately "
                         "reproducing the pre-change dataset only.")
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
        # round-robin schedule: covers every unordered pair exactly once, and
        # its PREFIX is balanced (that is the property vocab_pool relies on).
        for n in (4, 5, 6, 7, 8):
            sch = tt.round_robin_schedule(n)
            assert len(sch) == n * (n - 1) // 2, (n, len(sch))
            assert len(set(sch)) == len(sch), n
        print("self-test  round_robin_schedule covers every pair once OK")
        # pooled build: 10 pairs, pool 6 -> every class in >= 3 pairs, and in
        # both roles. Structure only; the stub tokenizer proves nothing about
        # Qwen BPE, but the class arithmetic is tokenizer-independent.
        _, pooled = build_split(StubTokenizer(), lexicons=["real"], n_pairs=10,
                                seed=args.seed, start_index=0, shot="zero",
                                vocab_pool=DEFAULT_VOCAB_POOL)
        rep = class_support(pooled, DEFAULT_MIN_PAIRS_PER_CLASS)
        print_class_support("stub-dev", rep, detail=True)
        assert rep["ok"], rep
        print("self-test  vocab-pool class support OK")
        # and the unpooled build must still FAIL that check, or the check is
        # not measuring anything.
        _, thin = build_split(StubTokenizer(), lexicons=["real"], n_pairs=10,
                              seed=args.seed, start_index=0, shot="zero",
                              vocab_pool=0)
        assert not class_support(thin, DEFAULT_MIN_PAIRS_PER_CLASS)["ok"]
        print("self-test  unpooled build correctly fails the class check")
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
        start_index=0, shot=args.shot, vocab_pool=args.vocab_pool)
    ho_pairs, ho_recs = build_split(
        tok, lexicons=lexicons, n_pairs=args.n_heldout, seed=args.seed,
        start_index=args.n_dev, shot=args.shot, vocab_pool=args.vocab_pool)

    assert not (set(p.pair_id for p in dev_pairs) &
                set(p.pair_id for p in ho_pairs)), "dev/held-out overlap"

    # ---------------------------------------------------------- self-check
    # Runs BEFORE anything is written. A dataset that cannot support
    # leave-one-pair-out must not reach disk without someone deciding it should.
    dev_support = class_support(dev_recs, args.min_pairs_per_class)
    ho_support = class_support(ho_recs, args.min_pairs_per_class)
    print(f"vocab_pool={args.vocab_pool} "
          f"min_pairs_per_class={args.min_pairs_per_class}")
    # Full per-class detail for DEV. For HELD-OUT only the aggregate line: the
    # held-out split is not inspected during development, and the aggregate is
    # all the check needs to report.
    print_class_support("dev", dev_support, detail=True)
    print_class_support("heldout", ho_support, detail=False)
    if not (dev_support["ok"] and ho_support["ok"]):
        bad = []
        for name, rep in (("dev", dev_support), ("heldout", ho_support)):
            if rep["thin_classes"]:
                bad.append(f"{name}: {len(rep['thin_classes'])} class(es) in "
                           f"fewer than {args.min_pairs_per_class} pairs")
            if rep["single_role_classes"]:
                bad.append(f"{name}: {len(rep['single_role_classes'])} class(es) "
                           "appear in only one role")
            if rep["n_duplicate_prompts"]:
                bad.append(f"{name}: {rep['n_duplicate_prompts']} duplicate "
                           "prompt string(s)")
        msg = "; ".join(bad)
        if not args.allow_thin_classes:
            print(f"\nSELF-CHECK FAILED -- nothing written. {msg}")
            print("Leave-one-pair-out cannot score records whose class has no "
                  "support outside the held-out pair. Raise --vocab-pool, or "
                  "pass --allow-thin-classes if a thin dataset is what you "
                  "actually want.")
            return 3
        print(f"\nSELF-CHECK FAILED but --allow-thin-classes was passed. {msg}")

    common = {"seed": args.seed, "model": args.model, "revision": args.revision,
              "lexicons": lexicons, "shot": args.shot,
              "vocab_pool": args.vocab_pool,
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
        "vocab_pool": args.vocab_pool,
        "vocab_pool_note": (
            "intermediates and their paired objects for every pair are drawn "
            "from one shared pool of this many words, assigned by "
            "task_templates.round_robin_schedule, so that leave-one-pair-out "
            "has class support outside each held-out pair. 0 = disabled."),
        "min_pairs_per_class": args.min_pairs_per_class,
        "class_support_dev": dev_support,
        "class_support_heldout": {k: v for k, v in ho_support.items()
                                  if k != "rows"},
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
          f"templates={len(tt.TEMPLATES)} vocab_pool={args.vocab_pool}")
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
