# Workflow Orchestration

## 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately – don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

## 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution
- **ALWAYS assign subagent/workflow-agent models explicitly — never let them inherit the session model.** Inheriting silently runs high-volume work on whatever tier the session is on (e.g. Fable/Mythos-class), which is a large, avoidable cost. Assignment rule:
  - **All development — implementation, fixes, mechanical edits — → `opus` or `sonnet`** (opus for substantial coding, sonnet for smaller/mechanical tasks). This is the delegatable, high-volume work and it always goes to a subagent at one of these tiers.
  - **Design, planning, and verification/review → Fable — but ONLY when I have explicitly set Fable as the session model (or explicitly asked for Fable on a specific step).** These judgment-critical roles are the Fable main loop's job when I've chosen Fable; do NOT silently spawn Fable subagents by default. When Fable isn't set, keep design/planning/verification in the main loop at whatever model I've chosen, and delegate them to a Fable subagent only on my explicit say-so.
  - Applies to both the `Agent` tool (`model` param) and `Workflow` `agent()` calls (`opts.model`). Set it every time — the cost mistake is leaving it unset, and the second mistake is defaulting judgment work to Fable when I haven't asked for it.

## 3. Self-Improvement Loop
- After ANY correction from the user: update tasks/lessons.md with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

## 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

## 5. Design Challenger
- After creating any major design (architecture, data model, API shape), ask me whether to run `/challenge-design` before proceeding, and suggest a duration sized to the design (`--minutes`, default 60). Don't start it without a yes: a run is two agents debating for up to an hour.

## 5b. Jev Fit Check (every design, every project)
- Every design, spec or plan includes a **"Jev fit" section**: for each of the six Jev usage categories, whether Jev applies, where, with what questions, and how it would be tested. Load the `jev-fit` skill (`~/.claude/skills/jev-fit/SKILL.md`) before writing it — it holds what Jev can/can't do, the fit test, the design rules and the required table.
- Any LLM call in a design that only classifies, routes, scores or answers yes/no is a Jev candidate — say why if it stays an LLM call.
- "Doesn't fit" is a valid answer; skipping the check is not.

## 6. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes – don't over-engineer
- Challenge your own work before presenting it

## 7. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests – then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

---

# Task Management

1. **Plan First**: Write plan to tasks/todo.md with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to tasks/todo.md
6. **Capture Lessons**: Update tasks/lessons.md after corrections

---

# Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

---

# gstack

Use the /browse skill from gstack for all web browsing. Never use mcp__claude-in-chrome__* tools.

Available skills: /plan-ceo-review, /plan-eng-review, /review, /ship, /browse, /qa, /qa-only, /setup-browser-cookies, /retro

---

# Self-Improvement

If there are more elegant ways to automate workflows across projects, add them here to learn from them.
