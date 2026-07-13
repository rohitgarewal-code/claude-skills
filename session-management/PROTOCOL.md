# Cross-Agent Session Protocol

This protocol keeps a software project's context alive across separate coding-agent
sessions — including sessions run by **different models/CLIs** (Claude Code, Codex,
Grok, Cursor). Any agent can write state at session end; any agent can read it at
session start. The state files are the interchange format between models that
otherwise share no memory.

Canonical template: `~/.claude/skills/session-management/PROTOCOL.md`.
Each project keeps its own copy at `.state/PROTOCOL.md` (copied on first use so the
repo is self-contained). If the two ever diverge, the repo copy wins for that repo.

## Layout — state is per-workstream

State lives under `.state/` at the repo root, **keyed by branch** so parallel
workstreams (including git worktrees) never clobber each other and never merge-conflict:

```
.state/
  PROTOCOL.md              # this file (repo copy)
  <branch-slug>/           # branch name with "/" replaced by "-"
    state.json             # current state for this workstream (small, always read)
    log.jsonl              # append-only, one line per session
    archive.json           # evicted narratives; NOT read at session start
```

Example: branch `feature/mentat-extension` → `.state/feature-mentat-extension/`.

## What does NOT live here

- **The durable backlog.** That belongs in the project's tracker (for this kind of
  repo: `_bmad-output/implementation-artifacts/{active,backlog,done}/`, issues, etc.).
  `state.json` carries only a `backlog_ref` pointer and the short-term
  `next_session_should` hint. Do not maintain a shadow backlog in state — it rots.
- **Durable rules and constraints.** Those live in `AGENTS.md` / `CLAUDE.md`;
  `handoff.constraints_doc` points at them.
- **Secrets.** Never. These files are committed.

## state.json shape

```json
{
  "workstream": "qa",
  "phase_narrative": "Session 12 (2026-07-11): shipped X | PRIOR — Session 11 (2026-07-09): refactored Y",
  "last_session": {
    "agent": "claude/fable-5",
    "session_number": 12,
    "date": "2026-07-11",
    "summary": "One-paragraph recap.",
    "work_completed": ["Shipped X", "Fixed Y"],
    "next_session_should": ["Start Z", "Re-run evals for W"]
  },
  "handoff": {
    "branch": "qa",
    "worktree": ".",
    "unpushed_commits": 3,
    "uncommitted_changes": false,
    "in_flight": ["executor swap gated on answer-quality A/B"],
    "gotchas": ["dev proxy adds ~180ms/round-trip — attribute latency by class"],
    "constraints_doc": "AGENTS.md",
    "backlog_ref": "_bmad-output/implementation-artifacts/active/"
  }
}
```

`agent` identifies the writer: `claude/fable-5`, `claude/opus-4.8`, `codex/gpt-5.6`,
`grok/grok-4.5`, etc. Use your actual model id; this drives the read-side rule below
and lets humans calibrate trust per entry.

## Session Start Protocol

1. Determine the current branch (`git branch --show-current`), slug it, and read
   `.state/<slug>/state.json`.
   - No `.state/` at all → this project isn't initialized. Copy the canonical
     PROTOCOL.md to `.state/PROTOCOL.md`, create `.state/<slug>/` with an empty
     `state.json` skeleton, `log.jsonl`, and `archive.json` (`{"phase_narrative_history": []}`),
     and treat this as session 1.
   - `.state/` exists but no dir for this branch → new workstream; initialize it
     (session 1 for this workstream).
2. Apply the read-side rule:
   - `last_session.agent` is a **different agent family than you** → read carefully;
     this is context your own memory does not have. Summarize it to the user.
   - Same family as you, and your harness has its own persistent memory (e.g.
     Claude Code auto-memory) → the state is likely redundant with what you already
     know; skip the ceremony, confirm briefly.
