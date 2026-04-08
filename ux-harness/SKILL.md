---
name: ux-harness
description: Use when building frontend UX from design intent — orchestrates a self-improving planner, generator, evaluator feedback loop with chrome-cdp visual testing, contract negotiation, trajectory tracking, and weighted scoring with hard quality gates
---

# UX Harness — Self-Improving Design-to-Code Pipeline

Run a repeatable UX harness:
1. Plan from intent
2. Negotiate an iteration contract
3. Generate UI code
4. Capture screenshots and interactive evidence
5. Evaluate with a separate calibrated evaluator
6. Record weighted scores and best-so-far trajectory
7. Decide refine vs pivot
8. Iterate until hard gates pass or the run plateaus
9. Persist learnings for future runs

Use this for frontend work where visual quality matters enough to justify a real evaluation loop. Do not use for quick throwaway prototypes.

## When To Use

- User asks for a polished frontend page, component, or app from design intent
- User provides references such as images, URLs, or existing brand language
- UX quality matters enough to justify multiple scored iterations
- Automated screenshots, page inspection, or browser interaction are needed during the loop; pair this skill with `/chrome-cdp`

## What Makes This A Harness

This skill is not "generate and eyeball."

It uses:
- a **planner** to turn intent into a concrete spec
- a **generator** to build the UI
- a separate **evaluator** to score the output skeptically
- a **coordinator** to track trajectory, enforce gates, and choose refine vs pivot

The evaluator must be independent from the generator. The latest iteration is not automatically the best iteration.

## Prerequisites

- Chrome with remote debugging enabled (for /chrome-cdp screenshots)
- Node.js 22+ (for cdp.mjs scripts)
- If screenshot tooling is unavailable, request screenshots from the user and continue with reduced visual confidence

## Inputs

Capture these up front:
- Prompt text (required)
- Reference images (optional, `--ref <path>`)
- Reference URLs (optional, `--url <url>`)
- `--max-iterations <N>` (default `5`)
- `--quality-target <N>` (default weighted score `7.2`)

## Run Artifacts

For each run, create:

- `.harness/ux/run-N/design-intent/prompt.md`
- `.harness/ux/run-N/design-intent/references/*`
- `.harness/ux/run-N/spec.md`
- `.harness/ux/run-N/trajectory.json`
- `.harness/ux/run-N/best.json`
- `.harness/ux/run-N/critique-1.md ... critique-N.md`
- `.harness/ux/run-N/contracts/iter-I.md`
- `.harness/ux/run-N/iterations/iter-I/scores.json`
- `.harness/ux/run-N/iterations/iter-I/evidence.json`
- `.harness/ux/run-N/iterations/iter-I/decision.json`
- `.harness/ux/run-N/screenshots/*`
- `.harness/ux/run-N/summary.json`

Learning stores:

- `~/.claude/harness/ux/taste.json`
- `~/.claude/harness/ux/anti-patterns.json`
- `~/.claude/harness/ux/calibration.json`
- `.harness/ux/patterns.json`

## Workflow

### Phase 1: Setup

1. Create the next run directory:
   ```bash
   RUN_N=$(ls -d .harness/ux/run-* 2>/dev/null | wc -l | tr -d ' ')
   RUN_N=$((RUN_N + 1))
   RUN_DIR=".harness/ux/run-${RUN_N}"
   mkdir -p "${RUN_DIR}/design-intent/references" "${RUN_DIR}/screenshots" "${RUN_DIR}/contracts" "${RUN_DIR}/iterations"
   ```
2. Write prompt text to `design-intent/prompt.md`.
3. Copy reference images into `design-intent/references/`.
4. If URLs are provided, use `/chrome-cdp` to capture screenshots into `design-intent/references/`.
5. Load existing learning JSON files if present; otherwise use empty defaults.
6. Read reference files for prompt injection:
   - `~/.claude/skills/ux-harness/references/spec-format.md`
   - `~/.claude/skills/ux-harness/references/critique-format.md`
   - `~/.claude/skills/ux-harness/references/scoring-rubric.md`
   - `~/.claude/skills/ux-harness/references/frontend-design.md`
   - `~/.claude/skills/ux-harness/references/calibration-examples.md`
   - `~/.claude/skills/ux-harness/prompts/coordinator.md` (read as reference, not dispatched)

### Phase 2: Plan (Planner Role)

1. Dispatch Planner subagent via Agent tool:
   - description: "Plan UX: [first 50 chars of prompt]"
   - prompt: Read `prompts/planner.md` and substitute all `{{VARIABLES}}`
2. Verify `${RUN_DIR}/spec.md` exists and is non-empty.
3. If missing: retry once with reduced context, then ask user.

### Phase 3: Generate/Evaluate Loop

**Create worktree (once, before first iteration):**
```bash
BRANCH_NAME="ux-harness/run-${RUN_N}"
WORKTREE_DIR=".claude/worktrees/ux-harness-run-${RUN_N}"
git worktree add "${WORKTREE_DIR}" -b "${BRANCH_NAME}"
```

