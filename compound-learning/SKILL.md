---
name: compound-learning
description: Document a solved problem or learned pattern into docs/solutions/ with structured frontmatter for future retrieval.
allowed-tools: Read, Write, Glob, Grep, AskUserQuestion
---

# Compound Learning — Solution Capture

Document problems solved and patterns learned so the team (and AI agents) can find them later.

## When to invoke

- After fixing a non-trivial bug
- After discovering a gotcha or footgun
- After establishing a new pattern or convention
- User invokes with `/compound-learning`

## Instructions

### 1. Gather context

If `$ARGUMENTS` is provided, use it as the starting description.

Otherwise, look at the recent conversation for:
- What problem was solved
- What the symptoms were
- What the root cause was
- What files were changed

Read the schema file to know valid categories, severities, and tags:
```
.claude/skills/compound-learning/schema.yaml
```

Ask the user only if you genuinely can't determine:
- The category (which subdirectory)
- Whether this is a new pattern or a fix for an issue

Do NOT ask about severity, tags, or other metadata — infer these from context.

### 2. Preview the document

Generate the complete document with YAML frontmatter and present it to the user. Use this format:

```markdown
---
title: [descriptive title]
category: [category from schema]
severity: [inferred severity]
date_discovered: [today's date]
tags: [relevant tags from schema]
symptoms:
  - "Observable symptom 1"
  - "Observable symptom 2"
root_cause: "Why it happened"
related_commits: [SHAs if known]
related_files: [key files if known]
---

## Context
[What was happening]

## Investigation
[How root cause was found — skip if obvious]

## Solution
[What changed and why]

## Prevention
[How to avoid this — skip if not applicable]
```

Tell the user: "Here's the solution document I'll create. Want me to write it, or would you like changes?"

### 3. Write the document

After user confirms:

1. Generate a filename from the title: lowercase, hyphens, no special chars, `.md` extension
   - Example: `ci-test-suite-silent-failures.md`
2. Write to `docs/solutions/{category}/{filename}`
3. Confirm the file path to the user

## Important

- Keep documents concise — aim for 50-150 lines
- One problem per document. If a fix touched multiple issues, create separate docs
- For patterns (not issues), symptoms and root_cause frontmatter can be omitted
- Tags should be lowercase kebab-case and match common tags from schema.yaml
- Don't duplicate information already in PROGRESS.md — solution docs go deeper on the "why" and "how to prevent"
