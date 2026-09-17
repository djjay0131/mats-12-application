"""Shared helpers for Phase 1 steps 2-5 (post-MATS continuation).

Everything here REUSES the application's code paths rather than re-deriving
them: model/lens identifiers, `ranks_of`, `resolve_positions`, `derangement`
and `randomize_lens` come from experiments/stage1/passive_readout.py; the
query-position anchoring is a verbatim copy of
experiments/stage3/heldout_frozen.py::anchored_positions; arm 3 uses
supervised_reference.fit_centroids / margin_of. The only new resolution is
FACT-TOKEN positions (city, person, period of each person->place sentence),
located through the tokenizer's offset mapping and verified token-by-token.

METHOD EVALUATION, not circuit discovery. Every number agent-unverified.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments" / "stage1"))

import task_templates as tt                                  # noqa: E402
from passive_readout import (MODEL_ID, MODEL_REV, LENS_REPO, LENS_REV,  # noqa: E402,F401
                             LENS_FILE, ranks_of, resolve_positions,
                             randomize_lens, derangement)
from supervised_reference import fit_centroids, margin_of      # noqa: E402,F401

FREEZE = json.loads((ROOT / "experiments" / "stage3" / "freeze.json").read_text())
QPOS = ["prequery", "relcomp", "qmark", "final"]
# fact-token positions: <token>_<role>, role q = queried person's sentence,
# role d = distractor's sentence
FPOS = ["person_q", "city_q", "period_q", "person_d", "city_d", "period_d"]
DATASETS = {"dev": "results/datasets/dev.jsonl",
            "heldout": "results/datasets/heldout.jsonl",
            "heldout2": "results/datasets/heldout2.jsonl"}
TEMPLATES = {t.tid: t for t in tt.TEMPLATES}


def read_split(path, want):
    rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    meta = next((r for r in rows if r.get("_meta")), {})
    recs = [r for r in rows if not r.get("_meta")]
    if meta.get("split") != want:
        sys.exit(f"REFUSING: {path} split is {meta.get('split')!r}, wanted {want!r}")
    return meta, recs


def load_all(dev_path=DATASETS["dev"], heldout_path=DATASETS["heldout"],
             heldout2_path=DATASETS["heldout2"]):
    """dev, heldout (application draw), heldout2 (Phase 1 draw)."""
    _, dev = read_split(dev_path, "dev")
    _, ho = read_split(heldout_path, "heldout")
    _, ho2 = read_split(heldout2_path, "heldout")
    return [("dev", dev), ("heldout", ho), ("heldout2", ho2)]


def load_model_and_lens(device="cuda"):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import jlens
    from jlens import JacobianLens
    tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)
    if hasattr(tok, "add_bos_token"):
        tok.add_bos_token = True
    try:
        hf = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REV,
                                                  dtype=torch.bfloat16)
    except TypeError:
        hf = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REV,
                                                  torch_dtype=torch.bfloat16)
    hf.to(device).eval()
    for p in hf.parameters():
        p.requires_grad_(False)
    lm = jlens.from_hf(hf, tok)
    lens = JacobianLens.from_pretrained(LENS_REPO, filename=LENS_FILE,
                                        revision=LENS_REV)
    return tok, hf, lm, lens


def anchored_positions(tok, prompt, input_ids):
    """Verbatim from experiments/stage3/heldout_frozen.py."""
    align = resolve_positions(tok, prompt, input_ids)
    qmark = None
    qc = prompt.rfind("?")
    if qc >= 0:
        enc = tok(prompt, return_offsets_mapping=True, add_special_tokens=False)
        for i, (a, b) in enumerate(enc["offset_mapping"]):
            if a <= qc < b:
                qmark = i + align["bos_offset"]
                break
    relcomp = qmark - 1 if qmark is not None and qmark >= 1 else None
    pos = {"prequery": align["prequery_idx"], "relcomp": relcomp,
           "qmark": qmark, "final": align["final_idx"]}
    ids = input_ids[0].tolist()
    toks = {k: (tok.convert_ids_to_tokens(ids[p]) if p is not None else None)
            for k, p in pos.items()}
    return pos, toks, align


def _tok_at_char(offsets, c, bos_offset):
    for i, (a, b) in enumerate(offsets):
        if a <= c < b:
            return i + bos_offset
    return None


def fact_positions(tok, prompt, rec, input_ids, bos_offset):
    """Token index of person / city / period in each person->place sentence.

    Verified: the token at each index must decode (stripped) to the expected
    word or to '.', else that position is None and counted as a failure.
    """
    t = TEMPLATES[rec["template_id"]]
    ids = input_ids[0].tolist()
    enc = tok(prompt, return_offsets_mapping=True, add_special_tokens=False)
    offsets = enc["offset_mapping"]
    out, toks, fails = {}, {}, []
    for role, person, city in (("q", rec["person_q"], rec["intermediate"]),
                               ("d", rec["person_d"], rec["alt_intermediate"])):
        sent = t.person_rel.format(p=person, place=city)
        start = prompt.find(sent)
        if start < 0 or prompt.find(sent, start + 1) >= 0:
            fails.append(f"{role}:sentence-not-unique")
            for k in ("person", "city", "period"):
                out[f"{k}_{role}"] = None
                toks[f"{k}_{role}"] = None
            continue
        chars = {"person": start,
                 "city": start + sent.index(city),
                 "period": start + len(sent) - 1}
        want = {"person": person, "city": city, "period": "."}
        for k, c in chars.items():
            idx = _tok_at_char(offsets, c, bos_offset)
            s = tok.convert_ids_to_tokens(ids[idx]) if idx is not None else None
            clean = (s or "").replace("Ġ", "").replace("▁", "").strip()
            if idx is None or clean != want[k]:
                fails.append(f"{k}_{role}:{s!r}!={want[k]!r}")
                idx = None
            out[f"{k}_{role}"] = idx
            toks[f"{k}_{role}"] = s
    return out, toks, fails


def person_ids(tok, rec):
    return (tt.single_token_id(tok, rec["person_q"]),
            tt.single_token_id(tok, rec["person_d"]))


def targets_for(rec, pid_q, pid_d):
    """Two-way (correct, alternative) token-id pairs per position family.

    Query positions: CITY target = (intermediate, alt_intermediate), exactly
    the application's "intermediate" target; ANSWER = (answer, alt_answer).
    Fact tokens, sentence role q: PERSON = (person_q, person_d), CITY =
    (intermediate, alt_intermediate); role d: PERSON = (person_d, person_q),
    CITY = (alt_intermediate, intermediate). "Correct" = the entity actually
    stated in that sentence.
    """
    return {
        "q": {"PERSON": (pid_q, pid_d),
              "CITY": (rec["intermediate_id"], rec["alt_intermediate_id"])},
        "d": {"PERSON": (pid_d, pid_q),
              "CITY": (rec["alt_intermediate_id"], rec["intermediate_id"])},
        "query": {"CITY": (rec["intermediate_id"], rec["alt_intermediate_id"]),
                  "ANSWER": (rec["answer_id"], rec["alt_answer_id"])},
    }


# which target(s) are read at each fact position (the pre-registered design)
FACT_TARGETS = {"person": ["CITY"], "city": ["PERSON"], "period": ["PERSON", "CITY"]}


def two_way(row, good, bad):
    return {"rank_correct": ranks_of(row, good), "rank_incorrect": ranks_of(row, bad),
            "margin": float(row[good] - row[bad])}


def frac_and_median(rows_scores):
    """rows_scores: list of two_way dicts."""
    if not rows_scores:
        return None
    n = len(rows_scores)
    frac = sum(s["rank_correct"] < s["rank_incorrect"] for s in rows_scores) / n
    ranks = sorted(s["rank_correct"] for s in rows_scores)
    return {"n": n, "frac": round(frac, 4), "median_rank": ranks[n // 2],
            "mean_margin": round(sum(s["margin"] for s in rows_scores) / n, 4)}
