# Launch Accessibility Checklist

Run this checklist as part of the pre-launch gate. It is the accessibility subsection of the launch
Definition of Done, expanded with concrete, verifiable items against **WCAG 2.1 AA**. Accessibility
is a legal and moral baseline, not a nice-to-have — and it is cheap to verify with the right tooling
(axe-core, Lighthouse, screen readers) before launch, expensive to retrofit after.

## Keyboard & Focus

- [ ] **All interactive elements keyboard-operable** — every button, link, input, and control is reachable and activatable via keyboard (Tab/Enter/Space/Arrows).
- [ ] **Visible focus indicator** — the focused element has a clear, high-contrast outline; focus is never removed with `outline: none` without a replacement.
- [ ] **Logical tab order** — tab sequence follows visual/DOM order; no traps; focus does not jump unexpectedly.
- [ ] **No keyboard trap** — focus can always move away from any component (modals, menus) with Esc or Tab.
- [ ] **Skip link present** — a "skip to main content" link is the first focusable element on multi-section pages.
- [ ] **Focus management on dynamic content** — opening a modal moves focus into it; closing returns focus to the trigger; SPA route changes move focus to the new heading.

## Screen Readers & Semantics

- [ ] **Semantic HTML used** — real `<button>`, `<nav>`, `<main>`, `<table>`, `<label>` elements instead of divs-with-handlers.
- [ ] **Landmarks present** — `<header>/<nav>/<main>/<aside>/<footer>` give structure a screen reader can navigate.
- [ ] **Images have alt text** — meaningful images have descriptive `alt`; decorative images have `alt=""`.
- [ ] **Form inputs labeled** — every input has a programmatically-associated `<label>` (or `aria-label`/`aria-labelledby`); not placeholder-only.
- [ ] **Errors associated with fields** — validation errors use `aria-describedby` and `aria-invalid`; error text is announced, not just colored red.
- [ ] **Dynamic updates announced** — live regions (`aria-live`) announce async changes (toasts, counts, status).
- [ ] **Headings form a hierarchy** — one `<h1>`, no skipped levels; headings describe content, not styling.
- [ ] **Links have discernible text** — no "click here"; link text conveys destination/action out of context.
- [ ] **Tables structured** — `<th scope>` headers, `<caption>`, and proper association for data tables.

## Color & Contrast

- [ ] **Text contrast ≥ 4.5:1** (WCAG AA) for normal text; ≥ 3:1 for large text (≥24px or ≥18.66px bold).
- [ ] **UI component contrast ≥ 3:1** — borders, icons, and form controls against their background.
- [ ] **Not color-only** — state (error/success/selected) is conveyed by icon/text/shape, not color alone (red-green color blindness).
- [ ] **Focus visible independent of color** — the focus ring does not rely solely on a subtle color shift.

## Media & Motion

- [ ] **Video has captions** — synchronized captions for prerecorded audio; transcripts for audio-only.
- [ ] **No autoplay with sound** — or a clear, accessible pause/stop control exists.
- [ ] **Reduced motion respected** — `prefers-reduced-motion` disables non-essential animation; no vestibular-triggering movement.
- [ ] **Flashing limited** — no content flashes more than 3×/second (seizure risk).

## Responsive & Zoom

- [ ] **Works at 200% zoom** — content reflows without loss of function or horizontal scrolling on desktop.
- [ ] **Viewport meta correct** — `width=device-width, initial-scale=1`; no forced user-scalable=no.
- [ ] **Responsive without horizontal scroll** — at 320px width (smallest common), no content is cut off or requires scrolling sideways.
- [ ] **Touch targets ≥ 44×44px** — interactive controls have enough hit area for low-dexterity users.

## Tooling Verification

- [ ] **axe-core clean** — automated scan (axe DevTools / `@axe-core/playwright`) reports no violations.
- [ ] **Lighthouse a11y ≥ 90** — or all flagged items resolved with rationale.
- [ ] **Manual screen-reader pass** — at least one NVDA/VoiceOver/JAWS walkthrough of the critical flow.
- [ ] **Keyboard-only pass** — the entire critical flow completed without a mouse.
- [ ] **Color-contrast tool pass** — every text/UI pair verified (e.g. Colour Contrast Analyser).

## Using the Checklist

Automated tools catch ~30–50% of issues — the rest need a human with a keyboard and a screen reader.
Treat any failure here as a launch blocker for user-facing changes; an inaccessible launch excludes
users and invites legal exposure. Verify in the actual browser, not just the build.
