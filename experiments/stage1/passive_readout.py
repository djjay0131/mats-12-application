"""Stage 1 -- passive J-Lens readout on role-swapped pairs (DEV SPLIT ONLY).

METHOD EVALUATION using a narrow task as instrument; not circuit discovery.

The question is whether J-Lens identifies the CORRECT hidden intermediate when
two prompts contain the same entities with their relational roles swapped. The
task is the instrument; the method is the object of study.

Two readout positions, collected in the same forward pass because the contrast
between them is the whole point:

  FINAL      the last prompt token, after the query has selected a subject.
             Success here licenses only the WEAK claim: the selected
             intermediate is readable.
  PREQUERY   the last token of the facts block, before the query is stated.
             Success here would license the STRONG claim: the stored binding
             itself is readable. We do not expect it.

Reporting the weak result without the strong control is how a post-selection
readout gets sold as graph reading. Both are collected; both are reported.

Two negative controls, both through the identical code path:

  LABEL PERMUTATION        score each record against a DIFFERENT pair's
                           intermediate (a derangement, fixed seed). If the
                           margin survives this, it is not about the binding.
  NORM-MATCHED RANDOM      replace every J_l with a Gaussian matrix of matched
  TRANSPORT                Frobenius norm and re-run. If the margin survives
                           this, it is not about the Jacobian.

Blocker B3: no shuffled-corpus control lens is published (all 40+ released
lenses are fit on Salesforce/wikitext), so these two are the declared fallback.

Blocker B4: len(tokenizer)=248077 but the unembedding is 248320 wide. All ranks
are computed over the FULL unembedding width and that width is recorded.

PRE-REGISTERED LAYER SELECTION RULE. The reported layer is the one maximising
the mean paired intermediate margin ON THE DEV SPLIT. It is chosen here, on
these 10 pairs, and then frozen. The held-out split is not read by this script
and must be evaluated at the frozen layer. There is no fixed 40-80% band: the
V1 coverage control already put the optimum at layer 30, the LAST fitted source
layer, so a band chosen by convention would have been wrong.

Every number this script emits is `agent-unverified`.
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import jlens
from jlens import JacobianLens
from runlog import start_run

MODEL_ID = "Qwen/Qwen3.5-4B"
MODEL_REV = "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a"
LENS_REPO = "neuronpedia/jacobian-lens"
LENS_REV = "qwen-n1000"
LENS_FILE = "qwen3.5-4b/jlens/Salesforce-wikitext/Qwen3.5-4B_jacobian_lens_n1000.pt"


# ---------------------------------------------------------------- utilities

def ranks_of(logits: torch.Tensor, token_id: int) -> int:
    """Rank of token_id in a 1-D logit vector; 0 = argmax. Full-width (B4)."""
    return int((logits > logits[token_id]).sum().item())


def prequery_char_cut(prompt: str) -> int | None:
    """Character index just past the final fact, before the query sentence.

    The templates end the facts block with '. ' and then state a question. We
    locate the last '. ' preceding the final '?'. Returned as a char offset so
    the token index can be derived from the tokenizer's offset mapping rather
    than from an assumption that prefix tokenization is a prefix of full
    tokenization -- which for a BPE tokenizer is not guaranteed.
    """
    q = prompt.rfind("?")
    if q < 0:
        return None
    cut = prompt.rfind(". ", 0, q)
    if cut < 0:
        return None
    return cut + 1          # include the period itself


def resolve_positions(tok, prompt, input_ids):
    """Map the pre-query char cut to a token index in apply()'s own input_ids.

    Verified, not assumed: we re-tokenize with offset mapping, align against
    the ids apply() actually used (which may carry a forced BOS), and record
    whether the alignment held. A failed alignment is reported, not silently
    patched.
    """
    ids = input_ids[0].tolist()
    enc = tok(prompt, return_offsets_mapping=True, add_special_tokens=False)
    own = enc["input_ids"]
    offsets = enc["offset_mapping"]

    offset = 0
    aligned = ids == own
    if not aligned and len(ids) == len(own) + 1 and ids[1:] == own:
        offset, aligned = 1, True          # apply() forced a BOS

    cut = prequery_char_cut(prompt)
    pre_local = None
    if cut is not None:
        for i, (_, end) in enumerate(offsets):
            if end <= cut:
                pre_local = i
    pre_idx = None if pre_local is None else pre_local + offset

    return {
        "n_tokens": len(ids),
        "alignment_ok": bool(aligned),
        "bos_offset": offset,
        "final_idx": len(ids) - 1,
        "prequery_idx": pre_idx,
        "prequery_char_cut": cut,
        "prequery_token_str": (tok.convert_ids_to_tokens(ids[pre_idx])
                               if pre_idx is not None else None),
        "prequery_context": (tok.decode(ids[max(0, pre_idx - 6):pre_idx + 1])
                             if pre_idx is not None else None),
        "final_token_str": tok.convert_ids_to_tokens(ids[-1]),
    }


def score_positions(lens_logits, pos_order, targets):
    """Per-layer ranks and continuous margins for every target at every position.

    The margin is the primary metric and it is paired and continuous:
        margin = logit[correct] - logit[incorrect]
    on the SAME forward pass, so per-prompt scale cancels. Ranks are reported
    alongside because a rank is interpretable and a logit difference is not.
    """
    out = {}
    for pname, pidx in pos_order.items():
        if pidx is None:
            out[pname] = None
            continue
        per_layer = {}
        for layer, v in lens_logits.items():
            row = v[pidx]
            rec = {}
            for label, (good, bad) in targets.items():
                rec[label] = {
                    "rank_correct": ranks_of(row, good),
                    "rank_incorrect": ranks_of(row, bad),
                    "margin": float(row[good] - row[bad]),
                }
            per_layer[int(layer)] = rec
        out[pname] = per_layer
    return out


def randomize_lens(lens, seed):
    """Return the original jacobians and install norm-matched random ones."""
    g = torch.Generator(device="cpu").manual_seed(seed)
    original = lens.jacobians
    randomized = {}
    for layer, J in original.items():
        R = torch.randn(J.shape, generator=g).to(J.dtype)
        R = R * (J.norm() / R.norm())
        randomized[layer] = R
    lens.jacobians = randomized
    return original


def derangement(n, seed):
    """A permutation with no fixed point, so no record keeps its own labels."""
    rng = random.Random(seed)
    idx = list(range(n))
    for _ in range(1000):
        rng.shuffle(idx)
        if all(i != j for i, j in enumerate(idx)):
            return idx
    raise RuntimeError("no derangement found")


# -------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="results/datasets/dev.jsonl")
    ap.add_argument("--seed", type=int, default=20260827)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--max-records", type=int, default=0)
    args = ap.parse_args()

    run = start_run("stage1-passive-readout", seed=args.seed,
                    dataset=args.dataset, model_repo=MODEL_ID,
                    model_revision=MODEL_REV, lens_repo=LENS_REPO,
                    lens_revision=LENS_REV, lens_file=LENS_FILE,
                    split="dev", note="held-out split not read by this script")

    rows = [json.loads(l) for l in Path(args.dataset).read_text().splitlines()]
    meta = next((r for r in rows if r.get("_meta")), {})
    recs = [r for r in rows if not r.get("_meta")]
    if meta.get("split") != "dev":
        print(f"REFUSING: dataset split is {meta.get('split')!r}, not 'dev'. "
              f"The layer-selection rule is not yet frozen; the held-out split "
              f"must not be touched.", flush=True)
        return 2
    if args.max_records:
        recs = recs[:args.max_records]

    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)
    if hasattr(tok, "add_bos_token"):
        tok.add_bos_token = True
    try:
        hf = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REV,
                                                  dtype=torch.bfloat16)
    except TypeError:
        hf = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REV,
                                                  torch_dtype=torch.bfloat16)
    hf.to(args.device).eval()
    load_s = time.time() - t0

    lm = jlens.from_hf(hf, tok)
    lens = JacobianLens.from_pretrained(LENS_REPO, filename=LENS_FILE,
                                        revision=LENS_REV)
    print(f"[stage1] {lens!r}  model_load={load_s:.1f}s  n_records={len(recs)}",
          flush=True)

    perm = derangement(len(recs), args.seed)
    VOCAB_W = None          # B4: recorded from the actual logit width, not len(tok)

    arms = [("jlens", True, False), ("logitlens", False, False),
            ("jlens_random_transport", True, True)]

    results = []
    t_apply = time.time()
    for arm_name, use_j, randomize in arms:
        saved = randomize_lens(lens, args.seed) if randomize else None
        try:
            for i, r in enumerate(recs):
                prompt = r["prompt"]
                # One apply() per record with BOTH positions requested, so the
                # two readouts come from the same forward pass by construction.
                probe_ll, model_logits, input_ids = lens.apply(
                    lm, prompt, positions=[-1], use_jacobian=use_j)
                align = resolve_positions(tok, prompt, input_ids)
                pos_order = {"final": align["final_idx"],
                             "prequery": align["prequery_idx"]}
                want = [p for p in pos_order.values() if p is not None]
                lens_logits, _, _ = lens.apply(
                    lm, prompt, positions=want, use_jacobian=use_j)
                lookup = {p: k for k, p in enumerate(want)}
                pos_slots = {k: (lookup[p] if p is not None else None)
                             for k, p in pos_order.items()}

                other = recs[perm[i]]
                targets = {
                    "intermediate": (r["intermediate_id"],
                                     r["alt_intermediate_id"]),
                    "answer": (r["answer_id"], r["alt_answer_id"]),
                    "control_label_permutation": (other["intermediate_id"],
                                                  other["alt_intermediate_id"]),
                }
                if VOCAB_W is None:
                    VOCAB_W = int(next(iter(lens_logits.values())).shape[-1])
                # The model's OWN distribution at the readout position, kept
                # rather than discarded. Without it, comparing where the readout
                # succeeds against where the MODEL succeeds needs a join across
                # two separately generated stimulus sets -- which, when tried,
                # overlapped on 4 of 40 records and produced zero discriminating
                # cases. See results/design-verification/xref-readout-vs-behaviour.md
                beh = None
                if model_logits is not None:
                    row = model_logits[0][-1].float()
                    beh = {
                        "answer_margin": float(row[r["answer_id"]]
                                               - row[r["alt_answer_id"]]),
                        "intermediate_margin": float(row[r["intermediate_id"]]
                                                     - row[r["alt_intermediate_id"]]),
                        "rank_answer": ranks_of(row, r["answer_id"]),
                        "argmax_is_answer": bool(int(row.argmax()) == r["answer_id"]),
                    }
                scored = score_positions(lens_logits, pos_slots, targets)
                results.append({
                    "arm": arm_name, "record_id": r["record_id"],
                    "pair_id": r["pair_id"], "cell": r["cell"],
                    "template_id": r["template_id"],
                    "permuted_from": other["record_id"],
                    "alignment": align, "scores": scored,
                    "model_behaviour": beh,
                })
                if i == 0 and arm_name == "jlens":
                    print(f"[stage1] positions -> final={align['final_idx']} "
                          f"({align['final_token_str']!r})  "
                          f"prequery={align['prequery_idx']} "
                          f"({align['prequery_token_str']!r})  "
                          f"aligned={align['alignment_ok']}", flush=True)
        finally:
            if saved is not None:
                lens.jacobians = saved
    apply_s = time.time() - t_apply

    # ------------------------------------------------- aggregate, dev-split
    def mean(xs):
        xs = list(xs)
        return sum(xs) / len(xs) if xs else None

    layers = sorted({int(l) for r in results
                     for p in r["scores"].values() if p
                     for l in p})
    summary = {}
    for arm_name, _, _ in arms:
        arm_rows = [r for r in results if r["arm"] == arm_name]
        summary[arm_name] = {}
        for pos in ("final", "prequery"):
            per_layer = {}
            for l in layers:
                cells = [r["scores"][pos][l] for r in arm_rows
                         if r["scores"].get(pos)]
                if not cells:
                    continue
                per_layer[l] = {
                    "mean_margin_intermediate":
                        mean(c["intermediate"]["margin"] for c in cells),
                    "mean_margin_answer":
                        mean(c["answer"]["margin"] for c in cells),
                    "mean_margin_control_permuted":
                        mean(c["control_label_permutation"]["margin"]
                             for c in cells),
                    "frac_correct_outranks_incorrect":
                        mean(float(c["intermediate"]["rank_correct"]
                                   < c["intermediate"]["rank_incorrect"])
                             for c in cells),
                    "median_rank_correct_intermediate":
                        sorted(c["intermediate"]["rank_correct"]
                               for c in cells)[len(cells) // 2],
                    "n": len(cells),
                }
            if not per_layer:
                summary[arm_name][pos] = None
                continue
            best = max(per_layer, key=lambda l:
                       per_layer[l]["mean_margin_intermediate"])
            summary[arm_name][pos] = {
                "per_layer": per_layer,
                "selected_layer": best,
                "selection_rule": "argmax mean paired intermediate margin on "
                                  "the DEV split; frozen for held-out",
                "at_selected_layer": per_layer[best],
            }

    payload = {
        "status": "agent-unverified",
        "stage": "1",
        "framing": "method evaluation using a narrow task as instrument; "
                   "not circuit discovery",
        "claim_type": {
            "final": "method-claim, WEAK -- the SELECTED intermediate is "
                     "readable; this is not evidence that stored bindings are "
                     "readable",
            "prequery": "method-claim, STRONG -- stored binding readable "
                        "before the query selects a subject",
        },
        "split": "dev", "n_records": len(recs), "n_pairs": meta.get("n_pairs"),
        "dataset": args.dataset, "dataset_seed": meta.get("seed"),
        "model": MODEL_ID, "model_revision": MODEL_REV,
        "lens_repo": LENS_REPO, "lens_revision": LENS_REV,
        "unembedding_width": VOCAB_W,
        "source_layers": [int(l) for l in lens.source_layers],
        "seconds": {"model_load": round(load_s, 2),
                    "readout": round(apply_s, 2)},
        "controls": {
            "label_permutation": "derangement, seed "
                                 f"{args.seed}; no record keeps its own labels",
            "norm_matched_random_transport": "every J_l replaced by a Gaussian "
                                             "of matched Frobenius norm, "
                                             "identical code path",
            "published_shuffled_lens_available": False,
            "b3_note": "no shuffled-corpus lens is published; the two above "
                       "are the declared fallback",
        },
        "summary": summary,
        "records": results,
    }
    out = run.outputs / "stage1-passive-readout.json"
    out.write_text(json.dumps(payload, indent=2))

    print("\n" + "=" * 62)
    for arm_name, _, _ in arms:
        for pos in ("final", "prequery"):
            s = summary[arm_name][pos]
            if not s:
                print(f"  {arm_name:24s} {pos:9s}  NO DATA")
                continue
            a = s["at_selected_layer"]
            print(f"  {arm_name:24s} {pos:9s} L{s['selected_layer']:<3d} "
                  f"margin={a['mean_margin_intermediate']:+.3f} "
                  f"ctrl={a['mean_margin_control_permuted']:+.3f} "
                  f"frac={a['frac_correct_outranks_incorrect']:.3f} "
                  f"medrank={a['median_rank_correct_intermediate']}")
    print("=" * 62)
    print(f"wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
