# Hive look: the in-app "new look" (synced with the repo, 12 Nov 2026)

**Source of truth:** `frontend/packages/ui-kit/tokens.css`, every rule under `html[data-look="new"]`. The base block holds fonts, the type ramp and radii; `[data-theme="dark"]` and `[data-theme="light"]` hold colour. The Tailwind mapping is `frontend/packages/ui-kit/tailwind-preset.js` (`look-new:` variant), and the plan behind it is `docs/plans/2026-10-22-hive-new-look.md`. Admins switch the new look on per person in prod. Before each demo, re-read the dark block on local `qa` (`git show qa:frontend/packages/ui-kit/tokens.css`). Where it differs from the values below, the repo wins: update `:root` in `demo.html`.

Not this: the public site (hive-os.ai, `frontend/src/pages/HomePage.tsx`) uses the same palette with marketing layout and no sidebar. Use it only for website-style clips.

## Colour (dark theme)

| Token | Value | Where |
|---|---|---|
| `--bg` | `#0a0d12` (`--paper`) | main content, top bar, Sayya panel |
| `--surface` | `#11151c` (`--paper-2`) | sidebar, cards, footer |
| `--surface-2` | `#161b24` (`--paper-50`) | inputs, search, answer cards, workflow cards |
| `--surface-3` | `#1b212c` (`--paper-100`) | inner panels, list headers, chips |
| `--line` | `#242b37` (`--rule`) | borders, dividers, active nav item fill |
| `--line-2` | `#3a4250` (`--rule-strong`) | stronger borders, dashed search box, empty bars |
| `--ink` | `#dfe3ea` | primary text |
| `--ink-2` | `#b4bcc9` (`--fg-2`) | secondary text, nav items at rest, descriptions |
| `--ink-3` | `#9ea7b5` (`--fg-3`) | mono metadata, dates, counts |
| `--muted` | `#687284` (`--control-border`) | placeholders, input borders |
| `--blue` | `#5b8def` | bars, the "new" row edge, quick-action dots |
| `--blue-link` | `#8fb3ff` | links, EMAIL/TASK type labels, "Ask Sayya →" text |
| `--blue-bg` / `--blue-border` | `#0f1626` / `#22385e` | outline-blue buttons ("Ask Sayya →", Approve) |
| `--amber` | `#f2b544` (\"needs you\"; Approve only) | Review badge, "7 TO APPROVE" pill, the Review card border, "TODAY" due labels |
| `--orange` | `#ff8a4c` (`--problem`) | overdue counts, "N DAYS LATE" |
| `--green` / `--green-dim` / `--green-bg` | `#3cc486` / `#16392e` / `#112722` | done counts and states, done bars, the done-row tint |
| violet | `#b871c4` on `#271d2f` | the "Watch for a reply" quick action |

The user's own chat bubble in Sayya is light (`#e9ebef`) with dark text.

## Shape and motion

- Radii: panels and cards 12 px (`--radius-panel`), buttons, inputs and rows 8 px (`--radius-ui`), tags 4 px (`--radius-tag`).
- No shadows in the new look (`--elev-*` are `none`). Use borders and fills for depth. The one exception is the workflow card's hover lift.
- Ease `cubic-bezier(0.2, 0.8, 0.2, 1)` for UI moves; cards fade up 12 px over about 0.45 s, staggered 60 ms (scale ×1.3 for video).

## Type

- **IBM Plex Sans Condensed** 600–700: page titles in uppercase ("TASKS", "REVIEW", letter-spacing ~.05em), card headings ("RECOMMENDED NOW", "YOUR PLATE"), big greetings ("Good evening, Rohit"), stat numbers, card titles.
- **IBM Plex Sans** 400–600: body, nav items, row titles and descriptions, buttons.
- **IBM Plex Mono** 400–600: dates ("WED 11 NOV"), section labels (ACT, APPLICATIONS, STRATEGY, LEARN), counts, type labels (EMAIL, MEETING, TASK), metadata ("DAILY 9:00 · IN HIVE · 0 RUNS"), footer. Uppercase, tracking .08–.14em.

## Shell (at 1920×1080)

- **Sidebar**, 232 px, on `--surface` with a right border in `--line`. At the top, a 64 px header with the honeycomb mark and "HIVE / OBJECT EDGE".
  - Below it, the dashed "Jump to… ⌘K" search.
  - Sections: **ACT** (Today, Tasks, Meetings, Review with the amber badge, Routines), **APPLICATIONS** (Mentat, Scout, Waggle, Sales Command Center, Customer billing), **STRATEGY** (Decisions, Signals, Initiatives, Insights), **LEARN** (Hive, Documents, Agent Actions, Files).
  - Items are 34 px tall and the active one is filled with `--line`. Counts are mono, on the right. At the bottom: the user, plus a theme toggle.
- **Top bar**, 64 px: the page title in Condensed uppercase plus the mono date. On the right: the segmented "Dashboard | Split | Focus" control, the "Show Sayya" outline button and a help icon.
- **Footer**, 36 px: "© 2026 HIVE · OBJECT EDGE" on the left; "WHAT'S NEW · STATUS · <PAGE> · V1.0.0" on the right.
- **Content** is a centred column about 1240 px wide.
- **Split view:** the page on the left, and the Sayya panel on the right ("ASK SAYYA · New conversation", quick-action chips, "Ask Sayya anything…" input, "Thinking: Balanced", "Show work").

## Components in the template (class names)

- `.card` (surface, line border, 14 px radius) with `.chead` (a Condensed h4 plus a mono `.r` on the right).
- `.rrow` recommendation and review rows: `.ty` mono type label, `.tx` title and description, `.src` mono source (blue when new), `.bt` outline-blue button, `.dots`.
- `.rv` amber-bordered review card, `.amber-pill`, `.bar` progress bars, `.stats` greeting counters.
- States: `.newglow` (blue left edge on new rows), `.donefill` (green tint), `.status` ("✓ SENT"/"✓ BOOKED").
- `#chat`: a generic light chat window with header, messages, a prepared-items card and an input. Label it with the product's name; never add its logo.
- `.capi` caption pill (amber step number), `.acard` "also in this release" card, `#ov-end` end card.

## Voice on screen

Hive's UI copy is plain and sentence-case: "Things Hive prepared that need your yes", "Nothing goes out until you approve it", "Waiting on others", "Hive drafts nudges · you send". Captions follow the same voice. Use the release note's own words for feature names.

## Workflow library (local qa, not yet in prod; `feat/workflow-library`)

Use these when a demo touches Workflows (`frontend/src/pages/Workflows.tsx`, `WorkflowDetail*.tsx`, `frontend/src/components/workflows/`):
- **Cards:** a category icon and colour (Your day teal, Money green, Projects purple, Sales blue, from the viz tokens), a mono caps category label, a Condensed title, one status chip (✓ Ready / Partially ready / ✓ On / Paused / Waiting for data), and a single "Open →". The whole card is the link, and hover lifts it with an accent border. Cards may carry an animated mini-scene (`nl/workflow-scenes`).
- **Nav:** a "Workflows · N on" row under Review.
- **Workflow page:** coloured section headings ("What it does" blue, "What you'd get" purple, "What it needs" amber, "How to run it" teal); data-check rows (✓ In Hive / ⚠ Partly in Hive / – Not in Hive yet); "Ask us to get this data"; a run-history table whose rows open in place.
- **Home:** "Working for you" and "Recommended now" entry points.
- **Ground truth:** the approved mockup https://claude.ai/artifact/LJMuyyNyoZsTic7CcC6trv (drawn in Control Tower tokens, so take colours from tokens.css, not from the mockup), or run local qa with `WORKFLOW_LIBRARY_ENABLED=true`.
