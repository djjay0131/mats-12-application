"""Paired two-hop relational-binding stimuli.

THIS IS A METHOD EVALUATION. The two-hop relational-binding task defined here is
an *instrument* used to evaluate an interpretability method; it is not an
attempt to discover the circuit that implements relational binding in any model.
Nothing in this file should be read as a claim about model internals.

Shared by the hour-1 eligibility screen and by `src/make_dataset.py`, so the
vocabulary and template definitions have exactly one home.

A *pair* holds two variants built from an identical inventory of entities,
relations and answer candidates. Only the person->place binding differs:

    Variant A:  Anna lives in Paris.  David lives in Tokyo.
    Variant B:  Anna lives in Tokyo.  David lives in Paris.

The place->object facts are byte-identical across the two variants, so any
readout that merely detects "which concepts are present" cannot separate them.
That is the whole point of the design.

Two nuisance factors are represented explicitly so they can be measured rather
than assumed:

*   ``lexicon``    -- how familiar the filler words are (see LEXICONS below).
*   ``fact_order`` -- ``AB`` states the queried person's binding fact first,
                      ``BA`` states it second. Reversing it dissociates role
                      from linear position. The IOI appendix reports positional
                      signal dominating token signal by roughly 3:1, so without
                      the reversed variant a positive binding result may simply
                      be reading linear position.

MEASURED TOKENIZER FINDING (agent-unverified; see the tokenization audit)
------------------------------------------------------------------------
Against Qwen/Qwen3.5-4B (Qwen2Tokenizer, vocab_size=248044, len(tok)=248077),
the space-prefixed single-token survival rates of the original candidate lists
were:

    NONCE_PEOPLE    2 / 26      REAL_PEOPLE    24 / 24
    NONCE_PLACES    2 / 24      REAL_PLACES    21 / 22
    NONCE_OBJECTS   7 / 24      REAL_OBJECTS   21 / 22

An invented lexicon is therefore NOT usable under a single-token constraint with
this tokenizer. Worse, the handful of "nonce" strings that do survive are almost
all real words the tokenizer already knows (``Mira``, ``Halo``, ``Sund``,
``urn``, ``yarn``, ``dorm``): the single-token filter selects *for* lexical
familiarity, so "single-token" and "nonce" are in direct tension here. The
familiarity contrast is therefore realised as a frequency gradient over real
words (``real`` vs ``rare``) plus an explicitly-labelled ``pseudo`` lexicon,
rather than as a true nonce condition.

Every word listed below has been checked against the real tokenizer in its
space-prefixed form. Nothing here is assumed.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, asdict, field
from typing import Any, Iterable, Sequence

# --------------------------------------------------------------------------
# Preamble
# --------------------------------------------------------------------------
# Every entity word is filtered on its SPACE-PREFIXED form, because that is the
# form in which it occurs mid-sentence. Without a preamble the first person name
# would sit at character 0 with no preceding space, where Qwen BPE tokenizes it
# differently ("Ralph" -> ['R','alph'] but " Ralph" -> [' Ralph']). The original
# version of this file filtered on " Name" while emitting bare "Name" at
# position 0, i.e. it verified a form that never occurred in the prompt. A fixed
# neutral preamble removes the position-0 slot entirely. It is identical across
# every item, so it cannot differentiate any condition.
PREAMBLE = "Facts:"

# --------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------
# All six share one shape: person -> place, place -> object, query the object
# via the person. Keeping them structurally parallel means a template effect is
# about surface wording, not about a different task.


@dataclass(frozen=True)
class Template:
    tid: str
    person_rel: str  # "{p} lives in {place}."
    place_rel: str  # "{place} uses {obj}."
    query: str  # "What is used where {p} lives?"


TEMPLATES: tuple[Template, ...] = (
    Template("T1", "{p} lives in {place}.", "{place} uses {obj}.",
             "What is used where {p} lives?"),
    Template("T2", "{p} works at {place}.", "{place} makes {obj}.",
             "What is made where {p} works?"),
    Template("T3", "{p} studies at {place}.", "{place} teaches {obj}.",
             "What is taught where {p} studies?"),
    Template("T4", "{p} shops at {place}.", "{place} sells {obj}.",
             "What is sold where {p} shops?"),
    Template("T5", "{p} trains at {place}.", "{place} offers {obj}.",
             "What is offered where {p} trains?"),
    Template("T6", "{p} paints at {place}.", "{place} stores {obj}.",
             "What is stored where {p} paints?"),
)

# --------------------------------------------------------------------------
# Candidate vocabulary
# --------------------------------------------------------------------------
# Provenance: every list below is the SURVIVING subset of a larger candidate
# list, filtered against Qwen/Qwen3.5-4B at revision
# 851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a on the space-prefixed form. The
# filter is re-run at build time (`filter_single_token`), so a wrong entry here
# is dropped rather than silently corrupting the dataset.

# --- real: high-frequency, highly familiar -------------------------------
REAL_PEOPLE = [
    "Anna", "David", "Sarah", "Michael", "Laura", "Peter", "Emma", "Thomas",
    "Julia", "Robert", "Clara", "Daniel", "Nina", "Simon", "Alice", "Martin",
    "Helen", "Oscar", "Ruth", "Victor", "Grace", "Leo", "Iris", "Felix",
]
REAL_PLACES = [
    "Paris", "Tokyo", "Berlin", "Madrid", "Cairo", "Boston", "Dublin", "Oslo",
    "Lisbon", "Vienna", "Athens", "Prague", "Munich", "Bristol", "Denver",
    "Seattle", "Milan", "Bergen", "Perth", "Quebec", "Leeds",
]
REAL_OBJECTS = [
    "copper", "silver", "cotton", "rubber", "marble", "bronze", "timber",
    "granite", "leather", "linen", "paper", "glass", "iron", "wool", "clay",
    "salt", "amber", "coral", "jade", "resin", "chalk",
]

# --- rare: real words, markedly lower frequency ---------------------------
# "Florence" was dropped from the people list because it is also a well-known
# city, which would confound the person/place roles.
RARE_PEOPLE = [
    "Cornel", "Cecil", "Clement", "Ernest", "Gilbert", "Irving", "Kenneth",
    "Neville", "Quentin", "Vernon", "Xavier", "Zelda", "Clifford", "Hugo",
    "Rupert", "Marcus",
]
RARE_PLACES = [
    "Utrecht", "Aarhus", "Bilbao", "Salerno", "Verona", "Siena", "Parma",
    "Modena", "Rimini", "Trieste", "Bremen", "Graz",
]
RARE_OBJECTS = [
    "gypsum", "quartz", "cedar", "hemp", "velvet", "satin", "denim", "brass",
    "nickel", "zinc", "platinum", "enamel", "porcelain", "slate", "limestone",
    "tar", "wax", "ash", "mortar",
]

# --- pseudo: pseudoword-STYLED, but NOT true nonce ------------------------
# Read the tokenizer finding at the top of this file before using these. They
# look invented, but the only reason they are single-token is that the
# tokenizer already knows them, and several are ordinary English words
# ("urn", "yarn", "barn", "ferry", "sled", "twig", "depot", "lodge", "vault")
# or ordinary names ("Otto", "Lars", "Nova", "Lima", "Odin"). Do not describe
# results obtained with this lexicon as a nonce-word control.
PSEUDO_PEOPLE = [
    "Mira", "Pell", "Tor", "Mal", "Vin", "Kar", "Den", "Sol", "Bran", "Cor",
    "Dar", "Eld", "Fal", "Gan", "Hal", "Jan", "Kel", "Lem", "Mor", "Nol",
    "Ost", "Pav", "Rin", "Sem", "Tal", "Uri", "Vel", "Wal", "Yan", "Ade",
    "Bel", "Cad", "Dov", "Esk", "Gil", "Hob", "Lars", "Otto", "Urs",
]
PSEUDO_PLACES = [
    "Vald", "Kron", "Lund", "Sund", "Halo", "Alba", "Mora", "Umb", "Zar",
    "Kali", "Kara", "Gala", "Lana", "Mana", "Pala", "Sara", "Belo", "Cala",
    "Lima", "Mala", "Nova", "Pola", "Tara", "Vera", "Aria", "Fora", "Hera",
    "Maia", "Nora", "Odin", "Pisa", "Vida",
]
PSEUDO_OBJECTS = [
    "quil", "kalt", "mev", "urn", "yarn", "cade", "dorm", "vond", "jorn",
    "klim", "rond", "blat", "emp", "mund", "perk", "risp", "sull", "tund",
    "gilt", "tarv", "welt", "brac", "frit", "sled", "twig", "barn", "ferry",
    "depot", "lodge", "vault",
]

# --- the original invented lists, KEPT ONLY AS AN AUDIT RECORD ------------
# These are the lists that failed the single-token filter. They are retained so
# the failure is reproducible, and are deliberately NOT registered in LEXICONS.
DEAD_NONCE_PEOPLE = [
    "Arin", "Bex", "Corin", "Dala", "Emro", "Fenn", "Gorse", "Hax", "Ilva",
    "Jool", "Kesh", "Lorn", "Mira", "Nyle", "Orin", "Pell", "Quin", "Rask",
    "Sova", "Tarn", "Ulm", "Vex", "Wren", "Xan", "Yara", "Zeph",
]
DEAD_NONCE_PLACES = [
    "Luma", "Nori", "Vash", "Drel", "Kova", "Thex", "Brin", "Zalm", "Fera",
    "Mork", "Pyre", "Sund", "Talv", "Wexa", "Yorn", "Cresk", "Glim", "Halo",
    "Jarn", "Odra", "Rill", "Skel", "Umber", "Vorn",
]
DEAD_NONCE_OBJECTS = [
    "zent", "vark", "quil", "brim", "dross", "flen", "gorm", "hesp", "kalt",
    "lorn", "mev", "nusk", "plim", "rax", "sorb", "tave", "urn", "volk",
    "wisp", "yarn", "zick", "cade", "dorm", "elth",
]

LEXICONS: dict[str, tuple[list[str], list[str], list[str]]] = {
    "real": (REAL_PEOPLE, REAL_PLACES, REAL_OBJECTS),
    "rare": (RARE_PEOPLE, RARE_PLACES, RARE_OBJECTS),
    "pseudo": (PSEUDO_PEOPLE, PSEUDO_PLACES, PSEUDO_OBJECTS),
}

FACT_ORDERS: tuple[str, ...] = ("AB", "BA")
BINDING_VARIANTS: tuple[str, ...] = ("A", "B")


class LexiconError(ValueError):
    """Raised when a requested lexicon cannot produce a sound dataset."""


_NONCE_MSG = (
    "lexicon 'nonce' has been removed. Measured against Qwen/Qwen3.5-4B, the "
    "invented lists survive the space-prefixed single-token filter at "
    "2/26 people, 2/24 places, 7/24 objects. Two surviving people and two "
    "surviving places means every generated pair reuses the same two entities, "
    "which the old >=2 guard did not catch. Use lexicon 'rare' for a "
    "low-frequency contrast, or 'pseudo' for pseudoword-styled strings -- but "
    "read the docstring first: 'pseudo' is NOT a nonce control."
)


# --------------------------------------------------------------------------
# Tokenizer filtering
# --------------------------------------------------------------------------

def is_single_token(tok: Any, word: str, *, with_space: bool = True) -> bool:
    """True iff `word` occupies exactly one token in the position it is used.

    Every scored word appears mid-sentence, i.e. preceded by a space, so the
    space-prefixed form is the one that must be single-token. Qwen BPE treats
    ``"Ralph"`` and ``" Ralph"`` as different token sequences; checking the
    bare form would be checking the wrong thing.
    """
    text = (" " + word) if with_space else word
    return len(tok.encode(text, add_special_tokens=False)) == 1


def single_token_id(tok: Any, word: str) -> int:
    ids = tok.encode(" " + word, add_special_tokens=False)
    if len(ids) != 1:
        raise ValueError(f"{word!r} is not single-token: {ids}")
    return ids[0]


def filter_single_token(tok: Any, words: Iterable[str]) -> list[str]:
    return [w for w in words if is_single_token(tok, w)]


def audit_lexicon(tok: Any, name: str) -> dict:
    """Survival counts for one registered lexicon, for the record."""
    people, places, objects = LEXICONS[name]
    out = {"lexicon": name}
    for role, words in (("people", people), ("places", places),
                        ("objects", objects)):
        kept = filter_single_token(tok, words)
        out[role] = {"n_candidates": len(words), "n_survived": len(kept),
                     "survivors": kept,
                     "died": [w for w in words if w not in set(kept)]}
    return out


# --------------------------------------------------------------------------
# Left-padding safety
# --------------------------------------------------------------------------
# The observation point is the FINAL prompt token. With right padding the final
# column of a batch is a pad token and nothing errors -- the readout silently
# reads padding. These helpers make that mistake impossible to make quietly.


class PaddingSideError(RuntimeError):
    pass


def assert_left_padding(tok: Any) -> None:
    side = getattr(tok, "padding_side", None)
    if side != "left":
        raise PaddingSideError(
            f"tokenizer.padding_side is {side!r}, must be 'left'. The readout "
            "indexes the final column of the batch; with right padding that "
            "column is a pad token and nothing raises."
        )


def final_token_index(attention_mask) -> Any:
    """Index of the last real token per row: attention_mask.sum(-1) - 1.

    Correct under either padding side. Prefer this over hard-coding -1.
    """
    return attention_mask.sum(-1) - 1


def batch_encode_for_readout(tok: Any, prompts: Sequence[str], **kw):
    """Encode a batch such that column -1 is guaranteed to be a real token.

    Sets left padding, then *verifies* it from the returned mask rather than
    trusting the flag. The check is the invariant that actually matters:
    under left padding every row's final position is unmasked.
    """
    prev = getattr(tok, "padding_side", None)
    tok.padding_side = "left"
    try:
        enc = tok(list(prompts), return_tensors="pt", padding=True, **kw)
    finally:
        if prev is not None:
            tok.padding_side = prev
    mask = enc["attention_mask"]
    if int(mask[:, -1].sum()) != int(mask.shape[0]):
        raise PaddingSideError(
            "final column of attention_mask contains padding; the batch is not "
            "left-padded. Do not read position -1."
        )
    return enc


# --------------------------------------------------------------------------
# Pair construction
# --------------------------------------------------------------------------


@dataclass
class Variant:
    variant: str  # "A" or "B" -- which person->place binding
    fact_order: str  # "AB" or "BA" -- linear order of the two binding facts
    prompt: str
    intermediate: str  # the place the queried person is bound to
    answer: str  # the object that place is bound to
    alt_intermediate: str
    alt_answer: str

    @property
    def cell(self) -> str:
        return f"{self.variant}/{self.fact_order}"


@dataclass
class Pair:
    pair_id: str
    template_id: str
    lexicon: str
    shot: str  # "zero" or "few"
    person_q: str  # the queried person
    person_d: str  # the distractor person
    place1: str
    place2: str
    obj1: str
    obj2: str
    seed: int
    variants: list[Variant] = field(default_factory=list)

    def to_json(self) -> dict:
        d = asdict(self)
        d["variants"] = [asdict(v) for v in self.variants]
        return d


def _body(t: Template, pq: str, pd: str, place_q: str, place_d: str,
          place1: str, place2: str, obj1: str, obj2: str,
          fact_order: str) -> str:
    """Assemble the fact block.

    `place_q` is the place the *queried* person is bound to in this variant.
    The two place->object facts are always stated in the fixed order
    (place1, place2) so that they are byte-identical across variants A and B;
    only the person->place facts move.
    """
    if fact_order not in FACT_ORDERS:
        raise ValueError(f"fact_order must be one of {FACT_ORDERS}")
    fq = t.person_rel.format(p=pq, place=place_q)
    fd = t.person_rel.format(p=pd, place=place_d)
    person_facts = [fq, fd] if fact_order == "AB" else [fd, fq]
    place_facts = [
        t.place_rel.format(place=place1, obj=obj1),
        t.place_rel.format(place=place2, obj=obj2),
    ]
    return " ".join(person_facts + place_facts)


def make_prompt(t: Template, pq: str, pd: str, place_q: str, place_d: str,
                place1: str, place2: str, obj1: str, obj2: str,
                fact_order: str, prefix: str = "") -> str:
    body = _body(t, pq, pd, place_q, place_d, place1, place2, obj1, obj2,
                 fact_order)
    return (f"{PREAMBLE} {prefix}{body} {t.query.format(p=pq)} Answer:")


def build_few_shot_prefix(t: Template, rng: random.Random,
                          people: list[str], places: list[str],
                          objects: list[str], n_shots: int = 2) -> str:
    """Solved examples of the same template.

    Drawn from a pool the caller has already made disjoint from the target
    item's vocabulary, so the prefix cannot leak the answer.
    """
    blocks = []
    for _ in range(n_shots):
        pq, pd = rng.sample(people, 2)
        pl1, pl2 = rng.sample(places, 2)
        o1, o2 = rng.sample(objects, 2)
        body = _body(t, pq, pd, pl1, pl2, pl1, pl2, o1, o2, "AB")
        blocks.append(f"{body} {t.query.format(p=pq)} Answer: {o1}.")
    return " ".join(blocks) + " "


def _pools(tok: Any, lexicon: str, *, min_per_role: int = 6):
    if lexicon == "nonce":
        raise LexiconError(_NONCE_MSG)
    if lexicon not in LEXICONS:
        raise LexiconError(f"unknown lexicon {lexicon!r}; "
                           f"known: {sorted(LEXICONS)}")
    people_all, places_all, objects_all = LEXICONS[lexicon]
    people = filter_single_token(tok, people_all)
    places = filter_single_token(tok, places_all)
    objects = filter_single_token(tok, objects_all)

    # Roles must not overlap within a lexicon, or a "person" token could also
    # be a candidate answer.
    if set(people) & set(places) or set(places) & set(objects) or \
            set(people) & set(objects):
        raise LexiconError(
            f"lexicon {lexicon!r} has words shared between roles: "
            f"{sorted((set(people) & set(places)) | (set(places) & set(objects)) | (set(people) & set(objects)))}"
        )

    # The old guard was `>= 2`, which a 2-word pool passes while producing N
    # pairs that all reuse the same two entities. Require a real pool.
    for role, pool, raw in (("people", people, people_all),
                            ("places", places, places_all),
                            ("objects", objects, objects_all)):
        if len(pool) < min_per_role:
            raise LexiconError(
                f"lexicon {lexicon!r} role {role}: only {len(pool)} of "
                f"{len(raw)} candidates are single-token, need "
                f">= {min_per_role}. A pool this small yields pairs that all "
                "reuse the same entities."
            )
    return people, places, objects


def build_pairs(tok: Any, *, n_pairs: int, seed: int, lexicon: str,
                fact_orders: Sequence[str] = FACT_ORDERS,
                shot: str = "zero", n_shots: int = 2,
                min_per_role: int = 6, id_prefix: str = "",
                start_index: int = 0) -> list[Pair]:
    """Build `n_pairs` paired items, cycling through the templates.

    Each Pair carries one Variant per (binding variant, fact_order) cell, i.e.
    four variants by default. `fact_orders` defaults to both orders because the
    order-reversed variant is a required control, not an option.

    Every word used is verified single-token first; because all of them are
    single-token, "equal token length across a swapped pair" holds by
    construction -- but `verify_pair_tokenization` asserts it explicitly rather
    than trusting the argument.
    """
    people, places, objects = _pools(tok, lexicon, min_per_role=min_per_role)

    # Reserve a disjoint slice for few-shot demonstrations so the prefix can
    # never contain a target item's entities.
    n_res = 4
    if shot == "few":
        if min(len(people), len(places), len(objects)) < n_res + min_per_role:
            raise LexiconError("not enough single-token words to reserve a "
                               "disjoint few-shot pool")
        res_people, people = people[:n_res], people[n_res:]
        res_places, places = places[:n_res], places[n_res:]
        res_objects, objects = objects[:n_res], objects[n_res:]

    rng = random.Random(seed)
    pairs: list[Pair] = []
    for i in range(start_index, start_index + n_pairs):
        t = TEMPLATES[i % len(TEMPLATES)]
        pq, pd = rng.sample(people, 2)
        place1, place2 = rng.sample(places, 2)
        obj1, obj2 = rng.sample(objects, 2)

        prefix = ""
        if shot == "few":
            prefix = build_few_shot_prefix(t, rng, res_people, res_places,
                                           res_objects, n_shots=n_shots)

        variants: list[Variant] = []
        for fo in fact_orders:
            # Variant A: queried person bound to place1 -> answer obj1
            variants.append(Variant(
                variant="A", fact_order=fo,
                prompt=make_prompt(t, pq, pd, place1, place2, place1, place2,
                                   obj1, obj2, fo, prefix),
                intermediate=place1, answer=obj1,
                alt_intermediate=place2, alt_answer=obj2,
            ))
            # Variant B: bindings swapped -> queried person bound to place2
            variants.append(Variant(
                variant="B", fact_order=fo,
                prompt=make_prompt(t, pq, pd, place2, place1, place1, place2,
                                   obj1, obj2, fo, prefix),
                intermediate=place2, answer=obj2,
                alt_intermediate=place1, alt_answer=obj1,
            ))

        pairs.append(Pair(
            pair_id=f"{id_prefix}{lexicon}-{shot}-{i:03d}",
            template_id=t.tid, lexicon=lexicon, shot=shot,
            person_q=pq, person_d=pd,
            place1=place1, place2=place2, obj1=obj1, obj2=obj2,
            seed=seed, variants=variants,
        ))
    return pairs


# --------------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------------


class TokenizationError(AssertionError):
    pass


def verify_pair_tokenization(tok: Any, pair: Pair) -> dict:
    """Assert every tokenization property the design depends on.

    1. Every scored word (intermediate, answer, and their alternates) is
       single-token in its space-prefixed form.
    2. Every ENTITY is single-token too -- people and distractor places, not
       only the scored slots.
    3. All variants of the pair have IDENTICAL prompt token length. If every
       word is single-token this holds by construction; it is asserted anyway,
       because "by construction" is exactly the kind of claim that quietly
       stops being true.
    4. The prompts of the variants differ (a pair whose variants collapse to
       the same string is useless).
    """
    for w in (pair.person_q, pair.person_d, pair.place1, pair.place2,
              pair.obj1, pair.obj2):
        if not is_single_token(tok, w):
            raise TokenizationError(
                f"{pair.pair_id}: entity {w!r} is not single-token when "
                f"space-prefixed: "
                f"{tok.encode(' ' + w, add_special_tokens=False)}"
            )

    lengths = {}
    for v in pair.variants:
        for w in (v.intermediate, v.answer, v.alt_intermediate, v.alt_answer):
            if not is_single_token(tok, w):
                raise TokenizationError(
                    f"{pair.pair_id}/{v.cell}: scored word {w!r} is not "
                    "single-token when space-prefixed")
        lengths[v.cell] = len(tok.encode(v.prompt, add_special_tokens=False))

    if len(set(lengths.values())) != 1:
        raise TokenizationError(
            f"{pair.pair_id}: variants have unequal prompt token lengths "
            f"{lengths}. A length difference means the swap is not a clean "
            "minimal edit and position indices are not comparable."
        )

    prompts = [v.prompt for v in pair.variants]
    if len(set(prompts)) != len(prompts):
        raise TokenizationError(
            f"{pair.pair_id}: two variants produced identical prompts")

    # The two place->object facts must be byte-identical across variants, i.e.
    # A and B at the same fact_order may differ only by the binding.
    by_order: dict[str, list[Variant]] = {}
    for v in pair.variants:
        by_order.setdefault(v.fact_order, []).append(v)
    for fo, vs in by_order.items():
        if len(vs) == 2:
            a, b = sorted(vs, key=lambda v: v.variant)
            ia = tok.encode(a.prompt, add_special_tokens=False)
            ib = tok.encode(b.prompt, add_special_tokens=False)
            diff = [k for k, (x, y) in enumerate(zip(ia, ib)) if x != y]
            if len(diff) != 2:
                raise TokenizationError(
                    f"{pair.pair_id}/{fo}: variants A and B differ at "
                    f"{len(diff)} token positions, expected exactly 2 (the two "
                    f"swapped place tokens). positions={diff}")

    return {"pair_id": pair.pair_id, "prompt_n_tokens": next(iter(lengths.values())),
            "cells": sorted(lengths)}
