#!/usr/bin/env node
/**
 * conformance-check.mjs — gate the MATS 12.0 submission against every
 * mechanically-checkable requirement in Neel Nanda's application doc.
 *
 * Requirement IDs refer to docs/application/conformance-register.md.
 *
 *   node scripts/conformance-check.mjs [--gate SELECT|EXECUTE|WRITEUP|SUBMIT]
 *
 * Exit 0 = no failures at or before the named gate. Exit 1 = blocked.
 * Default gate is SUBMIT (everything).
 *
 * Design note: this script cannot judge taste, clarity or skepticism.
 * It exists to make the *mechanical* failures impossible, so that human
 * review time goes entirely to the parts that need judgement. Anything it
 * cannot check is routed to the neel-reviewer agent and the human gate in
 * docs/application/selection-rubric.md.
 */

import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const GATES = ['SELECT', 'EXECUTE', 'WRITEUP', 'SUBMIT'];
const argGate = (process.argv.find(a => a.startsWith('--gate')) || '').split('=')[1]
  || (process.argv[process.argv.indexOf('--gate') + 1] || '');
const GATE = GATES.includes(argGate) ? argGate : 'SUBMIT';
const GATE_IDX = GATES.indexOf(GATE);

const P = {
  exec:     'writeup/exec-summary.md',
  main:     'writeup/main.md',
  claims:   'docs/application/claims-register.md',
  verify:   'docs/application/verification-ledger.md',
  controls: 'docs/application/controls-ledger.md',
  time:     'llm/memory_bank/time-log.md',
  canon:    'results/canonical.json',
  adr2:     'docs/adr/0002-project-selection.md',
};

const results = [];
const read = p => existsSync(join(ROOT, p)) ? readFileSync(join(ROOT, p), 'utf8') : null;
const has  = p => existsSync(join(ROOT, p));

function check(id, gate, label, fn) {
  if (GATES.indexOf(gate) > GATE_IDX) return;
  let status, detail;
  try { ({ status, detail } = fn()); }
  catch (e) { status = 'ERROR'; detail = e.message; }
  results.push({ id, gate, label, status, detail: detail || '' });
}
const pass = d => ({ status: 'PASS', detail: d });
const fail = d => ({ status: 'FAIL', detail: d });
const warn = d => ({ status: 'WARN', detail: d });
const na   = d => ({ status: 'N/A',  detail: d });

// ── helpers ────────────────────────────────────────────────────────────────
const words = s => (s.replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')      // drop images
                     .replace(/```[\s\S]*?```/g, ' ')            // drop code
                     .replace(/[#*_>|`-]/g, ' ')
                     .match(/\b[\w''-]+\b/g) || []).length;
const images = s => (s.match(/!\[[^\]]*\]\([^)]*\)|<img\s/gi) || []).length;
const tables = s => s.split('\n\n').filter(b => /^\|.*\|/m.test(b) && /\|\s*-{2,}/.test(b));
const numbersIn = s => (s.replace(/```[\s\S]*?```/g, ' ')
                         .match(/(?<![\w.])-?\d+(?:\.\d+)?%?(?![\w])/g) || [])
                       .map(n => n.replace('%', ''))
                       .filter(n => Math.abs(parseFloat(n)) > 1); // ignore 0/1/small ordinals
const rows = md => md ? md.split('\n').filter(l => /^\s*\|/.test(l) && !/\|\s*-{2,}/.test(l)).slice(1) : [];

// ── BLK-15 / BLK-16 — old models ───────────────────────────────────────────
const BANNED_MODELS = [/\bgpt-?2\b/i, /\bpythia\b/i, /\bgemma[\s-]?2\b/i];
const CURRENT_MODELS = [/olmo[\s-]?3/i, /qwen[\s-]?3\.\d/i, /gpt-oss/i, /gemma[\s-]?4/i,
                        /nemotron/i, /glm[\s-]?5/i, /deepseek[\s-]?v4/i, /kimi[\s-]?k2/i, /llama[\s-]?4/i];

check('BLK-15/16', 'SELECT', 'Primary model is not GPT-2 / Pythia / Gemma 2', () => {
  const doc = [read(P.main), read(P.exec), read(P.adr2)].filter(Boolean).join('\n');
  if (!doc) return na('no write-up or ADR-0002 yet');
  const hits = BANNED_MODELS.filter(r => r.test(doc)).map(r => String(r));
  const current = CURRENT_MODELS.filter(r => r.test(doc));
  if (hits.length && !/as a (baseline|comparison|control)|prior work|related work|not used/i.test(doc))
    return fail(`old-model mention with no exculpating context: ${hits.join(', ')} — Neel: "There's no good reason to use GPT-2 in your application at this point"`);
  if (!current.length) return warn('no model from the current allowlist detected — confirm the subject model reads as current');
  return pass(`${current.length} current-model reference(s), no unexplained old-model use`);
});

