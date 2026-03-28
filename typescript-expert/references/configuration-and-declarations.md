# Configuration and Declaration Files
## Chapters 11–13: Declaration Files, IDE Features, Configuration Options

---

## Chapter 11: Declaration Files

### What Are Declaration Files?

Declaration files (`.d.ts`) contain only type information — no runtime code. They describe the types of JavaScript values that exist elsewhere (in `.js` files, compiled output, or third-party packages).

```
source.ts  ──tsc──▶  source.js   (runtime code)
                     source.d.ts (type declarations)
```

### When You Need Declaration Files

- Consuming a JavaScript library with no TypeScript source
- Publishing a TypeScript library (tsc generates `.d.ts` from `.ts` source)
- Augmenting types of existing packages
- Declaring global variables or module shapes

### The declare Keyword

`declare` tells TypeScript "this exists at runtime, but I'm only declaring its type here":

```typescript
// declarations.d.ts
declare const VERSION: string
declare function fetch(url: string): Promise<Response>
declare class EventEmitter {
  on(event: string, listener: Function): this
  emit(event: string, ...args: any[]): boolean
}
```

### Module Declarations

Declare the shape of an entire module:

```typescript
// types/lodash.d.ts
declare module "lodash" {
  export function chunk<T>(array: T[], size: number): T[][]
  export function flatten<T>(array: (T | T[])[]): T[]
}
```

### Wildcard Module Declarations

Declare types for all imports matching a pattern (e.g., for asset imports):

```typescript
declare module "*.svg" {
  const content: string
  export default content
}

declare module "*.css" {
  const styles: Record<string, string>
  export default styles
}
```

### Global Declarations

Add globals to the type system (available without importing):

```typescript
// global.d.ts
declare global {
  interface Window {
    analytics: Analytics
  }

  const __DEV__: boolean
}
export {}  // Make this a module (required for 'declare global' to work)
```

### DefinitelyTyped: @types/

Most popular JavaScript libraries have community-maintained type definitions on DefinitelyTyped, published as `@types/<package>`:

```bash
npm install --save-dev @types/lodash
npm install --save-dev @types/node
npm install --save-dev @types/react
```

TypeScript automatically picks up `@types/` packages from `node_modules`. No import needed.

### typeRoots and types

Control which `@types` packages are included in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "typeRoots": ["./node_modules/@types"],  // where to look for @types
    "types": ["node", "jest"]               // only include these @types
  }
}
```

---

## Chapter 12: Using IDE Features

TypeScript's **Language Service** powers IDE features. These work in VS Code, WebStorm, and any editor using the TypeScript language server.

### Key IDE Features

| Feature | How to Use |
|---------|-----------|
| **Autocomplete** | Type `.` after an object — TypeScript lists valid properties/methods |
| **Go to Definition** | Cmd/Ctrl+Click — navigate to the declaration of a symbol |
| **Find All References** | Right-click → Find References — see all usages |
| **Rename Symbol** | F2 — renames across all files, including declaration files |
| **Quick Fix** | Cmd/Ctrl+. — fix errors: add missing import, implement interface, etc. |
| **Inline Type Hints** | Hover to see inferred types |
| **Error Squiggles** | Red underlines = type errors; yellow = warnings |

### tsconfig.json Discovery

The IDE uses the nearest `tsconfig.json` up the directory tree. For monorepos, each package should have its own `tsconfig.json` with the IDE opened at the package root.

### Organizing Imports

VS Code + TypeScript can auto-organize imports:
- Remove unused imports
- Sort alphabetically
- Add missing imports on paste

### Type Error vs. Syntax Error Display

TypeScript displays type errors in the Problems panel and inline. Syntax errors are reported by both the TypeScript server and the editor's syntax highlighting.

---

## Chapter 13: Configuration Options

### tsconfig.json Structure

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "CommonJS",
    "strict": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "sourceMap": true
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

### Strictness Options

| Option | What It Enables |
|--------|----------------|
| `"strict": true` | Enables all strict flags below |
| `strictNullChecks` | null/undefined are distinct types |
| `noImplicitAny` | Error on variables inferred as `any` |
| `strictFunctionTypes` | Contravariant function parameter checking |
| `strictPropertyInitialization` | Class properties must be initialized |
| `strictBindCallApply` | Stricter bind/call/apply typing |
| `useUnknownInCatchVariables` | catch clause variables are `unknown`, not `any` |
| `noUncheckedIndexedAccess` | Index access returns `T \| undefined` |
| `noImplicitOverride` | Must use `override` keyword when overriding |

### Target and Module Options

**target**: The JavaScript version emitted:

| Value | Use When |
|-------|---------|
| `"ES5"` | Must support old browsers |
| `"ES2015"` (ES6) | Modern browsers, Node 6+ |
| `"ES2020"` | Node 14+, modern browsers |
| `"ESNext"` | Always latest; good for library source |

**module**: The module system in emitted code:

| Value | Use When |
|-------|---------|
| `"CommonJS"` | Node.js applications |
| `"ESNext"` / `"ES2020"` | Bundlers (webpack, Vite, Rollup) |
| `"NodeNext"` | Node.js ESM projects (with `.mts`/`.cts`) |
| `"None"` | Single-file scripts |

### Module Resolution

| Option | Behavior |
|--------|---------|
| `"node"` | Classic Node.js resolution (require) |
| `"bundler"` | For bundler projects — allows extensionless imports |
| `"node16"` / `"nodenext"` | Full Node.js ESM resolution (requires extensions in imports) |

### Output Options

| Option | Effect |
|--------|--------|
| `outDir` | Where to put compiled `.js` files |
| `rootDir` | Root of the source tree (preserves directory structure) |
| `declaration` | Emit `.d.ts` files alongside `.js` |
| `declarationDir` | Separate directory for `.d.ts` files |
| `sourceMap` | Emit `.js.map` source maps for debugging |
| `noEmit` | Type-check only; don't emit any files |
| `noEmitOnError` | Don't emit if type errors exist |

### Path Aliases

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@utils/*": ["src/utils/*"],
      "@components/*": ["src/components/*"]
    }
  }
}
```

Note: `paths` affects TypeScript resolution only. You also need to configure your bundler to resolve these at runtime.

### Project References

For monorepos with interdependent packages:

```json
// packages/core/tsconfig.json
{
  "compilerOptions": { "composite": true },
  "references": []
}

// packages/app/tsconfig.json
{
  "references": [{ "path": "../core" }]
}
```

`tsc --build` (or `tsc -b`) uses project references for incremental compilation.

### Extending tsconfig

```json
{
  "extends": "@tsconfig/node20/tsconfig.json",
  "compilerOptions": {
    "outDir": "./dist"
  }
}
```

Community base configs: `@tsconfig/node20`, `@tsconfig/react-app`, `@tsconfig/strictest`.
