#!/usr/bin/env python3
"""Agent verification pass, part 2 (ARC, reads the saved residuals): an
INDEPENDENT re-fit of the step-5 probe result with different estimators and
a label-shuffle null, plus a re-derivation of arm 3 at the period from raw
residuals. Fresh code; does not import the experiment scripts. Read-only.
"""
import gzip, json, sys, time
import numpy as np, torch
from pathlib import Path
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import StandardScaler

RES = Path("/scratch/djjay/mats12/phase1/residuals")
S2 = Path("results/runs/20260917T202900Z-phase1-step2-fact-tokens/outputs/step2-records.json.gz")
POS = ["prequery", "relcomp", "qmark", "final", "person_q", "city_q", "period_q", "person_d", "city_d", "period_d"]
t0 = time.time()


def load(split):
    d = torch.load(RES / f"{split}.pt")
    assert d["positions"] == POS
    recs = {}
    for l in Path(f"results/datasets/{split}.jsonl").read_text().splitlines():
        if l.strip() and '"_meta"' not in l:
            r = json.loads(l); recs[r["record_id"]] = r
    return d["resid"], [recs[i] for i in d["record_ids"]]


with gzip.open(S2, "rt") as fh:
    sh = {(e["split"], e["record_id"]): e["shadow"] for e in json.load(fh)["shadow"]}
Xh, Rh = load("heldout"); X2, R2 = load("heldout2"); Xd, Rd = load("dev")
X = torch.cat([Xh, X2]); recs = Rh + R2; tags = ["heldout"] * len(Rh) + ["heldout2"] * len(R2)
pairs = np.array([r["pair_id"] for r in recs]); y = np.array([r["intermediate_id"] for r in recs])
alt = np.array([r["alt_intermediate_id"] for r in recs])
wrong = np.array([sh[(t, r["record_id"])]["relcomp"]["CITY"]["margin"] < 0 for t, r in zip(tags, recs)])
print(f"combined n={len(recs)} pairs={len(set(pairs))} model-wrong={wrong.sum()}  load {time.time()-t0:.0f}s")


def lopo(F, labels, alts, make, standardize=True):
    """two-way accuracy, leave-one-pair-out; returns per-record correct (bool) or nan if unscorable"""
    out = np.full(len(labels), np.nan)
    for p in sorted(set(pairs)):
        te = pairs == p; tr = ~te
        cls = sorted(set(labels[tr]))
        if len(cls) < 2: continue
        sc = StandardScaler().fit(F[tr]) if standardize else None
        Xtr = sc.transform(F[tr]) if sc else F[tr]; Xte = sc.transform(F[te]) if sc else F[te]
        clf = make().fit(Xtr, labels[tr])
        dec = clf.decision_function(Xte)
        if dec.ndim == 1: dec = np.stack([-dec, dec], 1)
        idx = {c: j for j, c in enumerate(clf.classes_)}
        for j, i in enumerate(np.where(te)[0]):
            a, b = labels[i], alts[i]
            if a in idx and b in idx:
                out[i] = dec[j, idx[a]] > dec[j, idx[b]]
    return out


def report(name, ok):
    m = ~np.isnan(ok)
    print(f"  {name:58s} acc={np.nanmean(ok):.4f} (n={m.sum()})  model-wrong acc={np.nanmean(ok[wrong]):.4f} (n={(m & wrong).sum()})", flush=True)


rng = np.random.RandomState(20260918)
for layer in (30, 15):
    F = X[:, 1, layer].float().numpy()          # relcomp
    print(f"\n== relcomp, block {layer}")
    report("LR lbfgs multinomial C=1 (as step 5)", lopo(F, y, alt, lambda: LogisticRegression(C=1.0, max_iter=500, tol=1e-3)))
    report("LR liblinear one-vs-rest C=0.05 (different estimator)", lopo(F, y, alt, lambda: OneVsRestClassifier(LogisticRegression(C=0.05, solver="liblinear", max_iter=500))))
    report("Ridge classifier alpha=100 (different estimator)", lopo(F, y, alt, lambda: RidgeClassifier(alpha=100.0)))
    perm = rng.permutation(len(y)); yp = y[perm]; ap = alt[perm]
    report("NULL: labels permuted across records (expect ~0.5)", lopo(F, yp, ap, lambda: LogisticRegression(C=1.0, max_iter=500, tol=1e-3)))
    # proxy check: can a probe read the FIRST-MENTIONED city? (informative, not a null)
    first = np.array([r["intermediate_id"] if r["fact_order"] == "AB" else r["alt_intermediate_id"] for r in recs])
    second = np.array([r["alt_intermediate_id"] if r["fact_order"] == "AB" else r["intermediate_id"] for r in recs])
    report("proxy: first-mentioned city (queried in AB, distractor in BA)", lopo(F, first, second, lambda: LogisticRegression(C=1.0, max_iter=500, tol=1e-3)))
    ab = np.array([r["fact_order"] == "AB" for r in recs])
    ok = lopo(F, y, alt, lambda: LogisticRegression(C=1.0, max_iter=500, tol=1e-3))
    print(f"  binding probe by fact order: AB={np.nanmean(ok[ab]):.4f} BA={np.nanmean(ok[~ab]):.4f}")

print("\n== arm 3 at the period (dev-fit centroids, pooled roles), re-derived from raw residuals")
for layer in (30, 0):
    Hd = torch.cat([Xd[:, 6, layer], Xd[:, 9, layer]]).float()
    yd = np.array([r["intermediate_id"] for r in Rd] + [r["alt_intermediate_id"] for r in Rd])
    hbar = Hd.mean(0); Xc = Hd - hbar
    mu = {c: Xc[yd == c].mean(0) for c in set(yd)}
    def margin(h, a, b):
        x = h - hbar
        return float(x @ mu[a] - 0.5 * mu[a] @ mu[a]) - float(x @ mu[b] - 0.5 * mu[b] @ mu[b])
    hits = n = 0
    for i, r in enumerate(recs):
        for pi, (a, b) in ((6, (r["intermediate_id"], r["alt_intermediate_id"])), (9, (r["alt_intermediate_id"], r["intermediate_id"]))):
            if a in mu and b in mu:
                hits += margin(X[i, pi, layer].float(), a, b) > 0; n += 1
    print(f"  block {layer}: acc={hits/n:.4f} (n={n})   [step 2 reported L30 0.664, L0 0.994]")
print(f"done {time.time()-t0:.0f}s")
