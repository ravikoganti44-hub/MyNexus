# Expert Review — MyNexus Desktop Client
**Date:** 2026-07-18  
**Scope:** `dashboard.py`, `premium_button.py`, `tokens.py`, `motion.py`, `onboarding.py`, `activities.py`, `budget.py`, `calendar_view.py`, `notification_center.py`, `ai_insights_panel.py`, `settings.py`, `stat_card.py`, `integrations.py`, `document_vault.py`, `net_worth.py`

---

## 1. First Impression
The current revision shows concrete progress: consistent token vocabulary across 14 surfaces, one verified animation hook, and a bounded collapse pattern. The remaining detractor is fragmented micro-styling in `connected_apps.py` and residual action-button rgba fragments in `document_vault.py`.

## 2. Visual Hierarchy
Strength: Dashboard now uses a consistent `color.text.primary` / `color.text.secondary` / `color.accent.primary` hierarchy.
Gap: `calendar_view.py` still uses category-specific hex fragments at runtime rather than token categories, so semantic emphasis is context-dependent rather than theme-driven.

## 3. Typography
Consistent `Segoe UI` weights across dashboard, onboarding, premium_button.
Gap: `activities.py` feed timestamps are `11px` while body copy is `13px`; scale discipline is slightly off for premium positioning.

## 4. Micro-Interaction Language
The `CollapsibleSection` height animation using `motion_duration("base")` is the first real motion token exercised.
Gap: No analogous motion on `PremiumButton`, `StatCard`, or table row selection. Motion is still effectively a one-off dashboard surface affordance.

## 5. Information Architecture
Delayed passphrase + first-action CTA in onboarding is correct for trust/science-compliant first-run.
Remaining friction: `dashboard.py` stat-card row still uses emoji glyphs, which read as placeholder rather than branded iconography, especially for HNWI positioning.

## 6. Engagement Mechanics
Streak counter and weekly insight chips are present but underutilized—no progressive disclosure path (e.g., streak milestone modal, share CTA, or earned badge state).

## 7. Pricing Psychology
Not yet implemented in desktop UI. Current premium language is theme-level ("primary/sec") rather than tier gate. Recommend deferring paywall chrome until tier labels are semantically distinct from accent tokens.

## 8. Differentiation
Offline-first posture is a genuine wedge against cloud-only competitors. The “paused warning” UX (no nag loops during reminders) is correct for a premium Windows local-first tool.
Gap: `connected_apps.py` still pulls entirely different palette constants, breaking differentiation at the app-integration surface.

## 9. Friction Points
- `document_vault.py` action-button fragments rely on rgba literals; inconsistent hover/disabled feel.
- `budget.py` uses both legacy `html`-style inline styles and token styles on adjacent widgets; mental model split.
- `net_worth.py` category colors are additive module-level constants; future sync requires manual mapping rather than token derivation.

## 10. Trust & Skepticism Handling
First-run CTA + delayed passphrase layout matches privacy-first messaging. Empty states in `activities.py` and `dashboard.py` use neutral phrasing rather than fear-based urgency.
Gap: No explicit “encrypted local-only” badge on vault or settings screens despite that being the differentiator.

## 11. Competitive Positioning
No direct competitor in “offline-first encrypted personal OS on Windows.” Closest analogs (Notion, Obsidian, Solid Explorer) trade granularity for cloud sync. MyNexus can win on trust and offline velocity.

## 12. Accessibility & Edge Cases
Contrast: current tokens are mostly sufficient. Exception: `color.text.tertiary` usage on `search_hint` over `color.bg.secondary` needs manual back-stop because Qt stylesheet contrast ratios vary by display profile.
Keyboard: `CollapsibleSection` uses mouse-only toggle; no accessible keyboard affordance.

## 13. Recommended Next Actions (ordered by impact / risk)
1. Tokenize remaining `connected_apps.py` dividers, dialog chrome, and hover states (`high risk`, bounded by alignment to existing token values).
2. Replace `document_vault.py` action-button rgba literals with token-backed `color.semantic.*` + reusable hover rgba helpers.
3. Standardize typographic scale in `activities.py` to 12/13/15 rhythm.
4. Swap dashboard stat-card emojis for `IconManager` or SVG glyphs.
5. Add keyboard toggle handler and focus indicator to `CollapsibleSection`.
6. Add `color.text.muted` + `color.text.inverse` token coverage if more components reference muted text.
