---
name: jev-fit
description: Use when designing, planning or reviewing any system, feature or workflow — checks where Jev (TypeSafe's cheap, fast judgment model) should or should not be part of the design, against the six usage categories, and produces the required "Jev fit" table. Also use when someone proposes an LLM call that only classifies, routes, scores or answers yes/no.
---

# Jev fit check

Every design gets a **Jev fit** section. Jev changes what is affordable: when a judgment costs
40–400× less than an LLM call, you stop *sampling* and ask questions about **every** item. That
is a difference in kind, not degree — so designs made before Jev existed routinely miss it.
"Jev doesn't fit here" is a valid answer; not asking is not.

## What Jev is

A judgment model (TypeSafe, "system one"). It answers only three question types, many per call:

| Type | Returns | Use for |
|---|---|---|
| **Choice** | best fit of ≤255 options + a probability for every option | kind, category, route, owner, which skill/tool |
| **Score** | position on a 2–10 level scale (every level described in words) + confidence | priority, severity, readiness, quality |
| **Noul** | P(true) for a yes/no question | "is this a pitch?", "does it ask for a deliverable?" |

- ~$0.042 per million input tokens, output free; p50 ~300 ms.
- Batching is nearly free: 13 questions in one call ≈ 12× cheaper than 13 calls, same answers.
  Ask more questions than you think you need.
- Evidence must fit as text under ~32k tokens. Refuse oversized state; never silently truncate.

**It cannot:** write text, code, SQL or explanations; do math, counting or date arithmetic
(extract the facts, compute in code); reason across multiple hops; read intent reliably;
guarantee consistency across calls. Its scores carry no rationale — for high stakes, use a
hybrid: Jev ranks everything, an LLM or human reviews the uncertain band.

## The four-question fit test

A use fits only if all four hold:
1. **The answers can be written in advance** (a fixed option set or a yes/no).
2. **There is volume** — a pile or a stream, not a one-off.
3. **A wrong answer is cheap or easy to catch** (or Jev only restricts/rejects, never grants).
4. **The evidence fits as text** under the state budget.

## The six usage categories — check every design against each

1. **Analyze what you already have.** Ask the same questions of an entire archive, then count
   and correlate. *Replaces:* sampling, hand-audits, "we looked at 50 of them."
2. **Search by meaning.** Describe what you want in words; Jev checks every candidate.
   *Replaces:* keyword/regex filters, embedding top-k with no verification.
3. **Triage what comes in.** "What is this and where does it go?" — per item, at the door, before
   expensive processing. *Replaces:* routing heuristics, paying an LLM to process junk.
4. **Check work against rules.** Turn "please review this" into yes/no questions run on every
   paragraph, record or trace. *Replaces:* spot-check reviews, LLM-as-judge on a sample.
5. **Speed up AI agents.** Micro-judgments that route: which model, how much reasoning effort,
   which skill/tools/context to load, is the draft sufficient. *Replaces:* one-size-fits-all
   agent loops, prompt bloat.
6. **Respond instantly.** "What does this person want right now?" — classify input fields,
   intents or paste targets in under a second. *Replaces:* waiting on an LLM for UI decisions.

## Design rules (learned the hard way)

- **Mirror the human reviewers' reasons.** Ask the questions a reviewer actually rejects on,
  not a generic "is this good?" (one question per judgment — a vague question is five judgments
  in a trench coat).
- **Judge the candidate, not its container.** "Is this *task* real?" with the email as context —
  not "is this email important?"
- **Reject first.** Where Jev gates human review queues, let it *reject* confidently and send the
  rest to humans. Never let Jev *approve* into an authority it doesn't hold.
- **A confident "what kind of item is this" beats "does it contain a request".** Every sales
  or marketing mail contains a request; decide the kind first, then ask the content questions.
- **Scope request/obligation questions to the reader's organization**, but don't narrow wording
  so far that the signal collapses — re-measure after every wording change.
- **Give Jev real evidence.** Snippets starve it; states built from the same fields the producer
  wrote (and the reader's role, where a question mentions it) are what make it accurate.
- **Frame third-party artifacts as the reader's own** (e.g. meeting notes written by a bot about
  the reader's meeting).
- **Build state only from data as it was at decision time** (as-of snapshots).

## Measuring it (required before anything is enforced)

- Pre-register a **claim** per use: variant, confidence floor, and bars (e.g. precision ≥ 0.95,
  recall ≥ 0.2) — set before seeing results.
- Labels come from existing human verdicts, plus a small blind owner review with **reasons**.
- **Distrust proxy labels.** "A task survived" is not "the task was right" — it is biased in both
  directions. Have the owner spot-check the disagreements before believing a FAIL or a PASS.
- A bar never passes on thin evidence: require a minimum *per-metric denominator* (not just total
  n), and show Wilson intervals.
- Promotion path: offline replay → production shadow → enforce per field. Every enforced value
  records its provenance (inferred, model, rubric version, probability), separate from observed
  facts and human assertions.

## Hard limits

- Jev never grants release/permission authority. Irreversible or permission-bearing actions stay
  with a human grant; inside a human-authored standing grant, a tested model may decide scope.
- Jev never produces the text a user reads. It decides, routes, ranks and annotates.

## Required output: the Jev fit table

Put this section in every design/spec/plan:

```markdown
## Jev fit

| # | Category | Applies? | Where in this design | Question(s) and type | Wrong answer costs | How we test it |
|---|---|---|---|---|---|---|
| 1 | Analyze what you have | yes/no | … | … | … | claim + labels |
| 2 | Search by meaning | … | | | | |
| 3 | Triage what comes in | … | | | | |
| 4 | Check work against rules | … | | | | |
| 5 | Speed up AI agents | … | | | | |
| 6 | Respond instantly | … | | | | |

Existing LLM calls in this design that only classify/route/score/answer yes-no: [list, or "none"]
— each is a Jev candidate.
```

Every "no" gets a short reason (fails fit-test question N, or no volume, etc.).

## Project-specific notes

Before proposing, look for an existing Jev/TypeSafe integration in the repo (a `typesafe` package,
decision sites, an offline replay harness, a program spec) and extend it rather than adding a
parallel path. Projects can add their own pointers (paths, harness commands) in their CLAUDE.md.
