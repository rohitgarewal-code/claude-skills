# UX Harness Scoring Rubric

Four criteria, each scored 1-10. The harness passes when ALL scores >= 7.

## Design Fidelity (Weight: HIGH)

Does the output match the original design intent?

| Score | Description |
|-------|-------------|
| 1-3   | Barely recognizable as the intended design. Wrong mood, wrong structure. |
| 4-6   | Recognizable intent but significant deviations. Missing key design tokens, wrong layout proportions, or mismatched aesthetic. |
| 7-8   | Clearly matches the intent. Design tokens are correct, layout follows the spec, mood is right. Minor deviations in spacing or proportions. |
| 9-10  | Indistinguishable from a human designer's interpretation of the intent. Every detail aligns. |

## Visual Quality (Weight: HIGH)

Is the aesthetic coherent, distinctive, and intentional?

| Score | Description |
|-------|-------------|
| 1-3   | Generic "AI slop" — default gradients, template layouts, system fonts. No design identity. |
| 4-6   | Has some personality but inconsistent. Mixed signals — e.g., dark theme with bright pastel accents that clash. |
| 7-8   | Cohesive aesthetic with clear identity. Colors, typography, and layout work together. Would not be immediately identified as AI-generated. |
| 9-10  | Distinctive and memorable. A designer would study this for inspiration. Bold choices executed with precision. |

## Craft (Weight: MEDIUM)

Is the technical execution precise?

| Score | Description |
|-------|-------------|
| 1-3   | Misaligned elements, inconsistent spacing, broken typography hierarchy. |
| 4-6   | Mostly aligned but with noticeable spacing inconsistencies or contrast issues. |
| 7-8   | Clean execution. Consistent spacing, proper hierarchy, good contrast ratios. Professional quality. |
| 9-10  | Pixel-perfect. Every element deliberately placed. Spacing rhythm is musical. |

## Functionality (Weight: MEDIUM)

Can users understand and complete tasks?

| Score | Description |
|-------|-------------|
| 1-3   | Broken layout, unclickable buttons, overlapping elements, unusable at any viewport. |
| 4-6   | Usable but with friction — unclear CTAs, confusing navigation, broken at some breakpoints. |
| 7-8   | Clear, usable interface. Users can find what they need and complete tasks. Responsive works. |
| 9-10  | Effortless. Information architecture guides the eye. Every interaction feels natural. |

## Calibration Notes

- **Weight HIGH criteria more in pass/fail decisions.** A score of 6 on Design Fidelity is more concerning than a 6 on Craft.
- **Grade against the spec's success criteria**, not against an abstract ideal.
- **Compare to the reference images/intent**, not to your own preferences.
- **AI slop indicators to watch for**: purple gradients on white, Inter/Roboto fonts, evenly-distributed muted palettes, card-heavy layouts with rounded corners, generic hero sections with gradient backgrounds.
