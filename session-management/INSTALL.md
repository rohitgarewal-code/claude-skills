# Installing session-management across CLIs

The `.state/` protocol only delivers cross-agent continuity if **every** CLI on
the machine is wired to it. Installing this skill into `~/.claude/skills/` wires
Claude Code — and, via Claude-compat discovery, usually Grok — but **Codex does
NOT scan `~/.claude/skills/` and knows nothing about the protocol until you wire
it explicitly.** An unwired CLI is a one-way blind spot: it neither reads the
state others wrote nor writes state others can pick up.

Per-CLI status after copying this directory to `~/.claude/skills/session-management/`:

| CLI | Wired by the copy? | Action needed |
|-----|--------------------|---------------|
| Claude Code | ✅ Yes | None |
| Grok | ✅ Usually (Claude-compat scan) | Optional but recommended: explicit `~/.grok/AGENTS.md` block (below) |
| Codex | ❌ **No** | Required: `~/.codex/AGENTS.md` block + `~/.codex/prompts/wrap-up.md` (below) |
| Cursor | ❌ No | Adapt the same block into your Cursor global rules |

## Codex (required — two files)

**1. Append to `~/.codex/AGENTS.md`** (create it if missing; Codex loads this as
global instructions in every session):

```markdown
## Cross-agent session state

Projects I work on may persist session context in a `.state/` directory at the
repo root, shared between coding agents (Claude Code, Codex, Grok). It is how you
learn what another model did in a previous session, and how you hand your work off.

- **At session start:** if `.state/` exists, read
  `.state/<branch-slug>/state.json` (branch name with `/` → `-`). If
  `last_session.agent` is not `codex/*`, that context is not in your history —
  summarize it to the user before starting work.
- **When the user says "wrap up", "save the session", or "I'm done":** read
  `.state/PROTOCOL.md` and execute its Session End Protocol. Identify yourself as
  `codex/<model>` (e.g. `codex/gpt-5.6`). Commit only the `.state/` files,
  locally. NEVER push.
- If the project has no `.state/` yet and the user asks for session management,
  bootstrap it by copying `~/.claude/skills/session-management/PROTOCOL.md` to
  `.state/PROTOCOL.md` and following it.
```

**2. Create `~/.codex/prompts/wrap-up.md`** (gives Codex a `/wrap-up` prompt as
an explicit entry point):

```markdown
Wrap up this coding session and persist state for cross-agent handoff.

Read `.state/PROTOCOL.md` at the repo root and execute its **Session End
Protocol** exactly, step by step. Key points:

- Identify yourself as `codex/<model>` (e.g. `codex/gpt-5.6`) in
  `last_session.agent` and in the `log.jsonl` entry.
- State is per-workstream: current branch, `/` replaced with `-`, under
  `.state/<branch-slug>/`.
- Base the summary on `git log` and `git status` since the last session's date —
  evidence, not memory.
- Refresh the `handoff` block fully (unpushed commits, in-flight work, gotchas the
  next agent — possibly a different model — needs).
- Carry forward or file every pending `next_session_should` item; never drop one.
- Cap `phase_narrative` at 10 entries; evict older ones to `archive.json`.
- Commit ONLY the `.state/` files, locally. **NEVER push.**

If `.state/PROTOCOL.md` does not exist, copy it from
`~/.claude/skills/session-management/PROTOCOL.md` first, initialize
`.state/<branch-slug>/` per its bootstrap instructions, and treat this as session 1.
```

## Grok (recommended)

Grok auto-discovers this skill by scanning `~/.claude/skills/` as a
Claude-compat source (lowest priority), so it usually works with no action. For
robustness — the scan is lowest-priority and discovery behavior can change —
append the same block to `~/.grok/AGENTS.md`, with two substitutions: the agent
check becomes `grok/*` and the identity becomes `grok/<model>` (e.g.
`grok/grok-4.5`). Also add this parenthetical after the intro paragraph so Grok
doesn't treat the skill and the AGENTS.md block as two different protocols:

```markdown
(You may also see this as the `session-management` skill via Claude-compat — same
protocol; `.state/PROTOCOL.md` is the source of truth.)
```

## Cursor

Cursor has no global AGENTS.md equivalent with the same semantics; adapt the
Codex block into your Cursor global rules (Settings → Rules, or a shared rules
file), substituting `cursor/<model>` as the identity.

## Verify

After wiring, check each of these on the installing machine:

```bash
ls ~/.claude/skills/session-management/            # SKILL.md, PROTOCOL.md, INSTALL.md
grep -l "Cross-agent session state" ~/.codex/AGENTS.md ~/.grok/AGENTS.md
ls ~/.codex/prompts/wrap-up.md
```

A CLI missing from this list simply won't participate — state written by others
is invisible to it, and its sessions leave no handoff. Fix the wiring before
relying on the protocol across tools.
