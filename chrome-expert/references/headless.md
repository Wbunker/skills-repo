# Chrome Headless

Run Chrome without a UI — for automation, testing, scraping, and rendering.

## Two Headless Modes

| Mode | Flag | Binary | Best for |
|------|------|--------|----------|
| New headless | `--headless=new` | `google-chrome` | Full Chrome fidelity, extensions, PWAs |
| Headless shell | (standalone) | `chrome-headless-shell` | Fast scraping/rendering, CI, no X11 needed |

### `--headless=new` (Chrome 112+)

Full Chrome browser with no visible window. Requires X11/Wayland + D-Bus on Linux (use `Xvfb` or set `DISPLAY`).

```bash
google-chrome \
  --headless=new \
  --remote-debugging-port=9222 \
  --disable-gpu \
  --no-sandbox \              # needed in containers
  --disable-dev-shm-usage \  # needed in Docker (shared memory)
  https://example.com

# Screenshot
google-chrome --headless=new --screenshot=/tmp/shot.png https://example.com

# Print to PDF
google-chrome --headless=new --print-to-pdf=/tmp/out.pdf https://example.com

# Run JavaScript and exit
google-chrome --headless=new --dump-dom https://example.com
```

### `chrome-headless-shell` (Chrome 120+)

Lightweight Chromium content shell. No X11, no D-Bus. Faster startup. No extension support.

```bash
# Install via Puppeteer tooling
npx @puppeteer/browsers install chrome-headless-shell@stable

# Or via Chrome for Testing
# https://googlechromelabs.github.io/chrome-for-testing/

# Run
./chrome-headless-shell --remote-debugging-port=9222 https://example.com
```

## Chrome for Testing

Provides pinned, versioned Chrome binaries + matching ChromeDriver for reproducible tests.
No auto-updates, no "first run" dialogs.

- **Discovery endpoint:** `https://googlechromelabs.github.io/chrome-for-testing/`
- **JSON API:** `https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json`

```bash
# Install specific channel via Puppeteer browsers tool
npx @puppeteer/browsers install chrome@stable
npx @puppeteer/browsers install chrome@canary
npx @puppeteer/browsers install chromedriver@stable
npx @puppeteer/browsers install chrome-headless-shell@stable
```

## Puppeteer (Node.js)

High-level CDP wrapper. Bundles and manages its own Chrome.

```bash
npm install puppeteer
```

```js
import puppeteer from 'puppeteer';

const browser = await puppeteer.launch({
  headless: true,           // true = headless shell, 'new' = full headless
  args: ['--no-sandbox'],   // needed in Docker
});

const page = await browser.newPage();
await page.setViewport({ width: 1280, height: 800 });
await page.goto('https://example.com', { waitUntil: 'networkidle2' });

// Screenshot
await page.screenshot({ path: 'screenshot.png', fullPage: true });

// PDF
await page.pdf({ path: 'output.pdf', format: 'A4', printBackground: true });

// Get text content
const title = await page.title();
const h1 = await page.$eval('h1', el => el.textContent);

// Click and type
await page.click('#search');
await page.type('#search', 'query', { delay: 50 });
await page.keyboard.press('Enter');
await page.waitForNavigation();

// Intercept requests
await page.setRequestInterception(true);
page.on('request', req => {
  if (req.resourceType() === 'image') req.abort();
  else req.continue();
});

// Run CDP directly
const client = await page.target().createCDPSession();
await client.send('Network.enable');
client.on('Network.responseReceived', event => {
  console.log(event.response.url, event.response.status);
});

await browser.close();
```

## Playwright (Node.js / Python)

Cross-browser (Chrome, Firefox, WebKit). More reliable auto-waiting. Preferred for test suites.

```bash
npm install @playwright/test
npx playwright install chromium
```

```js
// playwright.config.js
import { defineConfig } from '@playwright/test';
export default defineConfig({
  use: { browserName: 'chromium', headless: true }
});
```

```js
import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1280, height: 800 },
  userAgent: 'My Bot/1.0',
});
const page = await context.newPage();

await page.goto('https://example.com');

// Smart auto-waiting selectors
await page.click('button:has-text("Submit")');
await page.fill('input[name="email"]', 'test@example.com');
await page.waitForSelector('.result');

const text = await page.locator('h1').textContent();

// CDP access
const cdp = await context.newCDPSession(page);
await cdp.send('Network.enable');

await browser.close();
```

```python
# Python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com")
    print(page.title())
    page.screenshot(path="shot.png")
    browser.close()
```

## Docker / CI Configuration

Common flags for containerized environments:

```bash
google-chrome --headless=new \
  --no-sandbox \
  --disable-setuid-sandbox \
  --disable-dev-shm-usage \
  --disable-accelerated-2d-canvas \
  --disable-gpu \
  --remote-debugging-port=9222
```

Puppeteer in Docker:
```js
const browser = await puppeteer.launch({
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  executablePath: process.env.CHROME_PATH || undefined,
});
```

## Common Flags Reference

| Flag | Purpose |
|------|---------|
| `--headless=new` | Full headless mode |
| `--remote-debugging-port=9222` | Enable CDP |
| `--no-sandbox` | Required in containers/root |
| `--disable-dev-shm-usage` | Use /tmp instead of /dev/shm (Docker) |
| `--disable-gpu` | Disable GPU (headless servers) |
| `--window-size=1280,800` | Set window size |
| `--user-data-dir=/tmp/x` | Separate profile (avoid conflicts) |
| `--incognito` | Start in incognito mode |
| `--proxy-server=host:port` | Use proxy |
| `--disable-extensions` | Don't load extensions |
| `--dump-dom` | Print page DOM and exit |
| `--screenshot=path.png` | Screenshot and exit |
| `--print-to-pdf=path.pdf` | PDF and exit |
| `--virtual-time-budget=5000` | Fast-forward timers by N ms |
