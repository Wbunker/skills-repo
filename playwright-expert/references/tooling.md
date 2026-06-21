# Tooling — Install, Run, CI

Getting Playwright installed, running tests from the CLI, and wiring it into CI. For interactive
debugging (UI mode, Inspector, codegen) see [debugging.md](debugging.md); for the full config
reference see [test-config.md](test-config.md); for trace post-mortems see
[trace-viewer.md](trace-viewer.md).

## Contents
- [Installing](#installing)
- [Running tests](#running-tests)
- [CI](#ci)
- [Docker](#docker)

## Installing

```bash
npm init playwright@latest          # scaffold (also: yarn create playwright / pnpm create playwright)
npx playwright install --with-deps  # install browsers + OS dependencies
npx playwright install chromium     # install a single browser
npx playwright --version
```

Scaffolding creates `playwright.config.ts`, `tests/example.spec.ts`, and (optionally) a GitHub
Actions workflow. **Node.js 22.x / 24.x / 26.x**; macOS 14+, Windows 11+/Server 2019+, recent
Debian/Ubuntu (incl. Ubuntu 26.04, v1.61+). A VS Code extension can run/record tests without the CLI
— see [debugging.md](debugging.md).

## Running tests

```bash
npx playwright test                         # all tests, headless, all browsers
npx playwright test --ui                    # interactive UI mode (watch, time-travel) — recommended
npx playwright test --headed                # show the browser window
npx playwright test landing-page.spec.ts    # a single file
npx playwright test tests/todo/ tests/landing/   # multiple directories
npx playwright test landing login           # files matching keywords
npx playwright test -g "add a todo item"    # by test title (grep)
npx playwright test -G "@slow"              # invert grep: skip matching titles (v1.61+, = --grep-invert)
npx playwright test --project webkit        # one browser
npx playwright test --project webkit --project firefox
npx playwright test --last-failed           # rerun only previously failed tests
npx playwright test --test-list=list.txt    # run an explicit list of tests from a file (v1.56+; --test-list-invert to skip them)
npx playwright test --trace on              # force a trace for every test (see trace-viewer.md)
npx playwright show-report                  # open the HTML report (auto-opens on failure)
```

Other useful flags: `--workers <n>`, `--repeat-each <n>`, `--retries <n>`, `--shard=1/3`,
`--debug` / `--debug=cli` (see [debugging.md](debugging.md)). Sharding and reporters are covered in
[test-config.md](test-config.md).

## CI

```bash
npx playwright install --with-deps      # in CI, install browsers + deps first
npx playwright test
```

The `npm init playwright@latest` scaffold can generate a ready GitHub Actions workflow. Upload the
`playwright-report/` (and `test-results/`) directories as build artifacts to inspect failures with
traces afterward. For large suites, shard across machines with `--shard` + the `blob` reporter and
`npx playwright merge-reports` — see [test-config.md](test-config.md#sharding).

## Docker

Microsoft publishes an official image with browsers + dependencies preinstalled:

```bash
mcr.microsoft.com/playwright:v1.61.0-noble    # match the tag to your Playwright version
```

Run tests inside it (mount the repo, set `--ipc=host` so Chromium has enough shared memory):
```bash
docker run --rm --ipc=host -v $(pwd):/work -w /work \
  mcr.microsoft.com/playwright:v1.61.0-noble \
  npx playwright test
```

Keep the image tag in lockstep with the `@playwright/test` version, or browser binaries and the
runner can mismatch.
