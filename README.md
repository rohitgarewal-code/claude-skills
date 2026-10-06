# Claude Skills

A collection of [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) for knowledge management, design validation, and creative production. Nine skills organized into three groups: a **learning system** for capturing and retrieving knowledge, a **design system** for creating high-quality visual and frontend work, and a **workflow system** for cross-agent session continuity.

## Learning & Validation Skills

### `/challenge-design`

Pressure-tests a design with a **live debate**. A **defender** presents the design, and a **challenger** goes through it point by point proposing concrete alternatives. The two agents message each other directly. They first agree on a framework (criteria, the full topic list, what counts as evidence), then work topic by topic until they agree on a one-sentence resolution (keep / change / hybrid) or record a deadlock. The debate stops when every topic is aligned, when 90%+ are aligned and the rest are deadlocked, or after an hour. You get what they aligned on, what they couldn't, and the design with the aligned changes applied. There is no winner: the open items are yours to decide. Both agents must cite the code (no armchair arguments), and a concession needs a stated reason.

**Use when:** You're settling an architecture, data model, API shape, or workflow and want it argued out before you commit.

**Options:** `--minutes N` (default 60) · `--target P` (default 90%)

**Tools used:** `Agent`, `SendMessage`, `Bash`, `Read`, `Write`, `Glob`, `Grep`

---

### `/jev-fit`

