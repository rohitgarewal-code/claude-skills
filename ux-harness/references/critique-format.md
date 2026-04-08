# Critique Format

The evaluator MUST output `critique-N.md` with the exact structure below.

## Template

# Critique — Iteration [N]

## Scorecard
- Intent Match: [X]/10
- Design Quality: [X]/10
- Originality: [X]/10
- Craft: [X]/10
- Functionality: [X]/10
- Weighted Score: [X.X]/10
- Confidence: [low / medium / high]

## Hard Gate Status
- Intent Match >= 7: PASS / FAIL
- Design Quality >= 7: PASS / FAIL
- Originality >= 6: PASS / FAIL
- Craft >= 6: PASS / FAIL
- Functionality >= 6: PASS / FAIL
- Weighted Score >= 7.2: PASS / FAIL

## Evidence
[Concrete observations. Reference screenshots, breakpoints, and interactive states.]

- **Desktop**: [evidence]
- **Tablet**: [evidence]
- **Mobile**: [evidence]
- **Interaction Checks**: [evidence]

## Score Justifications
- **Intent Match**: [specific justification]
- **Design Quality**: [specific justification]
- **Originality**: [specific justification]
- **Craft**: [specific justification]
- **Functionality**: [specific justification]

## What Works
1. [Specific strength]
2. [Specific strength]

## Issues (Actionable)
1. **[Issue summary]** — [Exact fix: what to change, where, and to what]
2. **[Issue summary]** — [Exact fix]

## Regression Check (Iteration 2+ only)
- [Previous issue 1]: FIXED / PARTIALLY FIXED / NOT FIXED
- [Previous issue 2]: FIXED / PARTIALLY FIXED / NOT FIXED

## Contract Compliance
- Contract target addressed: YES / PARTIALLY / NO
- Required evidence captured: YES / PARTIALLY / NO
- Preserve requirements honored: YES / PARTIALLY / NO
- Notes: [short explanation]

## Direction Decision
- Recommendation: REFINE_CURRENT_DIRECTION / PIVOT_AESTHETIC_DIRECTION
- Reason: [why]

## Verdict: PASS / ITERATE / STOP_LOW_CONFIDENCE

[One short paragraph explaining the verdict.]
