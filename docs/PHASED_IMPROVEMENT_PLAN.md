# MyNexus — Phased Improvement Plan
Target: Premium, world-class personal OS experience  
Current grade: B-  
Target grade: A

---

## Phase 1 — Foundation (Weeks 1–2)
**Goal:** One unified design language, simplified information architecture, and a first-run experience that delivers value before asking for commitment.

### Deliverables
1. **Single-token theme system**
   - Replace all inline `#30363d` strings with references to `THEME_TOKENS`.
   - Add spacing, radius, shadow, motion tokens.
   - File: `src/ui/styles/theme.py`

2. **Motion language**
   - Page transitions: 140ms ease-out.
   - Card hover lift: 80ms.
   - Button press: scale 0.97.
   - File: `src/ui/styles/motion.py` (new)

3. **Information architecture rewrite**
   - Reduce sidebar to: Home, Tasks, Money, Vault, Settings.
   - Budget and Net Worth move under Money (tabbed).
   - Connected Apps move under Vault (tabbed).
   - File: `src/main.py`, `src/ui/components/sidebar.py`

4. **First-time experience reset**
   - Remove passphrase wall from first launch.
   - Add progressive dashboard empty states with primary CTAs.
   - Delay MasterPassphraseDialog until second session or Settings trigger.
   - File: `src/main.py`, `src/ui/components/onboarding.py`

5. **Dashboard collapse**
   - Keep only 4 KPIs + 1 dominant focus section.
   - Move streaks to subtle trend indicator.
   - Remove Recent Activity feed from Home.
   - File: `src/ui/components/dashboard.py`

### Verification
- [ ] Theme token coverage: grep for hardcoded colors → 0 hits.
- [ ] IA: sidebar has ≤ 5 top-level items.
- [ ] FTUE: fresh install launches dashboard without passphrase prompt.
- [ ] Dashboard: scroll height ≤ 1.5 viewports on 1400×900.

---

## Phase 2 — Money Hub (Weeks 3–6)
**Goal:** Make Budget and Net Worth first-class, differentiated, and conversion-driving.

### Deliverables
1. **Budget cash-flow header**
   - New card row: Income → Bills → Goals → Discretionary.
   - “Upcoming bills” mini-table with Pay / Mark Paid actions.
   - File: `src/ui/components/budget.py`

2. **Category health strip**
   - Replace progress bars with 30-day sparkline-style strip chart per category.
   - Trend arrows: up/down vs last period.
   - File: `src/ui/components/budget.py`

3. **Goals framework**
   - Add `Goal` model and `GoalManager`.
   - Goals: Emergency fund, Vacation, Monthly max.
   - Progress ring + days-to-target per goal.
   - File: `src/database/models.py`, `src/database/operations.py`, `src/ui/components/budget.py`

4. **Net Worth enrichments**
   - Cash buffer card: (Savings + Checking) − (14-day bills).
   - Monthly change drill-down.
   - FIRE ETA simplified to readiness % + monthly savings required.
   - File: `src/ui/components/net_worth.py`

5. **Bank import UX**
   - Move Import Statement to persistent header.
   - Post-import success banner: “3 new expenses added, 128 recognized.”
   - File: `src/ui/components/budget.py`, `src/ui/components/data_importers.py`

### Verification
- [ ] Budget header shows 4 cash-flow KPIs.
- [ ] Goals persist across refresh and export.
- [ ] Net Worth shows cash buffer.
- [ ] Import banner appears after CSV load.

---

## Phase 3 — Task Intelligence (Weeks 7–9)
**Goal:** Activities become a triage surface, not just a table.

### Deliverables
1. **Priority / Eisenhower flag**
   - Add `priority` field to `Activity` model.
   - Quick-set column in table and edit dialog.
   - Filter/sort by priority.
   - File: `src/database/models.py`, `src/ui/components/activities.py`

2. **Quick capture bar**
   - Smart parser in Dashboard and Tasks headers.
   - Input: “Call dentist Monday $100” → activity + optional budget link.
   - File: `src/ui/components/activities.py`, `src/core/ai_engine.py`

