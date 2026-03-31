# Design Spec Format

The planner MUST output a file named `spec.md` in the run directory with this exact structure.
Every section is required. No section may be left empty or contain placeholder text.

## Template

# Design Spec: [Project Name]

## Intent
[1-2 sentences — the soul of what we're building. What does the user want to feel when using this?]

## Aesthetic Direction
[Mood, references, key design decisions. Describe the visual identity — NOT implementation.
Example: "Dense, dark, terminal-inspired. High information density like Bloomberg Terminal.
Monospace typography for data. Minimal chrome. Every pixel earns its place."]

## Design Tokens
[Concrete values extracted from references or specified by the user.]

- **Colors**: Primary, secondary, accent, background, surface, text (with hex values)
- **Typography**: Font families for headings, body, data/code. Size scale.
- **Spacing**: Base unit and scale (e.g., 4px base, 4/8/12/16/24/32/48)
- **Border Radius**: Values for cards, buttons, inputs
- **Shadows**: Elevation levels if applicable

## Component Inventory
[Every distinct UI component needed, described by PURPOSE not implementation.
Example: "KPI summary card — displays a single metric with label, value, trend indicator, and sparkline"]

## Layout Architecture
[Page structure and information hierarchy.]

- **Desktop** (1440px+): [layout description]
- **Tablet** (768-1439px): [layout description]
- **Mobile** (< 768px): [layout description]
- **Information hierarchy**: What does the user see first, second, third?

## Interaction Model
[How the interface responds to the user.]

- **Hover states**: [description]
- **Transitions**: [duration, easing, what animates]
- **Loading states**: [skeleton, spinner, progressive]
- **Scroll behavior**: [sticky headers, infinite scroll, pagination]

## Success Criteria
[Specific, evaluatable statements. The evaluator grades against these.]

1. [Criterion 1 — measurable or visually verifiable]
2. [Criterion 2]
3. [Criterion 3]