// ── BLK-14 — areas he is out of ────────────────────────────────────────────
const DEAD_AREAS = [/\bgrokking\b/i, /circuit[- ]finding/i, /SAE hill[- ]climbing/i,
                    /basic science of SAEs/i, /\btoy model/i, /algorithmic task/i];
check('BLK-14', 'SELECT', 'Project is not in an area he has left', () => {
  const doc = [read(P.adr2), read(P.exec)].filter(Boolean).join('\n');
  if (!doc) return na('ADR-0002 not written yet');
  const hits = DEAD_AREAS.filter(r => r.test(doc)).map(r => String(r).slice(1, -2));
  if (!hits.length) return pass('clear');
  return warn(`mentions ${hits.join(', ')} — fine as contrast, fatal as the subject. Confirm framing.`);
});

// ── MEC-06 — exec summary length ───────────────────────────────────────────
check('MEC-06', 'SUBMIT', 'Executive summary ≤600 words', () => {
  const s = read(P.exec);
  if (!s) return fail('writeup/exec-summary.md missing');
  const w = words(s);
  return w <= 600 ? pass(`${w} words`) : fail(`${w} words — limit is 600 ("max 3 pages and max 600 words")`);
});

// ── MEC-07 — graphs in the exec summary ────────────────────────────────────
check('MEC-07', 'SUBMIT', 'Executive summary contains graphs', () => {
  const s = read(P.exec);
  if (!s) return fail('writeup/exec-summary.md missing');
  const n = images(s);
  return n >= 1 ? pass(`${n} figure(s)`) : fail('no figures — "Please include graphs!"');
});

// ── MEC-08 — exec summary structure ────────────────────────────────────────
check('MEC-08', 'SUBMIT', 'Executive summary has the three suggested sections', () => {
  const s = read(P.exec);
  if (!s) return fail('writeup/exec-summary.md missing');
  const need = [
    [/problem|trying to solve/i, 'What problem am I trying to solve'],
    [/takeaway|found|learned/i,  'High-level takeaways'],
    [/experiment/i,              'One paragraph + graph per key experiment'],
  ];
  const missing = need.filter(([r]) => !r.test(s)).map(([, n]) => n);
  return missing.length ? warn(`missing: ${missing.join('; ')}`) : pass('all three present');
});

