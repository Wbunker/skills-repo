---
name: claude-design-expert
description: Expert guide for Anthropic's Claude Design product (launched April 17, 2026). Use when users ask how to use Claude Design, need help creating prototypes, slides, mockups, one-pagers, or marketing collateral with Claude Design, want prompting strategies for visual creation, need to set up a design system, or want to integrate Claude Design into their workflow. Triggers on: "claude design", "design with claude", "prototype with claude", "pitch deck with ai", "create mockup", "claude.ai/design".
---

# Claude Design Expert

Claude Design (claude.ai/design) is Anthropic's visual creation tool that turns natural-language prompts into interactive prototypes, slides, mockups, one-pagers, and marketing collateral. Powered by Claude Opus 4.7. Launched April 17, 2026 as a research preview.

## Access

- **URL:** claude.ai/design
- **Plans:** Pro, Max, Team, Enterprise (not free tier)
- **Enterprise:** Admin must enable via Organization Settings before users can access
- **Usage quota:** Separate from Claude chat/Code limits — not shared

## Core Workflow

**Describe → Generate → Refine → Export**

1. **Describe** — prompt with text, upload docs/images, paste a URL, or link a codebase
2. **Generate** — Claude produces an interactive artifact (not a static image)
3. **Refine** — inline comments on specific elements, follow-up prompts, or the Tweaks panel
4. **Export** — choose format for downstream use

### Inputs Accepted
- Text prompts
- Image uploads (screenshots, inspiration)
- Documents: DOCX, PPTX, XLSX
- Codebase references (for design-system extraction)
- Website URLs / web capture
- Brand guideline PDFs

### Export Options
| Format | Best for |
|--------|----------|
| PPTX | PowerPoint workflows, external sharing |
| Canva | Further editing, collaboration |
| HTML | Claude Code handoff, interactive prototypes |
| PDF | Read-only stakeholder review |
| Internal URL | Org-scoped sharing (private / view-only / edit) |

## Design System

On first use, Claude reads your codebase and design files to extract colors, typography, and components into a persistent design system. Every subsequent project applies it automatically. Multiple design systems can be maintained (e.g., one per brand or product line).

- Rich inputs (full codebase, detailed style guide) → faithful extraction
- Minimal inputs (logo only) → reasonable approximation

## Prompting Strategy

Be specific. Include: target audience, platform/device, mood, constraints, and reference materials.

**Strong prompt:** "Prototype a mobile meditation app for Gen Z users — calm, dark-mode-first, with breathing animations and a daily streak tracker."

**Weak prompt:** "Make a meditation app."

Additional tips:
- Provide a real codebase or full brand guide for design-system setup — a lone logo yields guesses
- Use the **Tweaks panel** (device preview, theme toggles, typography scale) for small adjustments — faster than re-prompting
- Use **inline comments** to give feedback on specific elements rather than re-describing the whole design
- Apply **global changes** (color, spacing, font) across the entire design at once when adjusting brand elements
- Place long documents near the top of your prompt, query at the end — improves model accuracy

## Use Cases

See [references/use-cases.md](references/use-cases.md) for detailed workflows per use case:

1. Interactive prototypes (stakeholder demos, user testing)
2. Pitch decks (PPTX-first export, on-brand in minutes)
3. One-pagers and marketing collateral
4. Product wireframes and mockups
5. Code-powered prototypes (voice, video, WebGL shaders, 3D, AI features)

## Collaboration

- Share within org as private, view-only, or editable URL
- Group conversations with Claude while co-editing
- Export HTML bundle → hand off to Claude Code for implementation

## Workflow Integration

- **→ Claude Code:** Export as HTML bundle; Claude Code implements it as production-ready code
- **→ Canva:** Export for polish, further editing, and external collaboration
- **→ PPTX:** For stakeholders who live in PowerPoint

## Limitations

- Not a Figma replacement — no fine-grained vector editing or pixel-perfect control
- Design-system accuracy depends on richness of brand inputs
- Research-preview usage caps apply
- Latency and token costs tied to Opus 4.7

## Best Fit

**Ideal:** Pre-seed founders, PMs without design pairs, marketing teams (design-system extraction has strong ROI), agency teams in rapid divergence phases.

**Less ideal:** Workflows that start from long-form documents (researchers, consultants, analysts) — use a document-to-presentation tool first, then Claude Design for net-new visuals.

## Gotchas

- Enterprise users cannot access Claude Design until an admin enables it in Organization Settings — check this first if access is denied
- Claude Design quota is **separate** from chat/Claude Code usage — users are not trading messages for design prompts
- Claude Design produces **interactive artifacts**, not static images — outputs can include voice, video, WebGL, and 3D; frame expectations accordingly
- The Tweaks panel is faster than re-prompting for small visual adjustments — always reach for it first
- Providing only a logo or single color for design-system onboarding yields guesses, not faithful brand extraction; push users to supply a codebase or full style guide