For iteration `i` from `1..max_iterations`:

**Step 1 — Negotiate the iteration contract:**

Dispatch contract-generator subagent via Agent tool:
- description: "Propose iteration N contract"
- prompt: Read `prompts/contract-generator.md`, substitute `{{VARIABLES}}`
- The subagent writes `${RUN_DIR}/contracts/iter-${i}.md` (draft)

Dispatch contract-evaluator subagent via Agent tool:
- description: "Tighten iteration N contract"
- prompt: Read `prompts/contract-evaluator.md`, substitute `{{VARIABLES}}`
- The subagent rewrites `${RUN_DIR}/contracts/iter-${i}.md` (final)

Verify contract file exists and is non-empty.

**Step 2 — Generate implementation:**

Dispatch Generator subagent via Agent tool:
- description: "Generate UX iteration N"
- Iteration 1: read `prompts/generator.md`
- Iteration 2+: read `prompts/generator-iterate.md`
- Substitute all `{{VARIABLES}}` including `{{RUN_DIR}}`, `{{WORKTREE_DIR}}`, contract path, anti-patterns, taste, design guidelines
- For iteration 2+: include previous critique, scores.json, evidence.json, decision.json, best.json paths

Create `${RUN_DIR}/iterations/iter-${i}/` directory before dispatching.

**Step 3 — Run the UI locally:**

```bash
cd "${WORKTREE_DIR}" && python3 -m http.server 8765 &
# OR if Vite: cd "${WORKTREE_DIR}" && npm run dev -- --port 8765 &
```

**Step 4 — Capture screenshots:**

```bash
CDP=~/.claude/skills/chrome-cdp/scripts/cdp.mjs
$CDP list
$CDP nav <target> http://localhost:8765
$CDP shot <target> ${RUN_DIR}/screenshots/iter-${i}-desktop.png
```

Follow the `/chrome-cdp` skill workflow. Save screenshots into the current run's `screenshots/` directory.

**Step 5 — Evaluate:**

Dispatch Evaluator subagent via Agent tool:
- description: "Evaluate UX iteration N"
- prompt: Read `prompts/evaluator.md`, substitute `{{VARIABLES}}`
- Include: screenshot paths, spec, contract, calibration examples, scoring rubric, critique format
- For iteration 2+: include previous critiques and trajectory/best.json

The evaluator writes three files:
- `${RUN_DIR}/critique-${i}.md`
- `${RUN_DIR}/iterations/iter-${i}/scores.json`
- `${RUN_DIR}/iterations/iter-${i}/evidence.json`

Verify all three exist.

**Step 6 — Run coordinator logic:**

Read `prompts/coordinator.md` as a reference for heuristics. The coordinator is YOU (the orchestrator), not a separate subagent. Execute this logic:

a. Read `${RUN_DIR}/iterations/iter-${i}/scores.json` for structured scoring data.

b. Append to `${RUN_DIR}/trajectory.json`:
```json
{
  "iterations": [
    {
      "iteration": 1,
      "weighted_score": 6.4,
      "hard_gate_pass": false,
      "recommendation": "PIVOT_AESTHETIC_DIRECTION"
    }
  ]
}
```

c. Compare current weighted score to `${RUN_DIR}/best.json`. Update best.json if:
   - Current iteration scores higher, OR
   - Current iteration passes hard gates and previous best did not

d. Write `${RUN_DIR}/iterations/iter-${i}/decision.json`:
```json
{
  "iteration": 1,
  "status": "ITERATE",
  "next_action": "REFINE_CURRENT_DIRECTION",
  "reason": "core direction is right, but craft issues remain",
  "best_iteration_so_far": 1
}
```

e. Termination conditions (any → STOP):
   1. All hard gates pass (see `references/scoring-rubric.md`)
   2. Iteration count >= max_iterations
   3. Weighted score improved < 0.3 across last 2 completed iterations (plateau)
   4. Evaluator confidence is "low" → STOP_LOW_CONFIDENCE

f. If ITERATE, choose direction:
   - `REFINE_CURRENT_DIRECTION` when scores are trending up and direction is fundamentally right
   - `PIVOT_AESTHETIC_DIRECTION` when intent match, design quality, or originality are stalled or structurally weak

**Between iterations:** Kill the dev server before restarting.

### Phase 4: Termination

Stop when any condition is true:
- Current iteration passes all hard gates in `references/scoring-rubric.md`
- `i >= max_iterations`
- Best weighted score improved by less than `0.3` across the last two completed iterations
- Evaluator confidence is too low to continue

Do not assume the final iteration is the winner. Use `best.json` to choose the best iteration.

**Merge worktree:**

If best iteration is not the final iteration, checkout the best iteration's commit before merging:
```bash
cd "${WORKTREE_DIR}" && git log --oneline  # find the best iteration's commit
# If needed: git checkout <best-commit>
```

Then merge:
```bash
git merge "${BRANCH_NAME}" --no-edit
git worktree remove "${WORKTREE_DIR}"
git branch -d "${BRANCH_NAME}"
```

