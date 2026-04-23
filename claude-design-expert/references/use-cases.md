# Claude Design — Use Case Workflows

## Contents
1. [Interactive Prototypes](#1-interactive-prototypes)
2. [Pitch Decks](#2-pitch-decks)
3. [One-Pagers and Marketing Collateral](#3-one-pagers-and-marketing-collateral)
4. [Product Wireframes and Mockups](#4-product-wireframes-and-mockups)
5. [Code-Powered Prototypes](#5-code-powered-prototypes)

---

## 1. Interactive Prototypes

**Goal:** Stakeholder demo or user testing before design handoff.

**Workflow:**
1. Provide a text description or upload a rough wireframe/screenshot as reference
2. Prompt: "Build an interactive prototype for [feature]. Users should be able to [key flows]. Target: [device/platform]."
3. Refine navigation and interaction states via inline comments
4. Export as HTML for Claude Code handoff or share as internal URL for stakeholder review

**Tips:**
- Claude Design prototypes can include voice, video, WebGL shaders, and 3D — specify if you want advanced interactions
- Use the device-preview toggle in Tweaks to check mobile vs desktop rendering

---

## 2. Pitch Decks

**Goal:** Founder or AE needs a polished, on-brand deck fast.

**Workflow:**
1. Upload a rough outline (DOCX/PPTX) or paste bullet points as text
2. Prompt: "Turn this into a 10-slide pitch deck. Audience: [investors/customers]. Tone: [confident/technical/warm]. Apply our brand design system."
3. Use Tweaks panel to adjust typography scale and color theme
4. Export as PPTX for external sharing or Canva for further editing

**Tips:**
- PPTX export is first-class — slides are fully editable in PowerPoint
- Feed a competitor's deck URL via web capture to set a visual benchmark
- If no design system is set up yet, provide a brand guide PDF during this session

---

## 3. One-Pagers and Marketing Collateral

**Goal:** Marketing team needs landing pages, social assets, or campaign visuals consistent with brand.

**Workflow:**
1. Confirm design system is set up (brand colors, fonts, components extracted)
2. Prompt: "Create a one-pager for [product/feature]. Key message: [headline]. Secondary points: [bullets]. Call to action: [CTA text]."
3. Apply global brand changes if needed (Tweaks panel → color theme)
4. Export as HTML for web use or PDF for print/email

**Tips:**
- Design-system extraction pays off most here — a rich codebase or style guide produces on-brand results instantly
- For social assets, specify dimensions and platform (e.g., "1080×1080 for Instagram")

---

## 4. Product Wireframes and Mockups

**Goal:** PM or designer exploring layout options before committing to Figma work.

**Workflow:**
1. Describe the feature or screen: "Wireframe a dashboard for [user role]. Key data: [metrics]. Actions: [buttons/filters]."
2. Generate multiple layout explorations via follow-up prompts ("Now try a sidebar layout")
3. Use inline comments to adjust specific components
4. Export as HTML or Canva for further iteration

**Tips:**
- Claude Design is ideal for divergence phases — generate 3-4 layout directions quickly
- Not suitable for pixel-perfect production-ready specs; hand off to Figma for that
- Attach a PPTX/XLSX spec sheet to let Claude extract requirements directly

---

## 5. Code-Powered Prototypes

**Goal:** Engineer or technical PM needs a working prototype with real interactions.

**Workflow:**
1. Link your codebase so Claude can extract existing components and data models
2. Prompt: "Build a prototype for [feature] using our existing [component library]. Include [voice/video/3D/AI] interaction."
3. Refine via follow-up prompts targeting specific interaction states
4. Export as HTML bundle → hand off to Claude Code for production implementation

**Tips:**
- Specify interactive capabilities explicitly (voice, video, WebGL, 3D) — Claude won't add them by default
- The HTML export is designed for Claude Code handoff — it includes packaged assets and structure ready for implementation
- Use "Package for Claude Code" export option rather than plain HTML when implementation is the goal
