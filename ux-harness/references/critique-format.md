# Critique Format

The evaluator MUST output a file named `critique-N.md` (where N is the iteration number) in the run directory with this exact structure. Every section is required.

## Template

# Critique — Iteration [N]

## Scores
- Design Fidelity: [X]/10
- Visual Quality: [X]/10
- Craft: [X]/10
- Functionality: [X]/10

## Score Justifications
[One sentence per criterion explaining the score. Reference specific elements.]

- **Design Fidelity**: [justification]
- **Visual Quality**: [justification]
- **Craft**: [justification]
- **Functionality**: [justification]

## What Works
[List specific elements that match the design intent well. Be concrete.]

1. [Element + why it works]
2. [Element + why it works]

## Issues (Actionable)
[Each issue MUST include a specific fix. The generator should not need to investigate — just implement.]

1. **[Issue summary]** — [Exact fix: what to change, where, and to what value]
2. **[Issue summary]** — [Exact fix]

## Regression Check (Iteration 2+ only)
[For each issue from the previous critique, confirm whether it was fixed.]

- [Previous issue 1]: FIXED / NOT FIXED / PARTIALLY FIXED
- [Previous issue 2]: FIXED / NOT FIXED / PARTIALLY FIXED

## Verdict: [ITERATE / PASS]

[If ITERATE: which issues are blocking? Which scores need to improve?]
[If PASS: confirm all criteria meet threshold.]
