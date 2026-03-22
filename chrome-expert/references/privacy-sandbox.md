# Privacy Sandbox APIs

Goal: Enable advertising and measurement on the web without third-party cookies or cross-site tracking.
Status: `https://privacysandbox.google.com/`

> **Note:** Privacy Sandbox is actively evolving. Some APIs have been paused or changed direction.
> Always verify current status at the URL above before implementing.

## Topics API

Interest-based advertising without third-party identifiers.

- Browser infers topics from browsing history (e.g., "Sports", "Travel")
- Exposes up to 3 weekly top topics to participating ad tech
- Topics are from a fixed taxonomy (~470 topics)
- User can view and remove topics in `chrome://settings/privacySandbox`

```js
// Check support
if ('browsingTopics' in document) {
  // Request topics (requires Permissions-Policy: browsing-topics=*)
  const topics = await document.browsingTopics();
  // topics: [{ configVersion, modelVersion, taxonomyVersion, topic, version }]
}
```

Requires server to send: `Observe-Browsing-Topics: ?1` response header to record the observation.

---

## Protected Audience (formerly FLEDGE)

On-device remarketing without cross-site tracking.

**Flow:**
1. Advertiser site: browser joins an interest group
2. Publisher site: runs an on-device auction
3. Winning ad renders in a Fenced Frame

```js
// Advertiser — join interest group
await navigator.joinAdInterestGroup({
  name: 'custom-bikes',
  owner: 'https://advertiser.example',
  biddingLogicURL: 'https://advertiser.example/bidding.js',
  trustedBiddingSignalsURL: 'https://advertiser.example/signals',
  ads: [{ renderURL: 'https://cdn.example/ad.html', metadata: { price: 100 } }],
  lifetimeDays: 30,
}, 0.1);  // 0.1 second timeout

// Publisher — run ad auction
const adAuctionResult = await navigator.runAdAuction({
  seller: 'https://ssp.example',
  decisionLogicURL: 'https://ssp.example/scoring.js',
  interestGroupBuyers: ['https://advertiser.example'],
  auctionSignals: { floor: 0.05 },
});

// Render result in a fenced frame
if (adAuctionResult) {
  const ff = document.createElement('fencedframe');
  ff.config = adAuctionResult;
  document.body.appendChild(ff);
}
```

---

## Attribution Reporting API

Measure ad effectiveness (clicks → conversions) without cross-site tracking.

Two report types:
- **Event-level:** Links specific ad click to a conversion (limited data, noisy)
- **Aggregatable:** Rich conversion data processed via aggregation service

```js
// On ad click — register attribution source
// Server sets header: Attribution-Reporting-Register-Source

// HTML anchor with attribution:
// <a href="https://advertiser.example/product"
//    attributionsrc="https://adtech.example/register-source">

// Register conversion trigger (on advertiser site)
// Server sets header: Attribution-Reporting-Register-Trigger

// Reports sent automatically to registered endpoints
```

---

## CHIPS — Partitioned Cookies

Cookies Having Independent Partitioned State. Third-party cookies that are isolated per top-level site.

```http
Set-Cookie: session=abc; SameSite=None; Secure; Partitioned
```

- Cookie is accessible from `https://embed.example` when embedded in `https://site-a.com`
- But NOT accessible when embedded in `https://site-b.com` (different partition)
- Opt-in via `Partitioned` attribute — does not require removal of cross-site cookies

---

## Storage Partitioning

Third-party storage (localStorage, IndexedDB, Cache Storage, BroadcastChannel) is now partitioned by top-level site.

- Storage accessed from `https://embed.example` in `https://site-a.com` is isolated from the same embed in `https://site-b.com`
- Prevents cross-site identity joining via shared storage
- Enabled by default in Chrome 115+

---

## Fenced Frames

`<fencedframe>` — isolated browsing context that prevents cross-site data leakage between the embedder and the embedded content. Used with Protected Audience and Shared Storage.

```html
<fencedframe src="https://example.com/ad.html" mode="opaque-ads"></fencedframe>
```

Key restrictions:
- Cannot communicate with embedder via `postMessage` (unpartitioned)
- Network requests are not associated with top-level site
- Size is preset by the API that generated the frame config

---

## Related Website Sets (formerly First-Party Sets)

Allow a group of related domains to be treated as "same party" for cookie purposes.

- Declared in a JSON file at `/.well-known/related-website-sets.json`
- Stored in a public list maintained by Google
- Enables `requestStorageAccessFor()` without per-site user prompt within the set

---

## Storage Access API

Lets cross-site iframes request access to their unpartitioned (first-party) cookies.

```js
// In an iframe from embed.example
const hasAccess = await document.hasStorageAccess();
if (!hasAccess) {
  // Requires user gesture
  await document.requestStorageAccess();
}
// Now has access to first-party cookies
```

---

## Checking Status

```js
// Check if third-party cookies are blocked
const testKey = '_3pc_test';
document.cookie = `${testKey}=1; SameSite=None; Secure`;
const blocked = !document.cookie.includes(testKey);
```

Privacy Sandbox feature flags: `chrome://flags/#privacy-sandbox-ads-apis`
Settings: `chrome://settings/privacySandbox`
