---
version: alpha
name: Lotline
description: A calm operations workspace with a traceable material lineage at its centre.
colors:
  primary: '#254E70'
  background: '#F3F6F8'
  surface: '#FFFFFF'
  ink: '#20364B'
  muted: '#566a7d'
  line: '#D9E2E9'
  danger: '#B44748'
  warning: '#886121'
  success: '#2D735D'
  accent: '#D7AE69'
typography:
  sans:
    fontFamily: 'Manrope, Arial, sans-serif'
  mono:
    fontFamily: 'IBM Plex Mono, monospace'
rounded:
  DEFAULT: '0.5rem'
  sm: '0.25rem'
  lg: '0.875rem'
spacing:
  section: '1.5rem'
  field: '0.75rem'
components:
  button:
    rounded: '0.5rem'
  dialog:
    rounded: '0.875rem'
---

# Lotline design system

## Overview
Operations analysts need to follow a suspect material, verify the records and approve a bounded action. The visual reference is a quality-control workspace and material flow sheet, not a marketing dashboard. An asymmetrical three-part workspace keeps the investigation, lineage and review in view. A blue-grey foundation makes amber uncertainty and red flagged stock meaningful. The signature is the material path with a separate dashed evidence-gap branch.

Product register. English UI for a worldwide hackathon audience. Desktop-first investigation, phone-readable evidence and review. No location or compliance assumptions. Only fictional operational data appears. Manrope and IBM Plex Mono are bundled locally with their OFL licences. Native system fallbacks preserve legibility if fonts fail.

Token model A: this frontmatter is canonical. scripts/export_tokens.py generates web/src/tokens.css. Components consume the generated semantic variables. Only chart tints, state overlays and white-on-dark controls derive transparencies from those tokens. No dark theme is offered.

## Colors
Primary is for controls and connected paths, never for hazard severity. Danger marks the flagged source lot. Warning marks unsigned evidence. Success identifies supported scope, not certified product safety. Background provides workspace separation. Surface holds the graph and evidence. Muted is secondary readable text. Line separates table rows. Accent is used only for the product mark and evidence attention.

## Typography
Manrope gives compact, legible operations copy. Headings use restrained 600/700 weights. IBM Plex Mono renders lot identifiers, counts and query traces. Body is 14px with 1.55 line height. Small labels are 11px or 12px. Main title is 30px. Numeric tables use tabular figures. No huge promotional heading in the product workspace.

## Layout
A 224px side rail, flexible investigation canvas and 350px agent panel at 1440px. Below 1180px the agent panel moves below the canvas. Below 720px the side rail becomes a top navigation band and case selection uses a native select. The document owns scrolling. Graph scroll is contained only within its panel. White space around graph nodes preserves exact labels and arrow direction. Panels never hide essential overflow.

## Elevation & Depth
Thin separators and surface tints carry hierarchy. Only dialogs have a shadow. The graph is not wrapped in nested cards. The rail is a pale blue-grey surface. Dialog backdrop remains neutral.

## Shapes
8px controls and 14px large work surfaces. 4px data tags. Paths are gently curved, ports are round, material nodes are 8px rectangles. Pills are restricted to semantic status tags.

## Components
Buttons are native buttons. Hover changes tone, focus uses a visible 3px blue ring, busy preserves width and disables duplicate actions. Tables use native table semantics and explicit row buttons to open a path. Path details and documents use the same modal primitive with focus capture, Escape and focus return. Dialogs fit the narrow viewport and retain errors for retry.

The agent composer uses a labelled non-resizing textarea, a submit button, two useful suggestion chips and a visible tool trace. Error and success messages live in an accessible live region. Search/filter and tab controls have text labels. No empty avatar, fake chart, fabricated activity or decorative KPI card.

Lucide outline icons at 18px or 20px accompany text. Labels remain visible on primary actions. Motion lasts 150-250ms and communicates connection selection or loading. Reduced motion disables transitions and spinners. The visible diagram has an equivalent shipment table and path list for keyboard and screen-reader access.

## Do's and Don'ts
Do place evidence next to the affected item. Do distinguish confirmed, needs review and not linked. Do show database and planner status honestly. Do preserve the exact reviewed shipment set. Do not describe disconnected stock as safe. Do not add a purple gradient, glass panels, oversized metrics or automatic hold action. Do not hide the synthetic sandbox label.