// ── SCR-07 — exec summary specificity ──────────────────────────────────────
check('SCR-07', 'SUBMIT', 'Exec summary names models, an experiment, a number, a limitation', () => {
  const s = read(P.exec);
  if (!s) return fail('writeup/exec-summary.md missing');
  const miss = [];
  if (!CURRENT_MODELS.some(r => r.test(s))) miss.push('a named model');
  if (!/\d/.test(s)) miss.push('a numeric result');
  if (!/limit|caveat|however|doesn't|does not|unclear|weak/i.test(s)) miss.push('a stated limitation');
  return miss.length ? fail(`missing ${miss.join(', ')} — "Specifics beat vibes: name the models, the key experiment, the surprising number"`) : pass('specific');
});

// ── BLK-04/05 — LLM voice ──────────────────────────────────────────────────
const LLM_TELLS = [/\bdelve\b/i, /\btapestry\b/i, /\btestament to\b/i, /\bnavigat(e|ing) the\b/i,
  /\bit'?s worth noting\b/i, /\bin the realm of\b/i, /\bunderscore[sd]?\b/i, /\bmultifaceted\b/i,
  /\bcrucial(ly)? (to|for) (note|understand)\b/i, /\bleverage[sd]?\b/i, /\brobust(ly)? (framework|approach)\b/i,
  /\bthis (isn'?t|is not) (just|merely) [^.]{2,40}[—-] it'?s\b/i, /\bnot (just|only) [^.]{2,40}, but\b/i];
check('BLK-04/05', 'SUBMIT', 'Exec summary does not read as LLM output', () => {
  const s = read(P.exec);
  if (!s) return fail('writeup/exec-summary.md missing');
  const hits = LLM_TELLS.filter(r => r.test(s)).map(r => (s.match(r) || [''])[0]).filter(Boolean);
  const dash = (s.match(/[—–]/g) || []).length;
  const per100 = (dash / Math.max(words(s), 1)) * 100;
  const notes = [];
  if (hits.length) notes.push(`LLM-tell phrases: ${[...new Set(hits)].join(', ')}`);
  if (per100 > 1.2) notes.push(`em-dash density ${per100.toFixed(1)}/100w`);
  if (!notes.length) return pass('no stylometric flags');
  return fail(`${notes.join('; ')} — "Answers that read like they were written by an LLM are a significant negative signal"`);
});

// ── BLK-11 / BLK-12 — baselines ────────────────────────────────────────────
const BASELINE_WORDS = /random|baseline|control|probe|shuffl|ablat|just ask|prompt-only|chance/i;
check('BLK-11', 'WRITEUP', 'Every results table carries a baseline/control column', () => {
  const s = read(P.main);
  if (!s) return na('write-up not started');
  const t = tables(s);
  if (!t.length) return warn('no results tables found');
  const bad = t.filter(b => !BASELINE_WORDS.test(b.split('\n')[0]));
  return bad.length
    ? fail(`${bad.length}/${t.length} table(s) have no baseline column — "Failing to compare to baselines" is on his disqualifying list`)
    : pass(`${t.length}/${t.length} tables have a baseline column`);
});

check('BLK-12', 'WRITEUP', 'Controls ledger records a cheap control per method claim', () => {
  const s = read(P.controls);
  if (!s) return fail('docs/application/controls-ledger.md missing');
  const r = rows(s);
  if (!r.length) return fail('controls ledger has no rows');
  const empty = r.filter(l => !BASELINE_WORDS.test(l));
  return empty.length ? fail(`${empty.length} row(s) name no control`) : pass(`${r.length} claim(s), all controlled`);
});

// ── SCR-22 — claim typing ──────────────────────────────────────────────────
check('SCR-22', 'WRITEUP', 'Every claim is tagged existence-proof or method-claim', () => {
  const s = read(P.claims);
  if (!s) return fail('docs/application/claims-register.md missing');
  const r = rows(s);
  if (!r.length) return fail('claims register has no rows');
  const untagged = r.filter(l => !/existence[- ]proof|method[- ]claim|general[- ]claim/i.test(l));
  if (untagged.length) return fail(`${untagged.length} untagged claim(s) — cherry-picking is only permissible under an explicit existence-proof tag`);
  const methodNoBase = r.filter(l => /method[- ]claim|general[- ]claim/i.test(l) && !BASELINE_WORDS.test(l));
  return methodNoBase.length
    ? fail(`${methodNoBase.length} general/method claim(s) with no baseline`)
    : pass(`${r.length} claims, all tagged and controlled`);
});

// ── BLK-24 / SCR-20 — numbers trace to canonical results ───────────────────
check('BLK-24', 'SUBMIT', 'Every number in the write-up traces to canonical results', () => {
  const s = [read(P.exec), read(P.main)].filter(Boolean).join('\n');
  if (!s) return na('write-up not started');
  if (!has(P.canon)) return fail('results/canonical.json missing — no way to verify reported numbers');
  const canon = JSON.parse(read(P.canon));
  const flat = JSON.stringify(canon);
  const claimed = [...new Set(numbersIn(s))];
  const orphan = claimed.filter(n => !flat.includes(n) && !flat.includes(String(Math.round(parseFloat(n)))));
  return orphan.length
    ? fail(`${orphan.length} number(s) not in canonical results: ${orphan.slice(0, 12).join(', ')}${orphan.length > 12 ? '…' : ''}`)
    : pass(`${claimed.length} numbers all trace`);
});

// ── BLK-01 / SCR-19 / SCR-20 — verification ledger ─────────────────────────
check('BLK-01', 'SUBMIT', 'Every headline claim has a human verification row', () => {
  const v = read(P.verify), c = read(P.claims);
  if (!v) return fail('docs/application/verification-ledger.md missing — "if your write-up contains key results you clearly never verified … that\'s disqualifying"');
  const vr = rows(v), cr = rows(c || '');
  const unverified = vr.filter(l => !/\b(verified|re-?derived|confirmed)\b/i.test(l) || /\bTODO\b|\bpending\b/i.test(l));
  if (unverified.length) return fail(`${unverified.length} ledger row(s) not marked verified`);
  if (cr.length && vr.length < cr.length) return fail(`${cr.length} claims but only ${vr.length} verification rows`);
  return vr.length ? pass(`${vr.length} claim(s) independently re-derived`) : fail('verification ledger is empty');
});

// ── BLK-10 — random selection of qualitative examples ──────────────────────
check('BLK-10', 'SUBMIT', 'Qualitative examples are randomly selected with a recorded seed', () => {
  const s = read(P.main);
  if (!s) return na('write-up not started');
  if (!/qualitative|raw example|sample transcript|example rollout/i.test(s)) return warn('no qualitative-examples section detected — he asks for one right after the exec summary');
  return /seed\s*[=:]\s*\d+|random_state|randomly selected/i.test(s)
    ? pass('random selection declared')
    : fail('examples present but no seed / "randomly selected" declaration — "Randomly selected, not cherry-picked!"');
});

// ── BLK-18 — replication before building ───────────────────────────────────
check('BLK-18', 'WRITEUP', 'Phenomenon shown to replicate in this setup before downstream analysis', () => {
  const s = read(P.main);
  if (!s) return na('write-up not started');
  const idx = s.search(/replicat|reproduce|does the effect exist|sanity check.*setup|phenomenon.*present/i);
  if (idx < 0) return fail('no replication section — "Building on a phenomenon without first checking it replicates in your setting"');
  const heads = [...s.matchAll(/^##\s+/gm)].map(m => m.index);
  const after = heads.filter(h => h > idx).length;
  return after >= 1 ? pass('replication established before downstream sections') : warn('replication section appears late — move it earlier');
});

// ── SCR-17 — limitations, confidence, next steps ───────────────────────────
check('SCR-17', 'SUBMIT', 'Limitations, confidence labels and next steps are present', () => {
  const s = read(P.main);
  if (!s) return na('write-up not started');
  const need = [[/^#+.*limitation/im, 'Limitations'], [/speculative|low confidence|uncertain|tentative/i, 'confidence labelling'], [/^#+.*(next step|future work|what i.d do next)/im, 'Next steps']];
  const missing = need.filter(([r]) => !r.test(s)).map(([, n]) => n);
  return missing.length ? fail(`missing: ${missing.join(', ')}`) : pass('all present');
});

// ── SCR-02 — methods completeness ──────────────────────────────────────────
check('SCR-02', 'SUBMIT', 'Methods state data generation, prompts, metrics, hyperparameters, n', () => {
  const s = read(P.main);
  if (!s) return na('write-up not started');
  const need = [[/data (generation|was generated)|dataset construction|how i (built|generated)/i, 'data generation'],
                [/prompt/i, 'prompt choice'], [/metric|we define|defined as/i, 'metric definition'],
                [/hyperparameter|temperature|top[_ ]?p|seed|learning rate|n_?samples/i, 'hyperparameters'],
                [/\bn\s*=\s*\d+|sample size/i, 'sample size']];
  const missing = need.filter(([r]) => !r.test(s)).map(([, n]) => n);
  return missing.length ? fail(`missing: ${missing.join(', ')} — "Show me enough detail so I can follow along"`) : pass('complete');
});

// ── SCR-28 — simplicity before complexity ──────────────────────────────────
check('SCR-28', 'WRITEUP', 'Fancy methods are justified against a simple baseline', () => {
  const s = read(P.main);
  if (!s) return na('write-up not started');
  if (!/\bSAE\b|crosscoder|attribution graph|transcoder|sparse autoencoder/i.test(s)) return pass('no heavy machinery used');
  return /linear probe|prompting|just ask|reading the (chain of thought|CoT)/i.test(s)
    ? pass('simple comparison present')
    : fail('heavy method with no simple-baseline comparison — "trying a really high effort method without trying something simple"');
});

// ── SCR-35 — narrative not chronology ──────────────────────────────────────
check('SCR-35', 'SUBMIT', 'Write-up is structured by narrative, not chronologically', () => {
  const s = read(P.main);
  if (!s) return na('write-up not started');
  const heads = [...s.matchAll(/^##\s+(.+)$/gm)].map(m => m[1]);
  const chrono = heads.filter(h => /^(day|week|attempt|first|then|next|finally|step)\b/i.test(h.trim()));
  return chrono.length >= 2
    ? fail(`${chrono.length} chronological headings — "please structure the write-up to emphasise it, don't do chronological order!"`)
    : pass('narrative structure');
});

// ── MEC-14..17 / ADV-06 — the hour ledger ──────────────────────────────────
check('MEC-14/15/16', 'EXECUTE', 'Counted hours within budget', () => {
  const s = read(P.time);
  if (!s) return fail('llm/memory_bank/time-log.md missing');
  const nums = [...s.matchAll(/\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*$/gm)].map(m => parseFloat(m[1]));
  const total = nums.reduce((a, b) => a + b, 0);
  const execM = (s.match(/Exec summary:\s*([\d.]+)\s*\/\s*2/i) || [])[1];
  const out = [];
  if (total > 20) out.push(`counted total ${total.toFixed(1)}h exceeds 20`);
  if (execM && parseFloat(execM) > 2) out.push(`exec-summary time ${execM}h exceeds 2`);
  return out.length ? fail(out.join('; ')) : pass(`${total.toFixed(1)}/20.0 counted hours logged`);
});

check('ADV-06', 'EXECUTE', 'Paper reading ≤5 of the counted hours', () => {
  const s = read(P.time);
  if (!s) return na('no time log');
  const reading = s.split('\n').filter(l => /read|paper|literature/i.test(l))
    .map(l => parseFloat((l.match(/\|\s*([\d.]+)\s*\|\s*[\d.]+\s*\|\s*$/) || [])[1] || 0))
    .reduce((a, b) => a + b, 0);
  return reading > 5 ? fail(`${reading.toFixed(1)}h reading — he recommends at most 5`) : pass(`${reading.toFixed(1)}h reading`);
});

// ── MEC-20 — time screenshot ───────────────────────────────────────────────
check('MEC-20', 'SUBMIT', 'Time-tracker screenshot attached', () => {
  const s = [read(P.main), read(P.exec)].filter(Boolean).join('\n');
  if (!s) return na('write-up not started');
  return /toggl|time.?track/i.test(s) && images(s) > 0 ? pass('referenced') : warn('no time-tracker screenshot found — encouraged, and cheap credibility');
});

// ── MEC-02 — deadline ──────────────────────────────────────────────────────
check('MEC-02', 'SUBMIT', 'Before the deadline', () => {
  const due = new Date('2026-09-05T06:59:00Z'); // Sept 4 23:59 PT
  const left = (due - new Date()) / 36e5;
  if (left < 0) return fail('DEADLINE PASSED — extension form: https://forms.gle/gpceDYrxTUaZBoHA8');
  return left < 48 ? warn(`${left.toFixed(1)}h remaining`) : pass(`${(left / 24).toFixed(1)} days remaining`);
});

// ── ADR-0002 gate ──────────────────────────────────────────────────────────
check('GATE-1', 'EXECUTE', 'ADR-0002 accepted before counted execution begins', () => {
  const s = read(P.adr2);
  if (!s) return fail('docs/adr/0002-project-selection.md missing');
  return /^status:\s*accepted/im.test(s)
    ? pass('project locked')
    : fail('ADR-0002 still Proposed — do not start counted experiment hours until Gate 1 is cleared');
});

// ── report ─────────────────────────────────────────────────────────────────
const C = { PASS: '\x1b[32m', FAIL: '\x1b[31m', WARN: '\x1b[33m', 'N/A': '\x1b[90m', ERROR: '\x1b[31m', r: '\x1b[0m' };
const pad = (s, n) => String(s).padEnd(n);
console.log(`\nMATS 12.0 conformance — gate: ${GATE}\n${'='.repeat(78)}`);
for (const r of results)
  console.log(`${C[r.status]}${pad(r.status, 6)}${C.r} ${pad(r.id, 11)} ${r.label}${r.detail ? `\n${' '.repeat(19)}${C['N/A']}${r.detail}${C.r}` : ''}`);

const f = results.filter(r => r.status === 'FAIL' || r.status === 'ERROR');
const w = results.filter(r => r.status === 'WARN');
console.log(`${'='.repeat(78)}`);
console.log(`${results.filter(r => r.status === 'PASS').length} pass · ${w.length} warn · ${f.length} fail · ${results.filter(r => r.status === 'N/A').length} n/a`);
if (f.length) {
  console.log(`\n${C.FAIL}BLOCKED${C.r} — ${f.length} failure(s) at gate ${GATE}:`);
  f.forEach(r => console.log(`  · ${r.id} ${r.label}`));
  console.log(`\nFull requirement text: docs/application/conformance-register.md`);
  console.log(`Judgement-based criteria this script cannot check: docs/application/selection-rubric.md`);
  console.log(`Adversarial read: run the neel-reviewer agent.`);
}
process.exit(f.length ? 1 : 0);
