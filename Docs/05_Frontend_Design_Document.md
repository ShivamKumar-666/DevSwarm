# DevSwarm — Frontend Design Document

## 1. Purpose
Visual and interaction design direction for the SRE Dashboard. Direction is a merge of two reference inspirations: a dense, data-forward monitoring UI (structural base) and a status-badge/pill pattern from a second reference (borrowed selectively, decoration excluded). Rationale for what was kept vs. dropped is in §7.

## 2. Design Principles
- **Legible under viva pressure.** Read live, on a projector, by graders seeing it for the first time. Clarity and labeling beat visual flourish everywhere.
- **Simulated vs. real must be visually distinct**, not just labeled in text — see Cost Agent treatment in §3 and §6.4.
- **Status at a glance** — the Agent Overview view must communicate "is anything blocked or escalated" within 3 seconds of looking at it.
- **Every visual element must represent real data.** No decorative-only graphics (see §7 — this is a direct, deliberate rejection of one of the two reference designs).

## 3. Color Palette

| Token | Hex | Usage |
|---|---|---|
| `--bg-primary` | `#0A0A0B` | Page background |
| `--bg-surface` | `#121214` | Card / panel background |
| `--bg-surface-raised` | `#18181B` | Hover state, nested panels |
| `--border` | `#232326` | Card borders, dividers (1px, minimalist) |
| `--text-primary` | `#F5F5F5` | Headings, primary values |
| `--text-secondary` | `#9A9AA2` | Labels, timestamps, secondary text |
| `--text-muted` | `#6B7280` | Disabled/placeholder text |
| `--accent` | `#8B5CF6` | Reserved exclusively for confidence-score / precedent-match highlights in the Decision Trail — the project's novelty claim. Not used decoratively elsewhere. |
| `--status-healthy` | `#22C55E` | Healthy / proceed / passed |
| `--status-warning` | `#F59E0B` | Escalated / needs human approval |
| `--status-critical` | `#EF4444` | Blocked / failed / critical |
| `--status-simulated` | `#6B7280` (dashed border, no fill) | Cost Agent data only — never used for real agent output |

**Rule:** `--accent` (violet) appears in exactly one context — confidence scores and matched-precedent highlights. If it starts appearing elsewhere (buttons, nav, random emphasis), that's scope creep back toward the decorative reference — resist it.

## 4. Typography

| Role | Font | Weight | Size |
|---|---|---|---|
| Nav / UI labels / buttons | Inter | 500 (Medium) | 13–14px |
| Page headings | Inter | 600 (Semibold) | 20–24px |
| Card titles | Inter | 600 (Semibold) | 14px |
| Body / descriptions | Inter | 400 (Regular) | 13px |
| Data values (big numbers, metrics) | JetBrains Mono | 600 (Semibold) | 28–32px |
| Logs, commit SHAs, CVE IDs, confidence scores | JetBrains Mono | 400 (Regular) | 12–13px |
| Timestamps | JetBrains Mono | 400 (Regular) | 11px, `--text-secondary` |

**Rationale:** Inter for anything a human reads as language (labels, nav, descriptions); JetBrains Mono for anything that's technically precise data a viewer might need to verify character-by-character (SHAs, IDs, scores, log lines). This distinction itself is a small but real signal of technical intent under scrutiny.

## 5. Component Style

### Cards / Panels
- Border radius: **8px** (deliberately less rounded than a consumer-SaaS 12–16px — reinforces the dense/technical feel, not a marketing surface)
- Border: 1px solid `--border`, no shadow by default
- On hover (interactive cards only): background shifts to `--bg-surface-raised`, no shadow added
- Padding: 16px standard, 20px for primary metric cards

### Buttons
- Border radius: 6px
- Primary: `--text-primary` background, `--bg-primary` text (inverted, high contrast) — reserved for Approve/confirm actions only
- Secondary: transparent background, 1px `--border`, `--text-primary` text
- Destructive (Reject/Rollback): `--status-critical` text and border, transparent background — not filled red, to avoid it competing visually with status badges
- Padding: 8px 14px, 13px Inter Medium label

