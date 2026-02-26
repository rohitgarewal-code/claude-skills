# Claude Skills

A collection of [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) for knowledge management and design validation. These three skills form an interconnected system: challenge your designs, capture what you learn, and retrieve that knowledge later.

## Skills

### `/challenge-design`

Pressure-tests a design decision by running two AI agents in parallel — a **defender** of the current design and a **challenger** proposing an alternative. Both agents read the actual codebase (no armchair arguments), score designs across five dimensions (Simplicity, Correctness, Extensibility, Performance, Developer Experience), and a verdict is declared with reasoning.

**Use when:** You're debating an architecture, data model, API shape, or component structure and want structured pushback before committing.

**Tools used:** `Task`, `Read`, `Glob`, `Grep`

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

## How They Work Together

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

## Installation

Copy any skill directory into your project's `.claude/skills/` folder, or into `~/.claude/skills/` to make it available globally:

```sh
# Single skill — project-level
cp -r challenge-design /path/to/your-project/.claude/skills/

# All skills — global
cp -r challenge-design compound-learning learnings-researcher ~/.claude/skills/
```

Skills are automatically discovered by Claude Code once placed in a recognized skills directory.

## Example Output

A document created by `/compound-learning` looks like this:

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