3. **Calendar ↔ Activities linked workflow**
   - Double-click calendar cell → new activity pre-filled with date.
   - Calendar cell context menu: add activity, view day’s tasks.
   - File: `src/ui/components/calendar_view.py`

4. **Focus mode**
   - Toggle: hide all columns except Title + Days Left + Actions.
   - File: `src/ui/components/activities.py`

### Verification
- [ ] Priority column/filter functional.
- [ ] Quick parser correctly splits title/date/budget hint.
- [ ] Calendar double-click opens pre-filled activity dialog.
- [ ] Focus mode reduces visible columns to 4.

---

## Phase 4 — Premium Polish (Weeks 10–12)
**Goal:** Execution detail that moves perception from “good build” to “premium product.”

### Deliverables
1. **Fluent-style title bar**
   - Frameless window with custom traffic lights.
   - Mica/blur on Windows 11.
   - Drag regions, double-click maximize.
   - File: `src/main.py`, new `src/ui/components/title_bar.py`

2. **Icon system replaces emoji in chrome**
   - Add `IconManager` coverage for sidebar, headers, empty states.
   - Remove emoji from sidebar, page titles, section headers.
   - File: `src/ui/styles/icon_manager.py`, all component files

3. **Windows toast integration**
   - Replace custom notification popups with `wintoast` or `plyer` native toasts.
   - Respect Focus Assist.
   - File: `src/notifications/notify.py`

4. **Empty states and micro-interactions**
   - Every empty table shows primary CTA + illustration/icon.
   - Confetti on first activity completion, budget under limit, etc.
   - File: all widgets with empty states

5. **Accessibility audit**
   - Contrast check on all text tokens.
   - Focus indicators on all interactive elements.
   - Keyboard navigation through all pages.
   - File: `src/ui/styles/theme.py`, all components

### Verification
- [ ] No emoji remain in chrome/sidebar/titles.
- [ ] Title bar supports drag, double-click maximize, system menu.
- [ ] Toasts appear as Windows native notifications.
- [ ] Contrast ratios: all text ≥ 4.5:1.

---

## Phase 5 — Commercial Readiness (Weeks 13–16)
**Goal:** Make the app sellable and sync-ready.

### Deliverables
1. **License and trial UI**
   - Trial start screen: email gate, 30-day countdown.
   - Activate / Plans / Restore purchase.
   - File: new `src/ui/components/licensing.py`

2. **Encrypted sync architecture**
   - Optional cloud sync for Pro users.
   - E2E encrypted payload; server never sees plaintext.
   - Files: new `src/sync/` module, updated `README.md`

3. **Installer and store polish**
   - App icon 256×256.
   - Installer brand consistency.
   - File: `MyNexus.iss`, `assets/icons/`

4. **Marketing parity**
   - Screenshots updated to premium surfaces.
   - README/installer copy rewrite.
   - File: `README.txt`, `INSTALLATION.md`

### Verification
- [ ] Trial flow: email → 30-day timer → upgrade prompt.
- [ ] Sync: local changes replicate to remote without plaintext exposure.
- [ ] Installer runs clean on fresh Windows 11 VM.

---

## Execution Rules
1. **One phase at a time.** Complete Phase 1 verification before Phase 2 starts.
2. **Theme tokens first.** No new component styling until token system is in place.
3. **IA before features.** Sidebar reduction precedes any new page work.
4. **No emoji in chrome.** Enforced from Phase 1 onward.
5. **Commercial features behind flags.** Free vs Pro gated by license check, not code branches.

---

## Current Blockers
- Full unittest discovery segfaults on Windows; run individual files until resolved.
- `DocumentManager.get_expired_documents` missing; add before Phase 4 document polish.

---

## Success Criteria by End of Phase 1
- App launches to dashboard in ≤ 2 seconds on reference hardware.
- First-run user can add an activity or budget limit in ≤ 8 seconds without passphrase.
- Sidebar has ≤ 5 items.
- Zero inline hardcoded theme colors in component files.
