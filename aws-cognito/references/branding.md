# Managed Login Branding

Styling the Cognito-hosted pages ([managed-login.md](managed-login.md)). Two systems, gated by the domain's branding version: the **branding editor** (managed login) and **hosted UI (classic) branding**. You can style **visual** properties only — you **can't change page text** except via [localization](managed-login.md#localization--terms-documents).

## Table of Contents
1. [Style model](#style-model)
2. [Branding editor (managed login)](#branding-editor-managed-login)
3. [Branding via API](#branding-via-api)
4. [Hosted UI (classic) branding](#hosted-ui-classic-branding)
5. [Gotchas](#gotchas)

---

## Style model

- A **style** is the set of visual settings (images, colors, options) applied to **one app client**. Each app client can have a distinct style, but a domain serves **one** branding version, so effectively one branding version per pool.
- New console-created pools default to **Managed login**; older pools default to **Hosted UI (classic)**. Changing the domain's branding version applies immediately.
- **A programmatically-created app client has NO style** — managed login won't render for it until you call `CreateManagedLoginBranding`. Console-created clients get a default style automatically.
- **You can't copy a style or reassign it.** To move a style to a different app client, delete the original and create a new one. To replicate: `DescribeManagedLoginBranding` → edit the JSON → `CreateManagedLoginBranding` on the target.

## Branding editor (managed login)

A no-code visual editor in the console (with live preview). Enter it from **Managed login → Styles → Create a style** (assign to an app client) → **Launch branding editor**. Two setting groups:

- **Foundation** — overall theme, **display mode** (light / dark / **adaptive** to the browser; adaptive lets you set separate colors + logos per mode), spacing, border radius, page background (solid color or image per mode), **form behavior** (alignment, colors, primary branding color, form logo), header/footer, and **Authentication behavior** — including **Domain search input** (prompt for email and route to the matching [SAML IdP identifier](federation.md#idp-routing-identifiers)).
- **Components** — per-element styling: buttons, dividers, dropdowns, **favicon**, focus rings, form container, global header/footer, error/success indications, option controls, inputs, links, page/field text.

**Quick setup** offers the common choices (look-and-feel, background, forms, headers) as a guided flow.

## Branding via API

`CreateManagedLoginBranding` / `UpdateManagedLoginBranding` / `DescribeManagedLoginBranding(ByClient)` / `DeleteManagedLoginBranding`. Settings are a JSON `Document`; images go in an `Assets` array as **base64-encoded binary**.

Workflow to script a style:
1. Create a default style in the console and assign it to an app client.
2. `DescribeManagedLoginBrandingByClient` with `ReturnMergedResources: true`.
3. Strip the top-level `ManagedLoginBranding` wrapper; edit `Settings`; replace image `Bytes` with base64.
4. Send via `Create`/`UpdateManagedLoginBranding`. **PATCH semantics** — unspecified settings are left unchanged, so partial requests are safe.

**2 MB request limit.** If assets push a request over 2 MB, split into multiple `UpdateManagedLoginBranding` calls (partial updates don't reset omitted params). Cognito ignores `Settings` keys not in the schema it returned.

**Asset file types:**

| Asset | Extensions |
|---|---|
| `FAVICON_ICO` | ico |
| `FAVICON_SVG` | svg |
| `IDP_BUTTON_ICON` | ico, svg |
| logos / backgrounds / graphics (`PAGE_*`, `FORM_*`, `*_GRAPHIC`) | png, svg, jpeg |

SVG uploads are **sanitized** to an allowlist of SVG attributes/elements (no arbitrary scripting).

## Hosted UI (classic) branding

The first-generation option: a **logo image** + a **fixed-key CSS file**, set with `SetUICustomization` / `GetUICustomization` (CLI `set-ui-customization` / `get-ui-customization`). Requires a domain.

- **Scope:** a pool-wide default plus optional **per-app-client override** (`--client-id`). Clients without their own settings inherit the default.
- **Logo:** PNG/JPG/JPEG scaled to **350×178 px**, **≤ 100 KB** (≈130 KB base64), centered above the inputs.
- **Total request ≤ 135 KB** (headers + base64 logo + CSS). Keep logo ≤ 100 KB and **CSS ≤ 3 KB**, or you get `request parameters too large`. **You can't set CSS and logo separately** — one request carries both.
- **CSS is limited to a fixed set of class names** (download the **CSS template**; keys outside it are ignored). The ~19 customizable classes include `background-customizable`, `banner-customizable`, `submitButton-customizable(:hover)`, `idpButton-customizable(:hover)`, `socialButton-customizable`, `inputField-customizable(:focus)`, `label-customizable`, `logo-customizable`, `errorMessage-customizable`, `legalText-customizable`, `passwordCheck-valid/-notValid-customizable`, etc.
- Property values **can't** use `@import`, `@media`, `@supports`, `@page`, or JavaScript.

```bash
aws cognito-idp set-ui-customization \
  --user-pool-id "$POOL_ID" --client-id "$CLIENT_ID" \
  --image-file fileb://logo.png \
  --css '.submitButton-customizable{background-color:#0b5;} .logo-customizable{max-width:80%;}'
```

## Gotchas

- **A domain is required** before any branding takes effect.
- **Text isn't customizable** — only visuals + localization.
- Style changes can take **up to ~1 minute** to appear; refresh after a moment.
- Managed login and hosted UI branding are **separate systems**; switching the domain's branding version logs users out and doesn't carry styles over.
