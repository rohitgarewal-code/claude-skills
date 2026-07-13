---
name: session-management
description: Cross-agent session continuity — persist project context in .state/ so Claude, Codex, Grok, and Cursor sessions can hand off work to each other. Use at the START of a session to load context (especially if another agent wrote it), when the user asks "where were we?", and at the END when the user says "wrap up", "save the session", or "I'm done".
allowed-tools: Read, Write, Edit, Glob, Bash
---

# Session Management (cross-agent)

This skill is one entry point to a shared, tool-agnostic protocol. The protocol —
not this file — is the source of truth:

1. **Read `.state/PROTOCOL.md` at the repo root and follow it exactly.**
2. If it doesn't exist, this project isn't initialized yet: copy the canonical
   template from `~/.claude/skills/session-management/PROTOCOL.md` to
   `.state/PROTOCOL.md`, then follow it (it covers first-session bootstrap).

The same protocol can be wired into other CLIs (`~/.codex/AGENTS.md` + `/wrap-up`
prompt for Codex; Grok discovers this very skill via its Claude-compat scan), so
any of them may have written the state you're reading, and any of them will read
the state you write — **but only if they're wired**. Installing this skill wires
Claude Code only; Codex in particular does not scan `~/.claude/skills/` and stays
a blind spot until configured. See `INSTALL.md` (next to this file) for the
per-CLI wiring blocks.

**First use on a machine — wiring check.** The first time this skill runs on a
given machine (or whenever unsure), check the other CLIs' wiring:
`~/.codex/AGENTS.md` and `~/.grok/AGENTS.md` should contain a
"Cross-agent session state" section, and `~/.codex/prompts/wrap-up.md` should
exist. If any CLI is installed but unwired, tell the user it's a one-way blind
spot (it won't read or write handoff state) and offer to apply the blocks from
`INSTALL.md` — with their go-ahead, since it edits another tool's config.

## Notes for Claude Code specifically

- **Identify yourself** in `last_session.agent` and log lines as
  `claude/<model>` (e.g. `claude/fable-5`, `claude/opus-4.8`).
- **Read-side shortcut:** if `last_session.agent` is also `claude/*`, your
  auto-memory and the project's PROGRESS.md convention already cover most of it —
  skip the summary ceremony, confirm briefly. If it's `codex/*` or `grok/*`,
  treat the state as fresh intel and summarize it to the user.
- **This does not replace project conventions.** Where a repo mandates
  `docs/PROGRESS.md` updates on commits, do both — PROGRESS.md is repo history,
  `.state/` is the cross-agent handoff snapshot.
- Honor repo rules on committing: stage only the `.state/` files, commit locally,
  never push.
