---
name: learnings-researcher
description: Search solved problems and patterns across all projects
allowed-tools: Glob, Grep, Read, AskUserQuestion
user-invocable: true
argument-hint: "search query (keyword, topic, or problem description)"
---

# Learnings Researcher

Search across all projects for previously documented solutions, patterns, and learnings captured by `/compound-learning`.

## When to invoke

- Before solving a problem that might have been solved before
- When looking for established patterns or conventions
- When starting work in a domain where past learnings might apply
- User invokes with `/learnings-researcher [query]`

## Instructions

### 1. Get the search query

If `$ARGUMENTS` is provided, use it as the search query.

If `$ARGUMENTS` is empty, ask the user:
> "What problem, pattern, or topic are you looking for? (e.g., 'SSE streaming', 'shared state', 'deployment')"

### 2. Find all solution documents

Use Glob to find every solution doc across all projects:

```
~/dev/projects/*/docs/solutions/**/*.md
```

If no files are found, tell the user:
> "No solution documents found in any project under `~/dev/projects/*/docs/solutions/`. Use `/compound-learning` to start capturing learnings."

Then stop.

### 3. Search for matches

Use Grep with the search query against the found files. Search broadly — match against:
- Frontmatter fields (title, tags, category, root_cause)
- Body content (Context, Solution, Prevention sections)

If the query has multiple words, search for each word individually and combine results. Prefer files that match multiple terms.

If Grep returns no matches, try:
- Splitting the query into individual keywords
- Searching for synonyms or related terms (e.g., "websocket" if query is "real-time")

### 4. Read and rank matches

Read up to 5 matching files. For each file, extract:
- **Title** — from frontmatter `title` field
- **Category** — from frontmatter `category` field
- **Tags** — from frontmatter `tags` field
- **Severity** — from frontmatter `severity` field
- **Project** — inferred from the file path (the directory name under `~/dev/projects/`)
- **Summary** — the first 2-3 sentences of the `## Context` or `## Solution` section

Rank results by relevance:
1. Title or tag exact match → highest
2. Multiple term matches across sections → high
3. Single term match in body → medium

### 5. Present results

Format output as:

```
## Found N matching solution(s) for "[query]"

### 1. [Title]
**Category:** [category] | **Severity:** [severity] | **Project:** [project-name]
**Tags:** [tag1, tag2, tag3]
**Summary:** [2-3 sentence summary]
**File:** [full file path]

---

### 2. [Title]
...
```

If no matches were found after searching, tell the user:
> "No matching solutions found for '[query]'. This might be a new problem worth documenting with `/compound-learning` after you solve it."

### 6. Offer next steps

After presenting results, say:
> "Want me to read any of these in full, or apply a pattern from one of them to your current work?"
