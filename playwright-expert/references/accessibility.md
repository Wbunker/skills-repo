# Accessibility Testing

Automated a11y scanning with **`@axe-core/playwright`** (the `AxeBuilder` API) — catches a meaningful
subset of WCAG issues in CI. Distinct from ARIA snapshot assertions (`toMatchAriaSnapshot`, see
[assertions.md](assertions.md)), which pin the accessibility *tree* rather than scan for violations.

## Contents
- [Install](#install)
- [Full-page scan](#full-page-scan)
- [Scan part of a page](#scan-part-of-a-page)
- [WCAG-tagged scan](#wcag-tagged-scan)
- [Handling known issues](#handling-known-issues)
- [Reusable axe fixture](#reusable-axe-fixture)
- [Exporting results as attachments](#exporting-results-as-attachments)
- [Best practices](#best-practices)

## Install

```bash
npm install @axe-core/playwright
```

## Full-page scan

Navigate, `analyze()`, assert no violations:

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('homepage', () => {
  test('should not have any automatically detectable accessibility issues', async ({ page }) => {
    await page.goto('https://your-site.com/');
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });
});
```

## Scan part of a page

`.include()` constrains the scan; `.exclude()` removes a subtree. Always `waitFor()` the target so
the DOM is settled before scanning:

```typescript
test('navigation menu should not have detectable a11y violations', async ({ page }) => {
  await page.goto('https://your-site.com/');
  await page.getByRole('button', { name: 'Navigation Menu' }).click();
  await page.locator('#navigation-menu-flyout').waitFor();
  const accessibilityScanResults = await new AxeBuilder({ page })
      .include('#navigation-menu-flyout')
      .analyze();
  expect(accessibilityScanResults.violations).toEqual([]);
});
```

## WCAG-tagged scan

Limit rules to specific WCAG success criteria with `.withTags()` (common: `wcag2a`, `wcag2aa`,
`wcag21a`, `wcag21aa`):

```typescript
test('should not have any WCAG A or AA violations', async ({ page }) => {
  await page.goto('https://your-site.com/');
  const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();
  expect(accessibilityScanResults.violations).toEqual([]);
});
```

## Handling known issues

Exclude an element with a known problem, or disable a specific rule (prefer `disableRules` — it stays
narrow as the DOM changes):

```typescript
// exclude a subtree
const results = await new AxeBuilder({ page }).exclude('#element-with-known-issue').analyze();

// disable a rule everywhere
const results2 = await new AxeBuilder({ page }).disableRules(['duplicate-id']).analyze();
```

To lock in the *current* set of issues without snapshotting brittle HTML, snapshot a **fingerprint**:

```javascript
// my-test-utils.js
function violationFingerprints(accessibilityScanResults) {
  const violationFingerprints = accessibilityScanResults.violations.map(violation => ({
    rule: violation.id,
    targets: violation.nodes.map(node => node.target),
  }));
  return JSON.stringify(violationFingerprints, null, 2);
}
```
```javascript
expect(violationFingerprints(accessibilityScanResults)).toMatchSnapshot();
```

## Reusable axe fixture

Encapsulate your standard tags/exclusions in a [fixture](fixtures.md) so every test gets a
pre-configured builder:

```typescript
// axe-test.ts
import { test as base } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

type AxeFixture = {
  makeAxeBuilder: () => AxeBuilder;
};

export const test = base.extend<AxeFixture>({
  makeAxeBuilder: async ({ page }, use) => {
    const makeAxeBuilder = () => new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
        .exclude('#commonly-reused-element-with-known-issue');
    await use(makeAxeBuilder);
  }
});
export { expect } from '@playwright/test';
```

```typescript
// usage
import { test, expect } from './axe-test';

test('example using custom fixture', async ({ page, makeAxeBuilder }) => {
  await page.goto('https://your-site.com/');
  const accessibilityScanResults = await makeAxeBuilder()
      .include('#specific-element-under-test')
      .analyze();
  expect(accessibilityScanResults.violations).toEqual([]);
});
```

## Exporting results as attachments

Attach the full results to the report (visible in the HTML report / [Trace Viewer](trace-viewer.md)
Attachments tab):

```typescript
test('example with attachment', async ({ page }, testInfo) => {
  await page.goto('https://your-site.com/');
  const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
  await testInfo.attach('accessibility-scan-results', {
    body: JSON.stringify(accessibilityScanResults, null, 2),
    contentType: 'application/json',
  });
  expect(accessibilityScanResults.violations).toEqual([]);
});
```

## Best practices

- Automated scans catch only a fraction of issues — pair with manual review and assistive-tech
  testing (e.g. Accessibility Insights for Web).
- Prefer `.disableRules()` over `.exclude()` for preexisting issues so new elements still get scanned.
- Always `waitFor()` the relevant state before `analyze()`.
- Use violation fingerprints, not full-object snapshots, to avoid fragile HTML diffs.