### Inputs / Filters
- Border radius: 6px
- 1px `--border`, `--bg-surface` background
- Focus state: border shifts to `--text-secondary` (not `--accent` — accent stays reserved per §3)

### Status Badges / Pills
- Border radius: 999px (full pill) — the one place full-round is used, intentionally, to visually separate "status" from "container"
- 11px Inter Medium, uppercase optional
- Background: 15% opacity of the relevant status color; text: full-opacity status color
- Simulated data badge: dashed 1px border, `--status-simulated`, no fill

### Charts
- Bar/line charts only — no donut/gradient decorative charts (see §7)
- Axis labels always visible in `--text-secondary`, JetBrains Mono
- Bars/lines use status colors where the data has a pass/fail meaning; `--text-primary` at reduced opacity for neutral trend data

## 6. Layout

### Grid & Structure
- Fixed left sidebar: 240px, collapsible to 64px icon-only rail
- Main content: 12-column grid, 24px gutter
- Agent Overview: 5 cards, responsive down from 5-across to 3-across to 2-across to 1-across based on viewport (see breakpoints below) — never below 2-across on any supported demo viewport
- Decision Trail: single-column vertical timeline, max-width 840px, centered within content area for readability
- Human-Approval Queue: single-column list, full content width

### Spacing Scale
4 / 8 / 12 / 16 / 24 / 32 / 48px — no arbitrary values outside this scale. Card internal padding 16–20px; gap between cards 16px; section spacing (between major dashboard blocks) 32px.

### Responsive Rules
- **Desktop (≥1280px):** full sidebar, 5-across Agent Overview — this is the primary target, since the demo runs on a laptop/projector.
- **Tablet (768–1279px):** sidebar collapses to icon rail by default; Agent Overview drops to 3-across.
- **Mobile (<768px):** out of scope for v1 per the Frontend Spec Document — not a demo requirement. If time permits post-Phase-5, single-column stacked cards, sidebar becomes a bottom nav or hamburger drawer. Do not spend Phase 5 time here unless core views are already complete.

### 6.4 Simulated Data Treatment (applies across layout)
Any view/component showing Cost Agent output gets: dashed border (`--status-simulated`), a persistent "Simulated — not live billing data" label pinned to the component (not a tooltip, not collapsible), and exclusion from the accent-color highlight system. This must be visually obvious even to someone glancing at a screenshot out of context.

## 7. What Was Merged, and What Was Deliberately Excluded
Direction combines a dense, sidebar-nav, real-chart monitoring UI (structural/layout base — matches DevSwarm's actual data shape) with a status-pill/badge pattern from a second reference (borrowed for Agent Overview and Approval Queue statuses only).

**Explicitly excluded, and why:**
- Large decorative hero graphic (e.g. a globe/visualization with no data binding) — represents nothing real in DevSwarm; a purely decorative centerpiece invites "what does this actually show" under viva questioning, with no good answer.
- Sparkline-under-big-number tile pattern — real labeled bar/line charts (per §5 Charts) are more defensible under questioning than compressed decorative sparklines.
- Gradient donut/radial charts — replaced with plain labeled bars per §5; gradients read as decorative rather than data-accurate.
- Heavy single-color glow/ambient lighting effects — a single reserved accent color (§3) carries the same "draw the eye" function without the decorative cost.

## 8. Consistency with Prior Work
Reuse layout/interaction patterns already proven in AidFlow's Agent Dashboard (live polling of agent run history, decision-trail concept) where they fit — no need to reinvent a pattern you've already shipped and can speak to from experience.

## 9. Open Items
- Confirm JetBrains Mono is available/bundled without licensing friction (it's open-source/free — should be fine, but verify before Phase 5).
- Decide during Phase 5 whether dark mode is the only mode shipped (recommended: yes, skip a light-mode toggle — not worth the build time for a demo) or whether a light mode is required by any accessibility rubric item.
- Confirm sidebar icon set (consistent icon library, e.g. Lucide) before component build starts, so Deploy/Monitor/Security/Cost/Incident all get a coherent icon per agent.
