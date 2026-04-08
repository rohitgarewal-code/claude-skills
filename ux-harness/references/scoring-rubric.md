# UX Harness Scoring Rubric

The harness scores five criteria from 1-10 and computes a weighted total.

## Criteria And Weights

- Intent Match: `0.25`
- Design Quality: `0.25`
- Originality: `0.20`
- Craft: `0.15`
- Functionality: `0.15`

## Weighted Score

```text
weighted_score =
  intent_match * 0.25 +
  design_quality * 0.25 +
  originality * 0.20 +
  craft * 0.15 +
  functionality * 0.15
```

Round to one decimal place for reporting.

## Hard Gates

The harness cannot PASS unless all of these are true:

- Intent Match `>= 7`
- Design Quality `>= 7`
- Originality `>= 6`
- Craft `>= 6`
- Functionality `>= 6`
- Weighted score `>= 7.2`

High-weight criteria are not optional. A strong weighted average does not override a failed hard gate.

## Criterion Definitions

### 1. Intent Match

Does the output match the user's stated goal, references, and the run spec?

| Score | Description |
|-------|-------------|
| 1-3 | Barely recognizable as the intended design. Wrong mood, wrong structure, wrong hierarchy. |
| 4-5 | Some overlap with intent, but key design language or structure is off. |
| 6 | Recognizable intent, but meaningful mismatches remain in layout, tone, or information hierarchy. |
| 7-8 | Clearly aligned to the intent and spec. Minor deviations remain. |
| 9-10 | Feels like an expert interpretation of the brief. Strong fidelity with well-judged decisions. |

### 2. Design Quality

Does the design feel coherent, intentional, and aesthetically strong as a whole?

| Score | Description |
|-------|-------------|
| 1-3 | Generic, visually weak, or incoherent. |
| 4-5 | Functional but bland. Some design decisions exist, but they do not form a strong whole. |
| 6 | Solid and reasonably coherent, but not yet compelling or premium. |
| 7-8 | Cohesive, polished, and distinctive enough to ship confidently. |
| 9-10 | Strong enough that a designer would study it. Clear identity and excellent control. |

### 3. Originality

Is the work making deliberate, non-template decisions, or does it read like default AI output?

| Score | Description |
|-------|-------------|
| 1-3 | Template output, library defaults, or obvious AI slop. |
| 4-5 | Some custom decisions, but still heavily derivative or safe. |
| 6 | A few deliberate choices, but not enough to feel truly ownable. |
| 7-8 | Noticeably custom and intentional. Avoids common AI default patterns. |
| 9-10 | Surprising in the right way. Feels authored, not assembled. |

### 4. Craft

Is the technical execution precise and professionally controlled?

| Score | Description |
|-------|-------------|
| 1-3 | Misaligned, inconsistent, or visibly broken fundamentals. |
| 4-5 | Mostly usable, but spacing, rhythm, or contrast issues are visible. |
| 6 | Competent, with a few noticeable inconsistencies. |
| 7-8 | Clean execution with strong hierarchy, spacing, and polish. |
| 9-10 | Exceptionally controlled implementation. Tiny details hold up under scrutiny. |

### 5. Functionality

Can a user understand the page, find primary actions, and complete likely tasks without friction?

| Score | Description |
|-------|-------------|
| 1-3 | Broken or confusing enough to block normal use. |
| 4-5 | Usable but visibly awkward or unclear at important moments. |
| 6 | Mostly works, but there is meaningful friction or breakpoint weakness. |
| 7-8 | Clear, reliable, and responsive. Good enough to ship. |
| 9-10 | Extremely smooth, intuitive, and confidence-inspiring. |

## AI Slop Indicators

Penalize originality and design quality when you see:

- purple gradients on white cards
- default system fonts with no typographic point of view
- generic hero + card-grid layouts
- evenly distributed spacing with no rhythm
- visual style that could belong to any SaaS landing page
- decorative motion with no compositional role

## Anchor Interpretation

Use these anchors consistently:

- `5` = acceptable prototype, not ship quality
- `6` = promising but still meaningfully weak
- `7` = ship-worthy
- `8` = strong
- `9-10` = exceptional

Do not inflate scores because the implementation is "pretty good for AI."

## Evaluator Confidence

In addition to the numeric score, record confidence from `low`, `medium`, or `high`.

Lower confidence if:
- only one viewport was captured
- interactive states were not tested
- screenshots are stale, cropped, or ambiguous
- the references themselves are incomplete
