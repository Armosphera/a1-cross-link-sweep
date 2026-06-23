# a1-cross-link-sweep

Standalone implementation of the **A1 cross-account link sweep** — a Karpathy-pattern
"keep-or-revert" autoresearch loop that maintains `examples/*/program.md` files in
[`Armosphera/autoresearch-sboss`](https://github.com/Armosphera/autoresearch-sboss)
pointing at the right source repo.

Originally lived inside `autoresearch-sboss/examples/cross-link-sweep/`; extracted
into its own repo on 2026-06-21 for reusability — the same loop can target any
multi-file "follow the canonical ref" problem.

## Quick start

\`\`\`bash
# Install: clone + add to PATH
git clone https://github.com/Armosphera/a1-cross-link-sweep.git
export PATH="$PWD/a1-cross-link-sweep:$PATH"

# Run as a one-shot
a1-clx eval           # print current score (expect 22 / 22)
a1-clx verify         # list any dirty files (no commits)
a1-clx sweep          # commit any drift back to canonical refs
\`\`\`

## Files in this repo

| File | Role | Mutable? |
|---|---|---|
| \`a1-clx\` | Standalone CLI entry-point | yes |
| \`program.md\` | Research charter (Karpathy-style "what the agent does") | yes |
| \`workflow.py\` | Agent-editable strategy (sweep via GitHub Contents API) | yes |
| \`eval.py\` | Fixed judge (compute score 0-22) | **NO** — do not modify |
| \`eval_set.json\` | Fixed corpus: 22 entries with \`expected_source_repo\` | **NO** |
| \`results.tsv\` | Append-only ledger of iterations | append-only |

## The loop

\`\`\`
1. Read results.tsv — find current best score.
2. Read workflow.py — understand current strategy.
3. Edit workflow.py: pick next file, run GitHub Contents API replacement, verify.
4. Run eval.py — get new score.
5. If new > best: commit workflow.py + the new program.md, append 'keep' to results.tsv.
   If new ≤ best: revert, append 'revert' to results.tsv.
\`\`\`

Default time budget: 60 s per iteration (\`CROSS_LINK_BUDGET_S\` env, capped at 600 s).
The GitHub Contents API is rate-limited at 5000 req/h — keep batches ≤ 100 per run.

## The eval contract

22 \`examples/<name>/program.md\` files in \`autoresearch-sboss\` are checked:

| Bucket | Count | Source repo expected | Pass criterion |
|---|---|---|---|
| AI-Core | 7 | \`Armosphera/A1-AI-Core\` | has \`Armosphera/A1-AI-Core\` ref AND no \`SamStep74\` ref |
| Localization AM | 8 | \`Armosphera/A1-Localization-AM\` | no \`SamStep74\` ref at all |
| Localization RU | 7 | \`Armosphera/A1-Localization-RU\` | no \`SamStep74\` ref at all |

Max score: 22 / 22.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | All clean (22 / 22) |
| 1 | Drift detected — run \`a1-clx sweep\` to fix |
| 2 | Runtime error (missing token, network, etc.) |

## Integration

Wired into [\`Armosphera/A1-portfolio/scripts/health.sh\`](https://github.com/Armosphera/A1-portfolio/blob/main/scripts/health.sh) as check #3. The portfolio health check runs weekly via GitHub Actions and opens an issue on drift.

## History

- **2026-06-20**: First version inside \`autoresearch-sboss/examples/cross-link-sweep/\`. Baseline score 15/22, swept to 22/22 in 1 keep-or-revert iteration.
- **2026-06-21**: Extracted to standalone repo. CLI wrapper added.

## License

Copyright © 2026 Armosphera LLC. All rights reserved. See [\`LICENSE\`](./LICENSE).

## Related

- [\`karpathy/autoresearch\`](https://github.com/karpathy/autoresearch) — the original keep-or-revert loop pattern.
- [\`Armosphera/autoresearch-sboss\`](https://github.com/Armosphera/autoresearch-sboss) — the SBOSS workflows this loop maintains.
- [\`Armosphera/A1-portfolio\`](https://github.com/Armosphera/A1-portfolio) — portfolio-level docs + the health-check that depends on this loop.


## Relationship to `autoresearch-sboss/examples/cross-link-sweep/`

This standalone repo (a1-cross-link-sweep) and the original
`Armosphera/autoresearch-sboss/examples/cross-link-sweep/` directory look
similar but serve **different consumers**:

| Aspect | `a1-cross-link-sweep` (this repo) | `autoresearch-sboss/examples/cross-link-sweep/` |
|---|---|---|
| Purpose | Standalone CLI for ad-hoc sweeps by a developer | CI gate (Karpathy loop) integrated with autoresearch-sboss CI |
| Entry point | `a1-clx` shell script | Direct invocation of `workflow.py` |
| Consumers | Manual: `a1-clx verify` / `a1-clx sweep` | CI workflow + orchestration tools |
| Tolerates empty env vars | Yes (falls back to `gh` CLI) | No — CI sets them explicitly |
| Mutable | `a1-clx`, `program.md`, `workflow.py` | `workflow.py`, `program.md` only |

**They are not duplicates.** This repo is the developer-facing CLI; the
other is the autoresearch-pattern reference implementation. The `workflow.py`
and `eval.py` files are kept in sync manually (last sync: 2026-06-22).

**When to use which**:
- Running the sweep yourself → `a1-clx verify` (this repo)
- Adding a new Karpathy eval pattern to autoresearch-sboss → copy from
  `examples/cross-link-sweep/` and modify
- Production CI gate → use the autoresearch-sboss workflow
