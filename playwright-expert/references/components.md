# Component Testing (Experimental)

Playwright can mount and test UI components in a real browser via `@playwright/experimental-ct-*` packages. **This feature is experimental** — the API may change and is not covered by semver stability guarantees.

## Contents
- [Status & supported frameworks](#status--supported-frameworks)
- [Install](#install)
- [Generated files](#generated-files)
- [Writing a component test](#writing-a-component-test)
- [Props](#props)
- [Events & callbacks](#events--callbacks)
- [Children / slots](#children--slots)
- [Update & unmount](#update--unmount)
- [Hooks (beforeMount / afterMount)](#hooks-beforemount--aftermount)
- [Network mocking](#network-mocking)
- [How it works](#how-it-works)
- [Caveats & limitations](#caveats--limitations)

## Status & supported frameworks
Experimental. Packages are prefixed `@playwright/experimental-ct-`:
- `@playwright/experimental-ct-react`
- `@playwright/experimental-ct-vue`
- `@playwright/experimental-ct-solid`

Note: `@playwright/experimental-ct-svelte` was **REMOVED in v1.59** — use Svelte's own component testing (`vitest-browser-svelte`) instead.

## Install
```
npm init playwright@latest -- --ct
```
Equivalents: `yarn create playwright --ct`, `pnpm create playwright --ct`.

This scaffolds a `playwright-ct.config.ts` and a `playwright/` folder.

## Generated files

**`playwright-ct.config.ts`** — test config for component tests (see [test-config.md](test-config.md)). Uses Vite to bundle and serve components.

**`playwright/index.html`** — facade page. Must contain an element with `id="root"` (mount target) and link the init script.
```html
<html lang="en">
  <body>
    <div id="root"></div>
    <script type="module" src="./index.ts"></script>
  </body>
</html>
```

**`playwright/index.ts`** — runtime init code applied before each component renders (themes, global CSS, providers via hooks).
```typescript
// Apply theme here, add anything your component needs at runtime here.
```

## Writing a component test
Import `test`/`expect` from the framework-specific package. The `mount` fixture renders the component and returns a [Locator](locators.md) pointing at it, usable with all standard [assertions](assertions.md) and actions.

**React**
```typescript
import { test, expect } from '@playwright/experimental-ct-react';
import App from './App';

test('should work', async ({ mount }) => {
  const component = await mount(<App />);
  await expect(component).toContainText('Learn React');
});
```

**Vue**
```typescript
import { test, expect } from '@playwright/experimental-ct-vue';
import App from './App.vue';

test('should work', async ({ mount }) => {
  const component = await mount(App);
  await expect(component).toContainText('Learn Vue');
});
```

Interact with the returned locator like any element:
```typescript
const component = await mount(<App />);
await component.getByRole('button').click();
await expect(component).toContainText('clicked');
```

## Props
**React** — pass as JSX props:
```typescript
test('props', async ({ mount }) => {
  const component = await mount(<Component msg="greetings" />);
});
```

**Vue** — pass via `props`:
```typescript
test('props', async ({ mount }) => {
  const component = await mount(Component, { props: { msg: 'greetings' } });
});
```

## Events & callbacks
**React** — pass callbacks as props:
```typescript
test('callback', async ({ mount }) => {
  const component = await mount(<Component onClick={() => {}} />);
});
```

**Vue** — pass handlers via `on`:
```typescript
test('event', async ({ mount }) => {
  const component = await mount(Component, { on: { click() {} } });
});
```

Callbacks run in Node.js. To assert a callback fired, mutate a closure variable and check it after the interaction (callbacks cannot synchronously return values to the browser — see limitations).

## Children / slots

**React** — pass as JSX children:
```typescript
const component = await mount(<Component>Child</Component>);
```

**Vue** — pass via `slots`:
```typescript
const component = await mount(Component, { slots: { default: 'Slot content' } });
```

## Update & unmount

Re-render with new props/events/slots, or tear down:
```typescript
// React
await component.update(<Component msg="greetings" onClick={() => {}}>Child</Component>);
// Vue
await component.update({ props: { msg: 'greetings' }, on: { click() {} }, slots: { default: 'Child' } });

await component.unmount();
```

## Hooks (beforeMount / afterMount)
Wrap every mounted component with providers/routers via hooks registered in `playwright/index.ts`. `beforeMount` can return a wrapped element; `hooksConfig` is passed per-mount and typed by a shared `HooksConfig`.

**React** (`playwright/index.ts`)
```typescript
import { beforeMount } from '@playwright/experimental-ct-react/hooks';
import { BrowserRouter } from 'react-router-dom';

export type HooksConfig = {
  enableRouting?: boolean;
}

beforeMount<HooksConfig>(async ({ App, hooksConfig }) => {
  if (hooksConfig?.enableRouting)
    return <BrowserRouter><App /></BrowserRouter>;
});
```

In the test:
```typescript
const component = await mount<HooksConfig>(<ProductsPage />, {
  hooksConfig: { enableRouting: true },
});
```

**Vue** (`playwright/index.ts`)
```typescript
import { beforeMount } from '@playwright/experimental-ct-vue/hooks';
import { router } from '../src/router';

export type HooksConfig = {
  enableRouting?: boolean;
}

beforeMount<HooksConfig>(async ({ app, hooksConfig }) => {
  if (hooksConfig?.enableRouting)
    app.use(router);
});
```

## Network mocking

Page-level [`page.route`](network.md) works, plus an experimental `router` fixture that integrates
MSW handlers:

```typescript
import { http, HttpResponse } from 'msw';

test('mocked data', async ({ mount, router }) => {
  await router.use(http.get('/data', async () => HttpResponse.json({ value: 'mocked' })));
  const component = await mount(<DataWidget />);
  await expect(component).toContainText('mocked');
});
```

## How it works
Playwright collects the components referenced by the tests, compiles a bundle with **Vite**, and serves it from a local static web server. On `mount`, Playwright navigates the browser to the facade page `/playwright/index.html` and tells it to render the component. The component runs in a **real browser** while the test code runs in **Node.js** — giving genuine layout, styling, and event behavior plus full Node testing capabilities. See [fixtures.md](fixtures.md) for how `mount` is provided.

## Caveats & limitations
- **Experimental** API; surface may change between releases.
- **Real browser, real render** — CSS, layout, and browser events behave authentically (unlike jsdom).
- **No complex live objects as props.** Only plain JavaScript objects and built-in types (strings, numbers, dates, etc.) cross the Node↔browser boundary.
- **Callbacks cannot return data synchronously** to the component, because a callback executing in the browser cannot synchronously pull a value back from Node.js.
- Components are bundled by Vite; non-trivial build setups (aliases, env, transforms) must be reflected in `playwright-ct.config.ts`.
- Svelte support was removed in v1.59.