Checks every design for where **Jev** (TypeSafe's cheap, fast judgment model: Choice / Score / yes-no questions at ~$0.04 per million input tokens and ~300 ms) should, or should not, be part of it. It carries what Jev can and cannot do, a four-question fit test, the six usage categories (analyze archives, search by meaning, triage, check against rules, speed up agents, respond instantly), rubric-design rules learned from real replays, how to measure a use before enforcing it, and a required six-row **Jev fit** table for every design. `/challenge-design`'s challenger checks that table.

**Use when:** writing any design, spec or plan, or whenever an LLM call only classifies, routes, scores or answers yes/no.

---

### `/compound-learning`

Documents a solved problem or discovered pattern into `docs/solutions/{category}/` with structured YAML frontmatter. Creates a searchable knowledge base that grows alongside your projects.

**Use when:** You've solved a non-trivial bug, discovered a gotcha, or established a pattern worth remembering.

**Categories:** `patterns` · `performance-issues` · `database-issues` · `runtime-errors` · `security-issues` · `deployment-issues` · `integration-issues` · `frontend-issues`

**Severity levels:** `critical` · `high` · `medium` · `low`

**Tools used:** `Read`, `Write`, `Glob`, `Grep`, `AskUserQuestion`

**Schema:** See [`compound-learning/schema.yaml`](compound-learning/schema.yaml) for the full frontmatter specification.

---

### `/learnings-researcher [query]`

Searches across all projects for previously documented solutions and patterns. Finds documents created by `compound-learning`, ranks them by relevance, and presents summaries with metadata.

**Use when:** You hit a problem that feels familiar, or want to check if your team has already solved something similar.

**Search path:** `~/dev/projects/*/docs/solutions/**/*.md`

**Tools used:** `Glob`, `Grep`, `Read`, `AskUserQuestion`

---

## Design Skills

### `/ux-design-agent`

A router that classifies design requests and delegates to the right specialist skill. Analyzes what you're asking for and sends it to `frontend-design`, `canvas-design`, or `theme-factory` — or chains multiple together for compound requests.

**Use when:** You want any kind of design work and don't want to pick the specific skill yourself.

**Routing logic:**
- Web UI (components, pages, dashboards) → `frontend-design`
- Static visuals (posters, artwork, infographics) → `canvas-design`
- Styling existing artifacts (slides, docs, reports) → `theme-factory`
- Compound requests are chained (e.g., "build a landing page with Ocean Depths theme" → `frontend-design` + `theme-factory`)

---

### `/frontend-design`

Creates distinctive, production-grade web interfaces that avoid generic AI aesthetics. Starts with a design thinking phase (purpose, audience, tone) before writing working code with intentional typography, cohesive color palettes, high-impact animations, and unexpected spatial composition.

**Use when:** You need a web component, page, dashboard, landing page, or any browser-rendered UI.

**Output:** Working HTML/CSS/JS, React, or Vue code.

**Tone options:** Brutally minimal · maximalist chaos · retro-futuristic · organic/natural · luxury/refined · playful/toy-like · editorial/magazine · brutalist/raw · art deco/geometric · soft/pastel · industrial/utilitarian

---

### `/canvas-design`

Creates museum-quality visual art as `.png` or `.pdf` files. First generates a design philosophy manifesto (an original aesthetic movement), then expresses it visually — 90% visual, 10% essential text, with repeating patterns, perfect shapes, and systematic visual language.

**Use when:** You need a poster, piece of art, brand visual, infographic, or any static visual piece.

**Output:** Design philosophy `.md` file + `.pdf` or `.png` artwork.

**Includes:** 54 curated TTF fonts across serif, sans-serif, display, and monospace families.

---

### `/theme-factory`

Applies consistent, professional styling to existing artifacts — slides, documents, reports, HTML pages. Choose from 10 curated themes or generate a custom one on the fly.

**Use when:** You have an existing artifact that needs a cohesive look.

**Built-in themes:**

| Theme | Palette | Best for |
|-------|---------|----------|
| Ocean Depths | Navy/teal | Corporate, finance |
| Sunset Boulevard | Burnt orange/coral | Creative, marketing |
| Forest Canopy | Green/sage | Environmental, wellness |
| Modern Minimalist | Grayscale | Tech, architecture |
| Golden Hour | Mustard/terracotta | Hospitality, artisan |
| Arctic Frost | Ice blue/silver | Healthcare, clean tech |
| Desert Rose | Dusty rose/clay | Fashion, beauty |
| Tech Innovation | Electric blue/cyan | Startups, AI/ML |
| Botanical Garden | Fern/marigold | Food, natural products |
| Midnight Galaxy | Deep purple/lavender | Entertainment, gaming |

---

## Workflow Skills

### `/session-management`

Cross-agent session continuity. Persists project context in a `.state/` directory at the repo root — keyed by branch so parallel workstreams never clobber each other — so that Claude Code, Codex, Grok, and Cursor sessions can hand off work to each other. Any agent writes state at session end ("wrap up"); any agent reads it at session start ("where were we?"). The skill is one entry point to a shared, tool-agnostic protocol: the repo's `.state/PROTOCOL.md` copy is the source of truth.

**Use when:** Starting a session (load context, especially if another agent/model wrote it), or ending one ("wrap up", "save the session", "I'm done").

**State layout:** `.state/<branch-slug>/` with `state.json` (current snapshot), `log.jsonl` (append-only session log), and `archive.json` (evicted narratives). Summaries derive from `git log`, not memory; state commits locally and is never pushed by the agent.

**Tools used:** `Read`, `Write`, `Edit`, `Glob`, `Bash`

**Protocol:** See [`session-management/PROTOCOL.md`](session-management/PROTOCOL.md) for the full cross-agent specification.

**⚠️ Multi-CLI installs:** Copying this skill into `~/.claude/skills/` wires **Claude Code only**. Grok usually picks it up via its Claude-compat scan, but **Codex does not scan `~/.claude/skills/`** — without extra wiring it becomes a one-way blind spot that neither reads nor writes handoff state. See [`session-management/INSTALL.md`](session-management/INSTALL.md) for the exact `~/.codex/AGENTS.md` + `/wrap-up` prompt blocks (and the Grok/Cursor equivalents).

---

## How the Learning Skills Work Together

```
  /challenge-design          /compound-learning         /learnings-researcher
  ┌──────────────┐           ┌──────────────┐           ┌──────────────────┐
  │  Debate &    │           │  Capture &   │    ───►   │  Search &        │
  │  validate    │    ───►   │  document    │           │  retrieve        │
  │  designs     │           │  learnings   │           │  knowledge       │
  └──────────────┘           └──────┬───────┘           └────────┬─────────┘
                                    │                            │
                                    ▼                            │
                             docs/solutions/                     │
                             ├── patterns/                       │
                             ├── runtime-errors/    ◄────────────┘
                             ├── database-issues/
                             └── ...
```

1. **Challenge** a design decision before building
2. **Capture** what you learn as you build and debug
3. **Research** past solutions when you encounter similar problems

## How the Design Skills Work Together

```
                         /ux-design-agent
                        ┌───────────────┐
                        │    Routes     │
                        │   requests    │
                        └──┬─────┬────┬─┘
                           │     │    │
              ┌────────────┘     │    └────────────┐
              ▼                  ▼                  ▼
     /frontend-design     /canvas-design      /theme-factory
     ┌──────────────┐     ┌──────────────┐    ┌──────────────┐
     │  Web UI code │     │  Visual art  │    │  Apply theme │
     │  HTML/CSS/JS │     │  .pdf / .png │    │  to artifact │
     └──────────────┘     └──────────────┘    └──────────────┘
```

Use `/ux-design-agent` as the entry point, or invoke a specific skill directly when you know what you need.

## Installation

Copy any skill directory into your project's `.claude/skills/` folder, or into `~/.claude/skills/` to make it available globally:

```sh
# Single skill — project-level
cp -r challenge-design /path/to/your-project/.claude/skills/

# All skills — global
for d in */; do [ "$d" = "global/" ] || cp -r "$d" ~/.claude/skills/; done
```

To keep machines in sync, clone this repo and symlink instead of copying (`ln -s ~/dev/claude-skills/jev-fit ~/.claude/skills/jev-fit`), then `git pull` to update.

`global/CLAUDE.md` is the author's global Claude Code instructions (workflow rules, including the Jev fit check). To use it: `ln -s ~/dev/claude-skills/global/CLAUDE.md ~/.claude/CLAUDE.md`.

Skills are automatically discovered by Claude Code once placed in a recognized skills directory.

## Example Output

A document created by `/compound-learning`:

```markdown
---
title: Cloud Run cold starts causing timeout on first request
category: performance-issues
severity: high
date_discovered: 2025-11-15
tags: [cloud-run, cold-start, fastapi]
symptoms:
  - First request after idle period returns 504
  - Subsequent requests respond normally
root_cause: Default Cloud Run min-instances is 0, causing full container startup on first request.
related_files:
  - deploy/cloudrun.yaml
---

## Context
Production API returning 504 errors intermittently...

## Solution
Set minimum instances to 1 in Cloud Run configuration...

## Prevention
Add cold-start latency monitoring to alerting dashboard.
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
