# MyNexus — Phase 1 Live Rollout Plan
Last updated: July 18, 2026

## Phase 1 Progress — Foundation (Weeks 1–2)
Goal: One token-backed design system, reduced IA friction, and a cleaner first-run path before premium feel work.

### 1. Design Tokens + Motion
- [x] Single token source: `src/ui/styles/tokens.py`
  - Dark and light semantic color maps
  - Typographic scale and weight tokens
  - Spacings, radius, shadows
- [x] Token helpers
  - `token(path)` for colors/strings
  - `spacing(path)` for integer pixel values
- [x] Motion language: `src/ui/styles/motion.py`
  - `duration()` and `easing()` helpers
- [ ] Hook motion into 1–2 interactions
  - Sidebar expand/collapse
  - Page switch fade/slide
- [ ] AUDIT remaining component files for inline hex values

### 2. Theme Migration
- [x] Theme engine updated to consume token map
  - Shell background/border
  - Scroll area palette
  - Cards, tables, badges, charts
- [x] Migrated `src/ui/components/sidebar.py`
- [x] Migrated `src/ui/components/dashboard.py`
- [ ] Migrate remaining files:
  - `activities.py`
  - `budget.py`
  - `net_worth.py`
  - `document_vault.py`
  - `integrations.py`
  - `connected_apps.py`
  - `settings.py`
  - `calendar_view.py`
  - `notification_center.py`
  - `ai_insights_panel.py`

### 3. Refined Information Architecture
- [x] Reduced top-level rail from 9 to:
  - Dashboard
  - Activities
  - Budget Tracker
  - Net Worth
  - Document Vault
  - Connected Apps
  - Integrations
  - Calendar View
  - Settings
- [ ] Collapse related views under tabs
  - Calendar tab inside Activities
  - Settings categories
- [ ] Remove redundant static sections from Dashboard until collapsible sections are ready

### 4. First-Time Experience
- [x] Delayed passphrase setup
  - Onboarding runs on first launch
  - Passphrase offered later from Settings → Security
- [x] Onboarding wizard tokenized and simplified:
  - Welcome
  - Features
  - Ready
- [ ] Add one guided CTA after onboarding:
  - “Add your first activity”
  - “Set up your first budget”

### 5. Dashboard Collapse Strategy
- [ ] Introduce `CollapsibleSection` helper in `dashboard.py`
- [ ] Collapse lower-priority sections by default:
  - Connected Apps
  - Streaks
  - Weekly Summary
  - Recent Activity
  - AI Insights
- [ ] Make Overdue section dominant if overdue count > 0

### 6. Visual Polish
- [ ] Remove decorative emojis from chrome
  - Replace with icon tokens in sidebar and dashboard
- [ ] Standardize separators to one token
- [ ] Ensure consistent borders and shadow tokens
- [ ] Verify focus states for keyboard navigation

## Current Blockers
- `DocumentManager.get_expired_documents` missing
  - Causes `Error loading statistics` at runtime
  - Blocks Document Vault stats rendering

## What not to do
- Do not overwrite `dashboard.py` without exact diff plan
- Do not force passphrase on first launch
- Do not add more top-level nav items

## Next recommended moves
1. Finish `dashboard.py` collapse with exact patches only
2. Audit tokens in `activities.py`, `budget.py`, `net_worth.py`
3. Hook `motion.py` into sidebar expand/collapse and page transitions
4. Implement `get_expired_documents` in document manager
