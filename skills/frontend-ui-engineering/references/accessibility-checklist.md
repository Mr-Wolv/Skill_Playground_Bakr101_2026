# Frontend UI Engineering — Accessibility (WCAG 2.1 AA) Checklist

A concrete checklist for building **accessible, WCAG 2.1 AA** user interfaces. Complements the Accessibility section in `SKILL.md`. Use it during build and as a pre-merge gate. Each item is verifiable by inspection, keyboard test, or an automated tool (axe-core / Lighthouse a11y).

Severity legend: **[Critical]** = blocks merge (blocks AT users); **[High]** = required for AA; **[Med]** = strong recommendation; **[Low]** = polish.

---

## 1. Semantics & Document Structure

- [ ] **[Critical] Native HTML elements used for their purpose** — `<button>` for actions, `<a>` for navigation, `<nav>/<main>/<header>/<footer>` for landmarks, `<table>` for tabular data. Don't reinvent with `<div role=...>` when a native element exists.
- [ ] **[Critical] One `<h1>` per page; heading levels not skipped** (h1 → h2 → h3, never h1 → h3). Heading style is not applied to non-heading content.
- [ ] **[High] Landmark regions present and correctly nested** — `main` wraps primary content; only one `main`; `banner`/`contentinfo` used once per page.
- [ ] **[High] Language declared** — `<html lang="en">` (and `lang` on parts in a different language) so screen readers pick the right voice.
- [ ] **[High] Page `<title>` is descriptive and unique** — identifies the page within the app (not "Home").
- [ ] **[Med] Lists use real list elements** (`<ul>/<ol>/<li>` or `role="list"`) — not styled `<div>`s — so AT announces count and structure.
- [ ] **[Med] `<html>`/`<body>` has no `tabindex` misuse**; focus order follows DOM/visual order.
- [ ] **[Low] `scope`/`headers` on table cells** for complex tables so headers associate correctly.

## 2. Keyboard Navigation

- [ ] **[Critical] Every interactive element is keyboard reachable** — `Tab` reaches all buttons, links, inputs, controls. A `<div onClick>` with no `tabIndex`/`role` is not focusable — use a native element.
- [ ] **[Critical] Custom interactive widgets follow the ARIA keyboard pattern** — Enter/Space activate buttons; Arrow keys move within menus/tabs/comboboxes; Esc closes dialogs; Home/End for lists.
- [ ] **[High] Visible focus indicator on every focusable element** — never `outline: none` without a replacement; focus ring must be clearly visible.
- [ ] **[High] Logical focus order** — follows the visual/DOM order; no trap; no element focusable before its context makes sense.
- [ ] **[High] No keyboard trap** — focus can always move away (except modal dialogs while open, which must trap *and* release on close).
- [ ] **[Med] Skip link / "skip to main content"** present on multi-section pages for keyboard and screen-reader users.
- [ ] **[Med] Shortcut keys don't conflict** with screen-reader or browser shortcuts; document them.
- [ ] **[Low] `Tab` doesn't activate** controls unexpectedly (activation on focus is an anti-pattern).

## 3. ARIA (only when needed)

- [ ] **[Critical] ARIA used to supplement, not replace, semantics** — first reach for native elements; add ARIA only when native can't express the state.
- [ ] **[Critical] All interactive controls have an accessible name** — visible text, `aria-label`, `aria-labelledby`, or associated `<label>`. Icon-only buttons get `aria-label="Close"`.
- [ ] **[High] State is exposed** — `aria-expanded`, `aria-selected`, `aria-checked`, `aria-pressed` reflect the real UI state and update on interaction.
- [ ] **[High] `aria-live` regions for dynamic updates** — status/error/toast messages announced (polite vs assertive); `role="status"`/`role="alert"`.
- [ ] **[High] `role` matches behavior** — a `role="button"` element handles Enter *and* Space; mismatched roles confuse AT.
- [ ] **[Med] Avoid `aria-hidden="true"` on focusable descendants** — it hides content from AT while keyboard can still reach it (conflict); pair with `inert`/`tabindex=-1`.
- [ ] **[Med] No redundant/conflicting ARIA** — don't put `role="heading"` on an `<h2>`, don't label something twice contradictorily.
- [ ] **[Low] Test with an actual screen reader** (NVDA/VoiceOver), not just automated checks — ARIA correctness needs ears.

## 4. Forms & Labels