3. Summary format when you do summarize:
   ```
   Session resumed (last written by <agent>, <date>).
   Workstream: <branch> — <one-line from phase_narrative head>
   In flight: <handoff.in_flight>
   Next priority: <top of next_session_should>
   ```

## Session End Protocol

**Trigger:** the user says "wrap up", "wrap up the session", "save the session",
or "I'm done". Execute these steps in order.

1. **Gather evidence.** `git log --oneline` since `last_session.date`, plus
   `git status`. Base the summary on what actually happened, not on memory.
2. **Carry forward or file — never drop.** Read the *outgoing*
   `last_session.next_session_should`. Every item is either (a) done this session
   (goes in `work_completed`), (b) still pending (carries into the *new*
   `next_session_should`), or (c) bigger than a hint (file it in the project
   backlog at `backlog_ref`, and say so). `last_session` is a single-slot field —
   anything tracked only there dies on the next overwrite.
3. **Rewrite `state.json`:**
   - `last_session`: your agent id, incremented `session_number`, today's date,
     summary, `work_completed`, new `next_session_should`.
   - `handoff`: refresh every field — branch, worktree path,
     `unpushed_commits` (`git rev-list --count @{upstream}..HEAD`, or 0),
     `uncommitted_changes`, `in_flight`, `gotchas` (things the next agent — possibly
     a different model with no memory of this project — must know to not waste an hour).
4. **Prepend the narrative and cap at 10 (every session, not "when big").**
   Prepend `Session N (date): <one-line>` to `phase_narrative`, joining prior
   entries with ` | PRIOR — `. Split on `" | PRIOR — "`; if more than 10 entries,
   keep the newest 10 and append the evicted ones — oldest first, parsed as
   `{session, date, narrative}` — to `archive.json`'s `phase_narrative_history`.
5. **Append one line to `log.jsonl`:**
   ```json
   {"session": N, "agent": "<id>", "date": "YYYY-MM-DD", "summary": "...", "work_completed": ["..."], "next_actions": ["..."]}
   ```
6. **Commit ONLY the state files, locally.**
   ```bash
   git add .state/<slug>/state.json .state/<slug>/log.jsonl .state/<slug>/archive.json
   git commit -m "chore(state): session N (<agent>) — <brief summary>"
   ```
   Never `git add -A`. **NEVER push** — the user pushes when ready. Never switch
   branches to commit state; it belongs on the workstream's own branch.
7. **Confirm to the user:**
   ```
   Session N saved (<agent>).
   - Completed: [...]
   - Next session should: [...]
   - Filed to backlog: [...] (if any)
   ```

## Concurrency

Isolation is **between workstreams, not within one**. Parallel sessions on
different branches/worktrees never touch each other's state. Parallel sessions in
the *same* checkout share that branch's state files with no locking:

- Always perform the Session End Protocol as a read-modify-write **at wrap-up
  time** (the steps above already do this) — never from state remembered at
  session start. Sequential wrap-ups then compose: the later one carries the
  earlier one's pending items and preserves its narrative as a PRIOR entry.
- Near-simultaneous wrap-ups are last-writer-wins on `state.json`. `log.jsonl`
  is append-only, so no session's record is ever lost — the snapshot just heals
  on the next wrap-up. If `git` reports an index.lock conflict, another session
  is wrapping up: wait and redo from step 1.
- Users: run truly parallel efforts in separate worktrees; in a shared
  directory, wrap up one session at a time. Sessions with nothing worth handing
  off may skip wrap-up entirely.

## Key Principles

1. **Every agent writes at end; every agent reads at start.** The file exists so
   Fable knows what Grok did last night, and vice versa.
2. **Verify against code, not memory** — summaries derive from `git log`, not recall.
3. **State is a handoff snapshot, not a second source of truth** — backlog and rules
   live in their own homes; state points at them.
4. **Bound what grows** — cap the narrative at 10 every session; archive the rest.
5. **Commit locally, never push, never touch other branches.**
