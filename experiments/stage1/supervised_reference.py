"""Stage 1, arm 3 -- supervised difference-in-means reference (DEV SPLIT ONLY).

METHOD EVALUATION using a narrow task as instrument; not circuit discovery.

Section 2.5 of the write-up declares this arm NOT OPTIONAL, and gives the
reason: a two-arm comparison is uninterpretable in either direction. If J-Lens
beats the logit lens that may only say the logit lens does not work on
Qwen3.5; if BOTH sit at floor, "J-Lens cannot read binding" and "binding is not
linearly present in this residual at all" produce identical numbers. This arm
is the cheapest instrument that separates them, and without it a floor result
from `passive_readout.py` cannot be interpreted at all.

It is a REFERENCE LEVEL, not a ceiling, and it is biased in both directions:
it UNDER-estimates linear availability, because class means from ten pairs are
weaker than a probe fit on more data; and it OVER-states what any unsupervised
readout should reach, because it is handed the labels. Its only job is to
answer "is the binding linearly present here at all".

  If arm 3 is near floor  -> the conclusion is about the model or the layer,
                             NOT about J-Lens.
  If arm 3 is high and both lenses floor -> the conclusion is about the readouts.

Nearest-centroid (isotropic-covariance LDA) over the closed set V of
intermediate tokens, exactly as pre-registered:

    x     = h - h_bar
    score(h, v) = <x, mu_v> - 0.5 * <mu_v, mu_v>
    margin = score(h, correct) - score(h, alternative)

The -0.5*||mu_v||^2 term is what makes this a decision rule rather than a raw
projection; without it the arm would favour whichever intermediate happens to
have the larger centroid norm.

Residuals are captured with jlens's own ActivationRecorder DURING the same
lens.apply() call the other arms use, so the layer indexing and the token
positions are identical by construction rather than by assumption.

Leave-one-PAIR-out is reported alongside the in-sample fit. With ten pairs the
in-sample number is close to meaningless on its own; the LOO number is the one
to read, and both are printed so the gap is visible.

Every number this script emits is `agent-unverified`.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import jlens
from jlens import JacobianLens
from jlens.hooks import ActivationRecorder
from runlog import start_run

sys.path.insert(0, str(Path(__file__).resolve().parent))
from passive_readout import (MODEL_ID, MODEL_REV, LENS_REPO, LENS_REV,  # noqa: E402
                             LENS_FILE, resolve_positions)


def fit_centroids(items):
    """items: list of (label, vector). Returns (h_bar, {label: mu}, counts)."""
    X = torch.stack([v for _, v in items])
    h_bar = X.mean(dim=0)
    Xc = X - h_bar
    sums, counts = defaultdict(lambda: None), defaultdict(int)
    for (label, _), row in zip(items, Xc):
        sums[label] = row.clone() if sums[label] is None else sums[label] + row
        counts[label] += 1
    mu = {k: sums[k] / counts[k] for k in sums}
    return h_bar, mu, dict(counts)


def margin_of(h, h_bar, mu, correct, alt):
    """Nearest-centroid margin. None if either class was never seen in the fit."""
    if correct not in mu or alt not in mu:
        return None
    x = h - h_bar
    sc = lambda v: float(x @ mu[v] - 0.5 * (mu[v] @ mu[v]))
    return sc(correct) - sc(alt)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="results/datasets/dev.jsonl")
    ap.add_argument("--seed", type=int, default=20260827)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--max-records", type=int, default=0)
    args = ap.parse_args()

    run = start_run("stage1-supervised-reference", seed=args.seed,
                    dataset=args.dataset, model_repo=MODEL_ID,
                    model_revision=MODEL_REV, lens_repo=LENS_REPO,
                    lens_revision=LENS_REV, split="dev",
                    arm="supervised difference-in-means reference (arm 3)",
                    note="reference level, not a ceiling; biased both ways")

    rows = [json.loads(l) for l in Path(args.dataset).read_text().splitlines()]
    meta = next((r for r in rows if r.get("_meta")), {})
    recs = [r for r in rows if not r.get("_meta")]
    if meta.get("split") != "dev":
        print(f"REFUSING: split is {meta.get('split')!r}, not 'dev'.", flush=True)
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
    layers = [int(l) for l in lens.source_layers]
    print(f"[arm3] {lens!r}  model_load={load_s:.1f}s  n_records={len(recs)}",
          flush=True)

    # ------------------------------------------------- capture residuals once
    t_cap = time.time()
    captured = []          # one dict per record
    for i, r in enumerate(recs):
        with ActivationRecorder(lm.layers, at=layers) as rec:
            with torch.no_grad():
                _, _, input_ids = lens.apply(lm, r["prompt"], positions=[-1],
                                             use_jacobian=True)
        align = resolve_positions(tok, r["prompt"], input_ids)
        pos = {"final": align["final_idx"], "prequery": align["prequery_idx"]}
        H = {}
        for l in layers:
            act = rec.activations[l][0].detach().float().cpu()
            H[l] = {k: (act[p].clone() if p is not None else None)
                    for k, p in pos.items()}
        captured.append({"rec": r, "align": align, "H": H})
        if i == 0:
            print(f"[arm3] positions -> final={align['final_idx']} "
                  f"prequery={align['prequery_idx']} "
                  f"aligned={align['alignment_ok']}", flush=True)
    cap_s = time.time() - t_cap

    # ------------------------------------------------------------ fit + score
    def evaluate(train_idx, test_idx, layer, position):
        items = [(captured[i]["rec"]["intermediate_id"],
                  captured[i]["H"][layer][position]) for i in train_idx
                 if captured[i]["H"][layer][position] is not None]
        if len(items) < 2:
            return []
        h_bar, mu, counts = fit_centroids(items)
        out = []
        for i in test_idx:
            h = captured[i]["H"][layer][position]
            base = {"record_id": captured[i]["rec"]["record_id"],
                    "pair_id": captured[i]["rec"]["pair_id"]}
            if h is None:
                # No activation at this position -- resolve_positions found no
                # index. Recorded as unscorable WITH a reason rather than
                # dropped, so `n` stays comparable between final and prequery.
                out.append({**base, "margin": None, "scored": False,
                            "success": None, "reason": "no_position"})
                continue
            m = margin_of(h, h_bar, mu, captured[i]["rec"]["intermediate_id"],
                          captured[i]["rec"]["alt_intermediate_id"])
            out.append({**base, "margin": m, "scored": m is not None,
                        "success": None if m is None else bool(m > 0),
                        "reason": None if m is not None else "class_unseen_in_fit"})
        return out

    pair_ids = sorted({c["rec"]["pair_id"] for c in captured})
    by_pair = {p: [i for i, c in enumerate(captured) if c["rec"]["pair_id"] == p]
               for p in pair_ids}
    all_idx = list(range(len(captured)))

    def summarise(scores):
        scored = [s for s in scores if s["scored"]]
        if not scored:
            return {"n": 0, "n_unscorable": len(scores),
                    "unscorable_reasons": {s["reason"]: 1 for s in scores},
                    "mean_margin": None, "success_rate": None}
        reasons = {}
        for s in scores:
            if not s["scored"]:
                reasons[s["reason"]] = reasons.get(s["reason"], 0) + 1
        return {
            "n": len(scored),
            "n_unscorable": len(scores) - len(scored),
            "unscorable_reasons": reasons,
            "mean_margin": sum(s["margin"] for s in scored) / len(scored),
            "success_rate": sum(s["success"] for s in scored) / len(scored),
        }

    results = {}
    for position in ("final", "prequery"):
        per_layer = {}
        for l in layers:
            in_sample = evaluate(all_idx, all_idx, l, position)
            loo = []
            for p in pair_ids:                    # leave one PAIR out, not one row
                held = by_pair[p]
                train = [i for i in all_idx if i not in held]
                loo.extend(evaluate(train, held, l, position))
            per_layer[l] = {"in_sample": summarise(in_sample),
                            "leave_one_pair_out": summarise(loo)}
        usable = {l: v for l, v in per_layer.items()
                  if v["leave_one_pair_out"]["mean_margin"] is not None}
        if not usable:
            results[position] = {"per_layer": per_layer, "selected_layer": None,
                                 "note": "no layer produced a scorable LOO fit"}
            continue
        best = max(usable, key=lambda l:
                   usable[l]["leave_one_pair_out"]["mean_margin"])
        results[position] = {
            "per_layer": per_layer,
            "selected_layer": best,
            "selection_rule": "argmax mean leave-one-pair-out margin on dev; "
                              "selected on LOO, not in-sample, on purpose",
            "at_selected_layer": per_layer[best],
        }

    # Persist the fitted parameters. Section 2.5 says h_bar and mu are
    # estimated on development prompts and applied UNCHANGED to held-out. If
    # they are only ever computed inside evaluate() and thrown away, that
    # promise cannot be checked by a reader and any drift in the capture path
    # between now and then would change them silently.
    fitted = {}
    for position in ("final", "prequery"):
        sel = results[position].get("selected_layer")
        if sel is None:
            continue
        items = [(c["rec"]["intermediate_id"], c["H"][sel][position])
                 for c in captured if c["H"][sel][position] is not None]
        if len(items) < 2:
            continue
        h_bar, mu, counts = fit_centroids(items)
        fitted[position] = {"layer": sel, "h_bar": h_bar,
                            "mu": mu, "counts": counts,
                            "fitted_on": "dev, all records, no holdout"}
    if fitted:
        torch.save(fitted, run.outputs / "centroids-dev.pt")

    counts_example = None
    for l in layers[:1]:
        items = [(c["rec"]["intermediate_id"], c["H"][l]["final"])
                 for c in captured if c["H"][l]["final"] is not None]
        if items:
            _, _, counts_example = fit_centroids(items)

    payload = {
        "status": "agent-unverified",
        "stage": "1", "arm": "3 -- supervised difference-in-means reference",
        "claim_type": "method-claim, REFERENCE LEVEL not a ceiling; biased "
                      "downward (ten pairs of class means) and upward (given "
                      "the labels)",
        "framing": "method evaluation using a narrow task as instrument; "
                   "not circuit discovery",
        "interpretation_rule": {
            "arm3_at_floor": "the conclusion is about the model or the layer, "
                             "not about J-Lens",
            "arm3_high_lenses_at_floor": "the conclusion is about the readouts",
        },
        "split": "dev", "n_records": len(recs), "n_pairs": len(pair_ids),
        "dataset": args.dataset, "dataset_seed": meta.get("seed"),
        "model": MODEL_ID, "model_revision": MODEL_REV,
        "lens_repo": LENS_REPO, "lens_revision": LENS_REV,
        "source_layers": layers,
        "class_counts_layer0_final": {str(k): v for k, v
                                      in (counts_example or {}).items()},
        "thin_class_warning": "with ten pairs each intermediate centroid is "
                              "estimated from very few examples; read the "
                              "leave-one-pair-out number, not the in-sample one",
        "seconds": {"model_load": round(load_s, 2),
                    "capture": round(cap_s, 2)},
        "fitted_parameters_file": ("outputs/centroids-dev.pt" if fitted
                                   else None),
        "fitted_parameters_note": "h_bar and mu at the selected layer, fitted "
                                  "on all dev records. Held-out scoring must "
                                  "LOAD these, not refit.",
        "results": results,
    }
    out = run.outputs / "stage1-supervised-reference.json"
    out.write_text(json.dumps(payload, indent=2))

    print("\n" + "=" * 62)
    for position in ("final", "prequery"):
        r = results[position]
        if r.get("selected_layer") is None:
            print(f"  arm3 {position:9s}  NO SCORABLE FIT")
            continue
        a = r["at_selected_layer"]
        print(f"  arm3 {position:9s} L{r['selected_layer']:<3d} "
              f"LOO margin={a['leave_one_pair_out']['mean_margin']:+.3f} "
              f"LOO acc={a['leave_one_pair_out']['success_rate']:.3f} "
              f"(in-sample acc={a['in_sample']['success_rate']:.3f})")
    print("=" * 62)
    print(f"wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
