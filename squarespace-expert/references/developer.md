# Squarespace Developer Features Reference

## Table of Contents
1. [Custom CSS](#custom-css)
2. [Code Injection](#code-injection)
3. [Template Development](#template-development)
4. [Git Integration](#git-integration)
5. [JSON Data Access](#json-data-access)
6. [Developer Server](#developer-server)
7. [Extensions Marketplace](#extensions-marketplace)
8. [Third-Party Integrations](#third-party-integrations)

---

## Custom CSS

**Access:** Admin → Design → Custom CSS

**Capabilities:**
- Add site-wide CSS overrides
- Target any Squarespace-generated class or element
- Upload CSS asset files (referenced via URL in your CSS)
- Editor includes file storage for imported assets (fonts, images)

**Best practices:**
- Squarespace class names can change between template versions; use stable structural selectors when possible
- Prefer Custom CSS over code injection for style changes
- Use the browser inspector to identify target selectors

**Plan requirement:** Available on all paid plans

---

## Code Injection

**Access:** Admin → Settings → Advanced → Code Injection

**Injection points:**

| Location | Behavior |
|---|---|
| Header | Inserted into `<head>` on every page |
| Footer | Inserted before closing `</body>` on every page |
| Lock Page | Displays above password field on protected pages |
| Order Confirmation Page | Runs on order confirmation; supports `{orderId}`, `{customerEmailAddress}` tokens |
| Order Status Page | Runs on order status; same tokens available |

**Per-page injection:** Available via Page Settings → Advanced on individual pages

**Rules:**
- Wrap JavaScript in `<script></script>` tags
- Wrap CSS in `<style></style>` tags
- Checkout pages do NOT support code injection
- Temporarily disable custom scripts if they break editing

**Use cases:** Analytics (GA4, Hotjar), live chat widgets, domain verification tags, custom tracking pixels, A/B testing scripts, third-party embeds

**Plan requirement:** Core, Plus, Advanced, Business, and Commerce plans

---

## Template Development

**Squarespace template system:**
- Templates are built with Squarespace's **JSON-Template language** — a minimal templating language layered on top of JSON data
- Full control over markup, styles, and scripts
- Can create custom, Squarespace-hosted templates

**Template file structure:**
- `template.conf` — template metadata and navigation config
- `stylesheets/` — LESS/CSS files
- `scripts/` — JavaScript files
- `blocks/` — reusable template partials
- `collections/` — page type templates
- `assets/` — images and static files

**JSON-Template language basics:**
- Access data with dot notation: `{title}`, `{item.name}`
- Conditionals: `{.if condition}...{.end}`
- Iteration: `{.repeated section items}...{.end}`
- Formatters: `{date|date %B %d, %Y}`

**Query pages as JSON:** Append `?format=json` to any page URL to inspect its data structure (useful for template development)

---

## Git Integration

**Access:** Admin → Settings → Developer Tools → Git

**Capabilities:**
- All template repos are automatically exposed via Git
- Push/pull template changes via Git workflow
- Supports team collaboration (multiple contributors)
- Full rollback to any previous commit

**Workflow:**
1. Enable Git in Developer Tools
2. Clone the repo URL provided
3. Edit template files locally
4. Push changes — live on site immediately
5. Use branches for staging; merge to deploy

**Note:** Git integration is for template files only, not content data

---

## JSON Data Access

**Page as JSON:** Append `?format=json` to any Squarespace page URL:
```
https://yoursite.com/about?format=json
https://yoursite.com/blog?format=json
https://yoursite.com/shop?format=json
```

Returns structured JSON of all page content, collections, and configuration.

**Use cases:**
- Inspect data structure when building templates
- Build custom integrations that read page content
- Debug template variable availability
- Feed content to external systems

**Site collection JSON:** Most collection types (blog, products, portfolio) support `?format=json` and return arrays of items with full metadata.

---

## Developer Server

**Purpose:** Local development environment that mirrors Squarespace's rendering pipeline

**Features:**
- Edit template files locally with preferred tools
- Live reload on file changes
- Supports native build tools (Webpack, Gulp, etc.)
- Uses local file system; syncs with Squarespace on deploy

**Setup:**
1. Install `@squarespace/toolbelt` via npm
2. Authenticate with Squarespace
3. Run `squarespace server` in template directory
4. Edit files locally — preview at `localhost:9000`

---

## Extensions Marketplace

**Access:** Admin → Extensions

Third-party apps built by Squarespace partners. Categories include:

| Category | Examples |
|---|---|
| Shipping & Fulfillment | ShipStation, EasyPost, Shippo |
| Accounting | QuickBooks, FreshBooks, Xero |
| Inventory | DEAR Inventory, Brightpearl |
| Marketing | Privy, Klaviyo |
| Customer Support | Gorgias, Zendesk |
| Reviews | Yotpo, Okendo |

Extensions connect via OAuth and use the Commerce API internally.

**Building an extension:** Register as a Squarespace Developer, implement OAuth flow, submit for review via the developer portal.

---

## Third-Party Integrations

### Built-in (no setup required)
| Service | Integration type |
|---|---|
| Google Analytics (GA4) | Paste Measurement ID in Advanced → External Services |
| Google Search Console | Connect via Marketing → SEO |
| Google Shopping | Product catalog sync |
| Zapier | Trigger workflows from form submissions, orders |
| Mailchimp | Mailing list sync |

### Commerce & Payments
| Service | Notes |
|---|---|
| Stripe | Payment processor |
| PayPal | Payment processor |
| Square | In-person POS |
| Afterpay / Clearpay | BNPL at checkout |
| Klarna | Installments at checkout |
| Printful | Print-on-demand product fulfillment |
| TaxJar | Advanced sales tax compliance |
| Xero | Accounting sync |

### Scheduling
| Service | Notes |
|---|---|
| Google Meet | Auto-generate meeting links in Acuity |
| Zoom | Auto-generate meeting links in Acuity |
| GoToMeeting | Auto-generate meeting links in Acuity |
| Google Calendar | Two-way calendar sync in Acuity |

### Social Commerce
| Service | Notes |
|---|---|
| Instagram Shopping | Product catalog tag products in posts |
| Facebook Shop | Product catalog via Facebook Commerce Manager |
| Pinterest | Product catalog sync |
