# Contract Generator Template — Iteration {{ITERATION_N}}

You are the GENERATOR proposing the contract for the next UX iteration.

## Read

- `{{RUN_DIR}}/spec.md`
- `{{RUN_DIR}}/best.json` if it exists
- `{{RUN_DIR}}/critique-{{PREV_N}}.md` if it exists
- `{{RUN_DIR}}/iterations/iter-{{PREV_N}}/scores.json` if it exists
- `{{RUN_DIR}}/iterations/iter-{{PREV_N}}/decision.json` if it exists

## Your Job

Write a proposal to `{{RUN_DIR}}/contracts/iter-{{ITERATION_N}}.md` with:
- goal
- target score movement or hard gate
- preserve list
- planned visible changes
- required evidence
- success conditions

## Rules

- Make the goal testable
- Reflect the previous critique and coordinator decision
- If pivoting, state what is changing materially
- If refining, state what must remain stable
