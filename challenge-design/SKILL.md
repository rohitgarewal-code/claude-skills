---
name: challenge-design
description: Launch defender and challenger agents to pressure-test a major design decision. Both agents debate, then a winner is declared with reasoning.
allowed-tools: Task, Read, Glob, Grep
---

# Design Challenger

Pressure-test any major design (architecture, data model, API shape, component structure) by running a structured adversarial debate between two agents.

## When to invoke

- After creating or proposing a major design
- Before committing to an architecture or data model
- When choosing between multiple approaches
- User can also invoke manually with `/challenge-design`

## Instructions

When this skill is invoked:

### 1. Identify the design to challenge

- If `$ARGUMENTS` is provided, use it as context for what design to challenge
- Otherwise, look at the recent conversation for the most recent design proposal, plan, or architectural decision
- Summarize the design in 2-3 sentences so both agents have shared context

### 2. Launch the Defender and Challenger agents in parallel

Use the Task tool to launch **two agents simultaneously** (in a single message with two Task tool calls):

**Agent A — Defender** (subagent_type: general-purpose):
```
You are the DEFENDER of this design. Your job is to argue why this is the right approach.

DESIGN UNDER REVIEW:
[paste the design summary and any relevant details]

Instructions:
1. Read any files referenced in the design to fully understand it
2. List 3-5 concrete strengths of this design (correctness, simplicity, extensibility, performance, alignment with existing patterns)
3. Anticipate likely criticisms and preemptively address them
4. Identify what would break or get worse if a different approach were taken
5. Score the design 1-10 on: Simplicity, Correctness, Extensibility, Performance, Developer Experience

Output your defense as a structured argument with evidence from the codebase.
```

**Agent B — Challenger** (subagent_type: general-purpose):
```
You are the CHALLENGER of this design. Your job is to propose a better alternative and argue why it wins.

DESIGN UNDER REVIEW:
[paste the design summary and any relevant details]

Instructions:
1. Read any files referenced in the design to fully understand it
2. Identify 3-5 concrete weaknesses, risks, or missed opportunities in the current design
3. Propose a specific alternative design (not vague — concrete enough to implement)
4. Argue why your alternative is superior on at least 2 of: Simplicity, Correctness, Extensibility, Performance, Developer Experience
5. Acknowledge what the original design does better than yours (steel-man the opponent)
6. Score BOTH designs 1-10 on: Simplicity, Correctness, Extensibility, Performance, Developer Experience

Output your challenge as a structured counter-proposal with evidence from the codebase.
```

### 3. Synthesize the debate

After both agents return, present the results to the user in this format:

```
## Design Challenge Results

### Original Design (Defender)
[Summarize Agent A's key arguments and scores]

### Alternative Design (Challenger)
[Summarize Agent B's key arguments, counter-proposal, and scores]

### Verdict: [ORIGINAL WINS / CHALLENGER WINS / HYBRID]

**Why this design wins:**
[2-3 sentences explaining the logical reasoning — which arguments were stronger, which trade-offs matter more for this project, and what evidence from the codebase supports the decision]

**Key insight from the debate:**
[The single most valuable thing learned from the adversarial process — a risk identified, a simplification discovered, or a trade-off made explicit]
```

### 4. Decision rules for the verdict

- If the challenger's alternative is strictly better on 3+ dimensions with no major downsides → **Challenger wins**
- If the original design holds up and the challenger only found minor issues → **Original wins**
- If both have clear strengths in different areas → **Hybrid** (specify which parts to take from each)
- Always explain the reasoning. Never declare a winner without justification.

### 5. After the verdict

- If the challenger or hybrid wins, ask the user: "Want me to revise the design based on this outcome?"
- If the original wins, note any minor improvements surfaced by the challenger that are worth incorporating

## Important

- Both agents MUST read relevant source files — no armchair arguments
- The challenger must propose a **concrete** alternative, not just criticize
- The defender must address real trade-offs, not just cheerleading
- The verdict must be based on logical reasoning, not popularity
- Keep the whole process focused — this should take minutes, not hours