### Phase 5: Learning Update

Dispatch Learning subagent via Agent tool with `run_in_background: true`:
- description: "Learn from UX harness run"
- prompt: Read `prompts/learning.md`, substitute all `{{VARIABLES}}`
- Include: run directory, iteration count, final scores, score trajectory, all learning store paths

Initialize learnings stores if they don't exist:
```bash
mkdir -p ~/.claude/harness/ux .harness/ux/history
[ -f ~/.claude/harness/ux/taste.json ] || echo '{"preferences":[],"last_updated":""}' > ~/.claude/harness/ux/taste.json
[ -f ~/.claude/harness/ux/anti-patterns.json ] || echo '{"patterns":[]}' > ~/.claude/harness/ux/anti-patterns.json
[ -f ~/.claude/harness/ux/calibration.json ] || echo '{"examples":[],"max_examples":5}' > ~/.claude/harness/ux/calibration.json
[ -f .harness/ux/patterns.json ] || echo '{"conventions":[]}' > .harness/ux/patterns.json
```

## Scoring System

The evaluator scores five criteria:
- Intent Match (weight 0.25)
- Design Quality (weight 0.25)
- Originality (weight 0.20)
- Craft (weight 0.15)
- Functionality (weight 0.15)

The coordinator computes:
- weighted score
- hard gate pass/fail
- regression flags
- evaluator confidence
- best-so-far iteration
- next action: `REFINE_CURRENT_DIRECTION` or `PIVOT_AESTHETIC_DIRECTION`

The weighted score is not enough on its own. Hard gates matter.

## Iteration Contract Rule

Every iteration must have a contract before implementation begins.

The contract is a short generator-evaluator agreement that defines:
- the iteration goal
- the score movement or hard gate to address
- what strengths must be preserved
- what evidence must be captured
- what success looks like for this round

This prevents the generator from drifting and gives the evaluator a concrete basis for failure.

## Refine Vs Pivot Rule

The generator should not always keep polishing the current direction.

Use `decision.json`:
- `REFINE_CURRENT_DIRECTION` when scores are trending up and the evaluator believes the direction is fundamentally right
- `PIVOT_AESTHETIC_DIRECTION` when intent match, design quality, or originality are stalled or structurally weak

Pivots should preserve spec compliance while changing the visual or structural approach meaningfully.

## Screenshot Capture Guidance

```bash
CDP=~/.claude/skills/chrome-cdp/scripts/cdp.mjs
$CDP list
$CDP nav <target> http://localhost:8765
$CDP shot <target> .harness/ux/run-N/screenshots/iter-I-desktop.png
```

Follow the `/chrome-cdp` skill's workflow. If no screenshots are available, explicitly lower visual confidence in the critique.

## Quality Rules

- Separate generation from evaluation thinking
- The evaluator must be skeptical, not collaborative
- Every critique issue must include a specific fix
- Evaluate against the spec and user references, not personal preference
- Penalize generic "AI slop" explicitly
- Record why scores moved, not just the scores themselves
- Always preserve a best-so-far snapshot in case later iterations regress

## Files To Load On Demand

- Prompt templates:
  - `prompts/planner.md`
  - `prompts/contract-generator.md`
  - `prompts/contract-evaluator.md`
  - `prompts/generator.md`
  - `prompts/generator-iterate.md`
  - `prompts/evaluator.md`
  - `prompts/coordinator.md`
  - `prompts/learning.md`
- References:
  - `references/spec-format.md`
  - `references/critique-format.md`
  - `references/scoring-rubric.md`
  - `references/frontend-design.md`
  - `references/calibration-examples.md`

Load only what is needed for the active phase.

## Expected Report

At completion, report:
- prompt summary
- iteration count
- best iteration number
- final per-criterion scores
- weighted score
- verdict: `PASS`, `PLATEAU`, `MAX_ITERATIONS`, or `STOP_LOW_CONFIDENCE`
- run artifacts directory
- major fixes that moved the score
- key learnings added or updated

## Composition with Existing Skills

- The generator's prompt includes `/frontend-design` aesthetic guidelines (inlined, since subagents can't invoke skills)
- `/design-consultation` can produce a DESIGN.md beforehand that this harness reads as input
- `/design-shotgun` can be used independently for exploration before invoking the harness
- `/chrome-cdp` is used by the coordinator for all screenshot capture

## Troubleshooting

**Chrome not connected:** Ensure remote debugging is enabled in Chrome (chrome://inspect/#remote-debugging). Run `cdp.mjs list` to verify.

**Dev server won't start:** Check what the generator built. If it's plain HTML, use `python3 -m http.server`. If it's Vite/React, use `npm run dev`.

**Scores not improving:** Check if the evaluator's feedback is actionable enough. Read the critique files. Consider a PIVOT if the same structural issues repeat across 2+ iterations.

**Worktree conflicts:** If the merge fails, resolve conflicts manually. The worktree branch has all the generated code. Use `best.json` to identify the best iteration's commit.
