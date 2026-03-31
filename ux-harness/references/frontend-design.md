# Frontend Design Aesthetic Guidelines

These guidelines are injected into the Generator subagent's prompt. They replace the /frontend-design skill (which subagents cannot invoke directly).

## Design Thinking

Before coding, commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme — brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian
- **Differentiation**: What makes this UNFORGETTABLE?

Choose a clear conceptual direction and execute it with precision.

## Typography
Choose fonts that are beautiful, unique, and interesting. NEVER use: Arial, Inter, Roboto, system fonts. Pair a distinctive display font with a refined body font. Use Google Fonts or CDN-hosted fonts.

## Color & Theme
Commit to a cohesive palette. Use CSS variables. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.

## Motion
Focus on high-impact moments: page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Prefer CSS-only animations.

## Spatial Composition
Unexpected layouts. Asymmetry. Overlap. Grid-breaking elements. Generous negative space OR controlled density — match the aesthetic direction.

## Backgrounds & Depth
Create atmosphere — gradient meshes, noise textures, geometric patterns, layered transparencies. Never default to solid flat colors.

## NEVER
- Overused fonts (Inter, Roboto, Arial, Space Grotesk)
- Purple gradients on white backgrounds
- Predictable card-heavy layouts
- Cookie-cutter design without context-specific character
- Same aesthetic across different projects

Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code. Minimalist designs need restraint and precision.
