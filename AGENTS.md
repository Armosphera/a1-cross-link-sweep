# AGENTS.md — a1-cross-link-sweep

This file applies to every agent (human or AI) that touches the
`armosphera/a1-cross-link-sweep` repository. It extends, and never weakens, the
global rules in `https://github.com/Armosphera/A1-portfolio/blob/main/LICENSING.md`.

## 1. What this repo is

`a1-cross-link-sweep` is a **one-shot tooling repo** for the SamStep74 →
Armosphera account migration. It:

- Scans all armosphera/* repos for cross-account links (e.g. README referencing `SamStep74/...`)
- Reports a per-repo list of "dirty" links (lines that need to be updated)
- Provides a `sweep` mode that rewrites the links to point at the armosphera mirror
- Used once during the public→private migration (Wave 13, 2026-06-21)

This is **not** a service, **not** a product. It's a development tool that
runs against the A1 portfolio and then gets archived (or kept around for
future similar migrations).

## 2. The 2 protected files

- **`package.json` `"private": true`** — this package is not on npm by design.
- **`sweep.config.json`** — the cross-account patterns (SamStep74/*, A1-*/SamStep74).

These should not be edited without an operator OK. New migration patterns
should be added to `sweep.config.json` (the list of dirty prefixes to scan for).

## 3. Workflow — TDD where applicable

The repo ships with **unit tests** for the cross-link scanner logic:

1. Tests live in `test/sweep.test.js` (or `test/`).
2. New sweep patterns should come with a test fixture.
3. Run `npm test` before opening a PR.

## 4. CLI Usage

```bash
# Scan only (report, don't modify)
node bin/sweep.js --scan

# Apply (modify files in place)
node bin/sweep.js --apply

# Specific repos only
node bin/sweep.js --scan --repos=A1-AI-Core,A1-Localization-AM
```

## 5. Adding a new migration pattern

1. Edit `sweep.config.json` to add the new dirty pattern
2. Add a fixture in `test/fixtures/`
3. Add a test in `test/sweep.test.js`
4. Verify: `node bin/sweep.js --scan` reports expected matches

## 6. No secrets, no customer data

- This repo has no API keys, no customer data, no production secrets.
- It runs against public GitHub URLs only (no auth required for public repos).

## 7. Files, Functions, Nesting

- One concept per file (e.g. `scanner.js`, `rewriter.js`).
- Functions <50 lines, single responsibility.
- No nesting deeper than 4 levels.

## 8. Day-One Checklist

```
1. cat AGENTS.md             # this file
2. cat README.md             # what the tool does
3. cat package.json          # dependencies + scripts
4. cat sweep.config.json     # the dirty patterns
5. npm install && npm test   # confirm baseline green
6. Now you can edit.
```

If `npm test` baseline fails: STOP, file an issue. Do not edit around a
broken baseline.

## 9. Day-One Checklist (after migration)

This repo is **done** (used once for Wave 13). If you find yourself editing
it, ask: should this be a one-shot script in `armosphera/A1-portfolio`
instead? If yes, move it there and archive this repo.

## 10. Ownership

**Armosphera LLC** · contact: ops@a1-suite.local

---

*Adapted from `armosphera/SBOS-A1-ERP/AGENTS.md`. Specializes for "this is a one-shot
tooling repo, not a service." License: MIT (operator's choice for tooling — see LICENSE).*