- [ ] **[Critical] Every input has a programmatically associated `<label>`** (`for`/`id` or wrapping label). Placeholder is NOT a label.
- [ ] **[Critical] Errors are announced and linked to the field** — `aria-invalid`, `aria-describedby` pointing to the error text; focus moved to the first invalid field.
- [ ] **[High] Required/optional state is conveyed in text**, not by color alone (e.g. "(required)" not just a red asterisk).
- [ ] **[High] Instructions/help text associated** via `aria-describedby` so the field's purpose is announced.
- [ ] **[High] Groups of related fields use `<fieldset>/<legend>`** (radio groups, address blocks).
- [ ] **[Med] Autocomplete attributes set** on name/email/phone/etc. (`autocomplete="email"`) for faster, safer input.
- [ ] **[Med] Input type & mode correct** (`type="email"`, `inputmode="numeric"`) — brings up the right keyboard on mobile.
- [ ] **[Low] Don't disable submit on validation prematurely** in a way that traps keyboard users; allow submit to show errors.

## 5. Color & Contrast

- [ ] **[Critical] Text contrast ≥ 4.5:1** (normal text), **≥ 3:1** (large text ≥ 24px or ≥ 18.66px bold). Check with a contrast tool.
- [ ] **[Critical] UI component contrast ≥ 3:1** — borders, icons, form controls against adjacent colors.
- [ ] **[High] Information never conveyed by color alone** — pair color with text/icon/pattern (error = icon + text, not red-only).
- [ ] **[High] Focus indicator has sufficient contrast** and isn't relying on a low-contrast outline.
- [ ] **[Med] Dark mode / forced-colors support** — respect `prefers-color-scheme`; test Windows High Contrast / `forced-colors`.
- [ ] **[Low] Don't use pure black/white only**; ensure hover/disabled states remain distinguishable for low-vision users.

## 6. Focus Management

- [ ] **[Critical] Focus moves into a dialog/modal on open** (to the first control or close button) and returns to the trigger on close.
- [ ] **[Critical] Focus is trapped inside the open modal** (Tab cycles within) and released on close — no escaping behind the overlay.
- [ ] **[High] Focus moves to new content on route/SPA navigation** — announce the new page/region (e.g. move focus to the `main` heading or use `aria-live`).
- [ ] **[High] `aria-busy` on loading regions**; loading/empty/error states are announced, not silent.
- [ ] **[Med] Restore focus after async actions** (e.g. after saving a form, return focus sensibly; don't drop it to `body`).
- [ ] **[Low] Avoid stealing focus on mount** for non-dialog content (surprises screen-reader and keyboard users).

## 7. Images, Media & Alt Text

- [ ] **[Critical] Meaningful images have descriptive `alt`** — conveys the content/purpose; decorative images use `alt=""` (intentionally empty, not missing).
- [ ] **[Critical] Icons/icon-buttons have text or `aria-label`** — an unlabeled icon is invisible to AT.
- [ ] **[High] Complex images (charts, diagrams) have extended description** (`aria-describedby` or a visible caption/long description).
- [ ] **[High] Functional images link/button has alt describing the action** ("Search", not "magnifier.png").
- [ ] **[High] Video/audio have captions/transcripts** — captions for spoken audio; transcripts for podcasts.
- [ ] **[Med] `prefers-reduced-motion` respected** — disable/reduce non-essential animation/autoplay.
- [ ] **[Med] Autoplay media has pause/stop and no sound-on-by-default** violating user control.
- [ ] **[Low] SVG with meaning has `<title>`/`role="img"` + `aria-label`**.

## 8. Screen-Reader & Testing

- [ ] **[Critical] Page is navigable by screen reader** — headings list, landmarks, and links are announced correctly (test NVDA + VoiceOver).
- [ ] **[High] Run axe-core / Lighthouse a11y in CI** — zero critical/serious violations; treat new violations as build failures.
- [ ] **[High] Tab through the whole page** manually — no unreachable control, no surprise order, no invisible focus.
- [ ] **[Med] Check zoom to 200%** — content remains usable, no loss of info or overlap (WCAG 1.4.10).
- [ ] **[Med] Test with keyboard only, no mouse** — the entire flow (including menus, dialogs, drag alternatives) works.
- [ ] **[Low] Verify `role`/`state` changes are announced** during interaction (not just present in DOM).

## 9. Responsive & Target Size

- [ ] **[High] Works at 320px width** without horizontal scroll of the whole page (reflow, not zoom-out).
- [ ] **[Med] Touch targets ≥ 24×24px (aim 44×44px)** — buttons/links easy to hit; spacing prevents mis-taps.
- [ ] **[Med] Text reflows, doesn't overlap** at all breakpoints (320/768/1024/1440).
- [ ] **[Low] Orientation not locked** unless essential (e.g. landscape-only game); support both.

---

### How to use this list
- Build accessibly from the start — retrofitting a11y is 3× harder.
- Automated tools (axe/Lighthouse) catch ~30–40% of issues; the rest need keyboard + screen-reader testing (sections 2, 6, 8).
- "Color as the sole indicator of state" and "no keyboard nav test" are red flags in `SKILL.md`.
- Do not modify `SKILL.md`. This file is the supporting reference for `frontend-ui-engineering`.
