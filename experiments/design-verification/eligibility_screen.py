"""Behavioural eligibility screen -- the cheapest kill-shot in the project.

METHOD EVALUATION, not circuit discovery: this measures only whether the
unmodified model can perform the two-hop task at all. Nothing here touches
J-Lens. If the model cannot solve both variants of a pair, the binding metric
the design defines has nothing to attach to, and the design must change before
any lens work is worth running.

Pre-registered thresholds (fixed before execution):
    PASS      >= 80% of pairs with BOTH bindings answered correctly
    MARGINAL  60-80%  -> report and propose a fix
    STOP      <  60%  -> halt; the design needs changing

Note the arithmetic: pair eligibility is a CONJUNCTION over the two bindings,
so an 80% pair rate demands roughly 90% per-variant accuracy. The bar is
stricter than it reads.

Six cells are measured in one pass rather than iterating on one:
    lexicon in {real, rare, pseudo}   x   shot in {zero, few}
so the named fallbacks are measured up front instead of being selected after
seeing a bad number. Within each cell every pair carries all four
(binding, fact_order) variants, so fact-order sensitivity is measured too --
if eligibility depends on the queried person's fact coming first, that is a
positional confound we need to know about before, not after.

Every number this script emits is `agent-unverified`.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from runlog import start_run
from task_templates import (
    FACT_ORDERS, LEXICONS, TEMPLATES, assert_left_padding, audit_lexicon,
    build_pairs, single_token_id, verify_pair_tokenization,
)

MODEL_ID = "Qwen/Qwen3.5-4B"
MODEL_REV = "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a"
WORD_RE = re.compile(r"[A-Za-z]+")


THINK_CLOSE = "</think>"


def first_word(text: str) -> str:
    """First alphabetic word of the ANSWER.

    Qwen3.5 is a hybrid-thinking model and will open a <think> block on
    zero-shot raw-completion prompts. Everything up to and including the
    closing tag is reasoning, not the answer, so it is skipped. A model that
    thinks and then answers correctly is scored correct.
    """
    if THINK_CLOSE in text:
        text = text.split(THINK_CLOSE)[-1]
    m = WORD_RE.search(text)
    return m.group(0).lower() if m else ""


BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


def answer_span(text: str) -> str:
    """The model's own final answer, as best it can be located.

    Zero-shot this model answers verbosely and puts its conclusion in the
    LAST bolded span. Fall back to the last alphabetic word.
    """
    if THINK_CLOSE in text:
        text = text.split(THINK_CLOSE)[-1]
    bolds = BOLD_RE.findall(text)
    if bolds:
        m = WORD_RE.search(bolds[-1])
        if m:
            return m.group(0).lower()
    words = WORD_RE.findall(text)
    return words[-1].lower() if words else ""


def score_generation(text: str, answer: str, alt: str) -> dict:
    """Score by CONTENT, not by position.

    The behavioural question is whether the model resolved the binding, not
    whether its answer happened to land in the first token slot.
    """
    body = text.split(THINK_CLOSE)[-1] if THINK_CLOSE in text else text
    low = body.lower()
    a, b = answer.lower(), alt.lower()
    present, alt_present = a in low, b in low
    return {
        # Primary: names the correct object and not the paired alternative.
        # Robust to verbosity, which the first-word rule was not.
        "correct": present and not alt_present,
        "answer_present": present,
        "alt_present": alt_present,
        "strict": answer_span(text) == a,
        "first_word": first_word(text) == a,
        # The informative error: read the concepts, bound them wrongly.
        "chose_alternative": alt_present and not present,
    }


def load(device: str):
    tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)
    # jlens's HFLensModel uses force_bos=True; match it so the behavioural
    # screen and the later lens readouts see the same input ids.
    if hasattr(tok, "add_bos_token"):
        tok.add_bos_token = True
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    # The observation point is the FINAL prompt token. Right-padding would
    # silently read a pad token and nothing would error.
    tok.padding_side = "left"
    assert_left_padding(tok)
    try:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID, revision=MODEL_REV, dtype=torch.bfloat16)
    except TypeError:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID, revision=MODEL_REV, torch_dtype=torch.bfloat16)
    return tok, model.to(device).eval()


@torch.no_grad()
def generate(tok, model, prompts, *, max_new_tokens=96, batch_size=1,
             device="cuda"):
    out = []
    for i in range(0, len(prompts), batch_size):
        enc = tok(prompts[i:i + batch_size], return_tensors="pt",
                  padding=True).to(device)
        gen = model.generate(**enc, max_new_tokens=max_new_tokens,
                             do_sample=False, num_beams=1,
                             pad_token_id=tok.pad_token_id)
        for row in gen[:, enc["input_ids"].shape[1]:]:
            ids = row.tolist()
            out.append({"text": tok.decode(ids, skip_special_tokens=True),
                        "first_id": ids[0] if ids else -1})
    return out


def padding_control(tok, model, prompts, device):
    """Batched (left-padded) vs unbatched must agree exactly.

    Cheap control for the single most likely silent bug in the pipeline.
    """
    s = prompts[:8]
    b = generate(tok, model, s, batch_size=8, device=device)
    u = generate(tok, model, s, batch_size=1, device=device)
    mism = [{"prompt": p, "batched": x["text"], "unbatched": y["text"]}
            for p, x, y in zip(s, b, u) if x["text"] != y["text"]]
    return {"n_checked": len(s), "n_mismatch": len(mism),
            "agree": not mism, "mismatches": mism}


def run_cell(tok, model, *, lexicon, shot, n_pairs, seed, device):
    pairs = build_pairs(tok, n_pairs=n_pairs, seed=seed, lexicon=lexicon,
                        shot=shot)
    for p in pairs:
        verify_pair_tokenization(tok, p)   # raises rather than warns

    flat = [(p, v) for p in pairs for v in p.variants]
    gens = generate(tok, model, [v.prompt for _, v in flat], device=device)

    per_variant = []
    for (p, v), g in zip(flat, gens):
        sc = score_generation(g["text"], v.answer, v.alt_answer)
        per_variant.append({
            "pair_id": p.pair_id, "template_id": p.template_id,
            "cell": v.cell, "variant": v.variant, "fact_order": v.fact_order,
            "prompt": v.prompt, "expected": v.answer, "alt": v.alt_answer,
            "generated": g["text"], "text_match": sc["correct"],
            "strict_match": sc["strict"], "first_word_match": sc["first_word"],
            "answer_present": sc["answer_present"], "alt_present": sc["alt_present"],
            "first_token_match": g["first_id"] == single_token_id(tok, v.answer),
            "chose_alternative": sc["chose_alternative"],
        })

    by_pair = defaultdict(dict)
    for r in per_variant:
        by_pair[r["pair_id"]][r["cell"]] = r["text_match"]

    tmpl = {r["pair_id"]: r["template_id"] for r in per_variant}
    elig, per_pair = {}, []
    for fo in FACT_ORDERS:
        elig[fo] = sum(c.get(f"A/{fo}") and c.get(f"B/{fo}")
                       for c in by_pair.values()) / len(by_pair)
    strict = sum(all(c.values()) for c in by_pair.values()) / len(by_pair)
    for pid, c in by_pair.items():
        per_pair.append({"pair_id": pid, "template_id": tmpl[pid],
                         "cells": c,
                         "both_AB": bool(c.get("A/AB") and c.get("B/AB")),
                         "both_BA": bool(c.get("A/BA") and c.get("B/BA")),
                         "all_four": all(c.values())})

    by_tmpl = defaultdict(list)
    for r in per_pair:
        by_tmpl[r["template_id"]].append(r["both_AB"])

    return {
        "lexicon": lexicon, "shot": shot, "n_pairs": len(by_pair),
        # Primary headline number: canonical fact order.
        "pair_eligibility_AB": elig["AB"],
        "pair_eligibility_BA": elig["BA"],
        "pair_eligibility_all_four": strict,
        "fact_order_gap": elig["AB"] - elig["BA"],
        "variant_accuracy": sum(r["text_match"] for r in per_variant) / len(per_variant),
        "alt_answer_rate": sum(r["chose_alternative"] for r in per_variant) / len(per_variant),
        # The confound that invalidated the first run. Kept as a reported
        # metric so it can never silently return.
        "think_mode_rate": sum("think" in r["generated"] for r in per_variant) / len(per_variant),
        # Report all three criteria. If they disagree sharply, the metric is
        # measuring the parser rather than the model -- which is exactly what
        # happened on the first two runs.
        "strict_accuracy": sum(r["strict_match"] for r in per_variant) / len(per_variant),
        "first_word_accuracy": sum(r["first_word_match"] for r in per_variant) / len(per_variant),
        "answer_present_rate": sum(r["answer_present"] for r in per_variant) / len(per_variant),
        "first_token_agreement": sum(
            r["text_match"] == r["first_token_match"] for r in per_variant
        ) / len(per_variant),
        "by_template_AB": {k: sum(v) / len(v) for k, v in sorted(by_tmpl.items())},
        "per_pair": per_pair, "per_variant": per_variant,
    }


def verdict(rate: float) -> str:
    return "PASS" if rate >= 0.80 else ("MARGINAL" if rate >= 0.60 else "STOP")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-pairs", type=int, default=30)
    ap.add_argument("--seed", type=int, default=20260827)
    ap.add_argument("--device", default="cuda")
    args = ap.parse_args()

    run = start_run("eligibility-screen", seed=args.seed,
                    n_pairs=args.n_pairs, model_repo=MODEL_ID,
                    model_revision=MODEL_REV,
                    thresholds={"pass": 0.80, "marginal_low": 0.60})

    tok, model = load(args.device)
    lex_audit = {name: audit_lexicon(tok, name) for name in LEXICONS}

    probe = build_pairs(tok, n_pairs=2, seed=args.seed, lexicon="real")
    ids = tok(probe[0].variants[0].prompt)["input_ids"]
    pad_ctl = padding_control(
        tok, model, [v.prompt for p in probe for v in p.variants], args.device)
    print(f"[padding control] batched==unbatched: {pad_ctl['agree']} "
          f"({pad_ctl['n_mismatch']}/{pad_ctl['n_checked']} mismatched)",
          flush=True)

    cells = []
    for lexicon in ("real", "rare", "pseudo"):
        for shot in ("zero", "few"):
            try:
                c = run_cell(tok, model, lexicon=lexicon, shot=shot,
                             n_pairs=args.n_pairs, seed=args.seed,
                             device=args.device)
            except Exception as e:                      # record, do not hide
                print(f"  {lexicon:6s} {shot:4s}  FAILED: {type(e).__name__}: {e}",
                      flush=True)
                cells.append({"lexicon": lexicon, "shot": shot,
                              "error": f"{type(e).__name__}: {e}"})
                continue
            cells.append(c)
            print(f"  {lexicon:6s} {shot:4s}  AB={c['pair_eligibility_AB']:.3f} "
                  f"BA={c['pair_eligibility_BA']:.3f} "
                  f"all4={c['pair_eligibility_all_four']:.3f} "
                  f"var={c['variant_accuracy']:.3f} "
                  f"alt={c['alt_answer_rate']:.3f}  [{verdict(c['pair_eligibility_AB'])}]",
                  flush=True)

    ok = [c for c in cells if "error" not in c]
    best = max(ok, key=lambda c: c["pair_eligibility_AB"], default=None)
    headline = next((c for c in ok if c["lexicon"] == "real"
                     and c["shot"] == "zero"), None)

    payload = {
        "status": "agent-unverified",
        "kind": "behavioural-eligibility-screen",
        "framing": "method evaluation using a narrow task as instrument; "
                   "not circuit discovery",
        "model": MODEL_ID, "model_revision": MODEL_REV,
        "seed": args.seed, "n_pairs_per_cell": args.n_pairs,
        "decoding": {"do_sample": False, "num_beams": 1, "max_new_tokens": 96, "batch_size": 1},
        "templates": [t.tid for t in TEMPLATES],
        "thresholds": {"pass": 0.80, "marginal_low": 0.60},
        "primary_metric": "pair_eligibility_AB (both bindings correct, "
                          "canonical fact order)",
        "lexicon_audit": lex_audit,
        "tokenization_note": {
            "example_prompt": probe[0].variants[0].prompt,
            "first_5_tokens": tok.convert_ids_to_tokens(ids[:5]),
            "n_tokens": len(ids),
            "bos_present": bool(ids and ids[0] == tok.bos_token_id),
            "padding_side": tok.padding_side,
            "len_tokenizer": len(tok),
        },
        "padding_control": pad_ctl,
        "cells": cells,
        "headline": None if headline is None else {
            "cell": "real/zero",
            "pair_eligibility_AB": headline["pair_eligibility_AB"],
            "verdict": verdict(headline["pair_eligibility_AB"]),
        },
        "best_cell": None if best is None else {
            "cell": f"{best['lexicon']}/{best['shot']}",
            "pair_eligibility_AB": best["pair_eligibility_AB"],
            "verdict": verdict(best["pair_eligibility_AB"]),
        },
        "peak_gpu_alloc_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2)
        if torch.cuda.is_available() else None,
    }
    with open(run.outputs / "eligibility-screen.json", "w") as f:
        json.dump(payload, f, indent=2)

    print("\n" + "=" * 62)
    if headline:
        print(f"HEADLINE  real/zero  pair_eligibility(AB) = "
              f"{headline['pair_eligibility_AB']:.1%}  -> "
              f"{verdict(headline['pair_eligibility_AB'])}")
    if best:
        print(f"BEST      {best['lexicon']}/{best['shot']}  = "
              f"{best['pair_eligibility_AB']:.1%}  -> "
              f"{verdict(best['pair_eligibility_AB'])}")
    print("=" * 62)
    print(f"wrote {run.outputs / 'eligibility-screen.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
