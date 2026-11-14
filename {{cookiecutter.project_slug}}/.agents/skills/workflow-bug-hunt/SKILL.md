---
name: workflow-bug-hunt
description: >-
  Runs an autonomous multi-agent bug hunting and security audit pipeline using parallel scouts, worktree reproduction, and independent arbiters.
  Runs only when explicitly requested.
  Triggers: bug hunt, audit codebase, find vulnerabilities, bug hunting, security audit, swarm audit, arbiter.
disable-model-invocation: true
version: 1.2.0
---

# Multi-Agent Bug Hunt (`workflow-bug-hunt`)

This skill defines a multi-agent bug hunting and security audit pipeline for codebases from 10k to 1M lines.
It coordinates risk-tiered scouting, worktree reproduction, sharded arbiter review, and branch patching.

---

## 1. Core Principles & Invariants

1. **Disjoint Slice Ownership**: Assign each scout a unique slice ID (`S01`, `S02`) for reporting. Allow 1-hop caller and callee reads across modules.
2. **Evidence-Only Reporting**: Reject every finding that lacks a concrete trigger input or failing test.
3. **Arbiter Independence**: Separate discovery from validation. Independent arbiters verify that each reproducer triggers the claimed root cause.
4. **Rolling Worktree Pool**: Run experimentation, reproduction, and patching in Git worktrees under `.temp/worktrees/`. Cap active worktrees at 4 and remove completed worktrees immediately.
5. **Shared Environment**: Pin `PYTHONPATH="$PWD/src"` and `UV_PROJECT_ENVIRONMENT="<root>/.venv"` with `--no-sync`. This avoids `.venv` rebuilds and shadowed imports.
6. **Persistent State Ledger**: Track slice status in `.temp/bug-hunt/scope.md`, findings in `.temp/bug-hunt/findings/`, and reproducers in `.temp/bug-hunt/repro/`. Never run `uv run poe clean` during an active hunt.
7. **Human Review Gate**: Present triaged findings and branch diffs for human approval before merging fixes.

---

## 2. Agent Roles

This workflow coordinates five specialized roles.
Read [references/agent_roles.md](./references/agent_roles.md) for isolation modes, budgets, and handoff contracts.

- **Coordinator**: Ranks risk tiers, maintains `.temp/bug-hunt/scope.md`, indexes findings with `rg`, and compiles `.temp/bug-hunt/summary.md`.
- **Scout Swarm**: Parallel read-only agents that scan assigned slices with 1-hop contract reads.
- **Triage & Repro Agents**: Reproduce bugs inside clustered worktrees and save verified tests to `.temp/bug-hunt/repro/`.
- **Arbiter**: Independent judge (sharded at 8 findings per agent) that verifies root causes, scans sibling variants, and issues verdicts.
- **Patcher**: Writes minimal fixes and typed regression tests inside branch worktrees when the user requests fixes.

---

## 3. Standard 5-Stage Pipeline

### Stage 1: Reconnaissance, Tiering & Wave Budgeting

1. Run `git status` to verify a clean working tree and create `.temp/bug-hunt/{findings,repro}`.
2. If `.temp/bug-hunt/scope.md` exists, resume from the first incomplete slice instead of remapping.
3. Map entrypoints and module boundaries from `pyproject.toml` and `tach.toml`.
4. Rank modules by sink density (`rg -c` on process, file, parser, and network APIs) and 90-day churn (`git log --since="90 days ago" --name-only`).
5. Partition modules into disjoint slices (`S01`, `S02`) of at most 15 files or 4,000 lines in `.temp/bug-hunt/scope.md` with status `PENDING`.
6. Group slices into `Tier 1` (boundaries and dense sinks), `Tier 2` (core logic), and `Tier 3` (helpers).
7. Budget at most 3 waves (15 slices) per run starting from `Tier 1`.

### Stage 2: Scout Swarm (Parallel Discovery)

1. Start 3 to 5 read-only scouts per wave for `PENDING` slices.
2. Allow each scout to read 1-hop callers and callees outside its slice to audit cross-module contracts.
3. Cap each scout at 5 findings written to `.temp/bug-hunt/findings/BH-<slice>-<nn>.md` using [templates/finding_report.md](./templates/finding_report.md).
4. Mark completed slices as `SCOUTED` in `.temp/bug-hunt/scope.md`.

### Stage 3: Clustered Worktree Triage & Reproduction

1. Index candidate headers without reading full files into context:

```bash
rg "^- \*\*(Location|Bug Class|Status|Verdict)\*\*:" .temp/bug-hunt/findings/
```

2. Deduplicate candidates by `(Location, Bug Class)` and group up to 4 candidates per triage cluster.
3. Create a detached Git worktree per active cluster (`git worktree add --detach .temp/worktrees/repro-<cluster>` or `workspace: "share"`), keeping at most 4 active worktrees.
4. Experiment inside the worktree and save each minimal failing `pytest` test to `<root>/.temp/bug-hunt/repro/test_bh_<slice>_<nn>.py`.
5. Run each reproducer inside the worktree without coverage thresholds against the root environment:

```bash
PYTHONPATH="$PWD/src" UV_PROJECT_ENVIRONMENT="<root>/.venv" uv run --no-sync pytest --no-cov <root>/.temp/bug-hunt/repro/test_bh_<slice>_<nn>.py
```

6. Stop after 3 failed attempts per candidate and update status (`CONFIRMED`, `UNREPRODUCED`, or `FALSE_POSITIVE`).
7. Remove `.temp/worktrees/repro-<cluster>` immediately and mark slices `TRIAGED`.

### Stage 4: Sharded Arbiter Review & Variant Scan

1. Group `CONFIRMED` findings by subsystem into shards of at most 8 findings per independent arbiter agent.
2. Evaluate each shard against [references/arbiter_rubric.md](./references/arbiter_rubric.md) and re-run its reproducers in batch with `pytest --no-cov`.
3. Scan source roots with `rg -n` for sibling occurrences of each verified root cause and record them under `Sibling Variants`.
4. Merge duplicate root causes, assign severity, and issue `ACCEPT`, `REJECT`, or `NEEDS_MORE_EVIDENCE` (at most 1 retry round).
5. Mark slices `ARBITRATED`, write `.temp/bug-hunt/summary.md`, and pause for human review.

### Stage 5: Worktree Patching & Merge Gate (Optional)

Run this stage only when the user requests fixes, or after user approval of `.temp/bug-hunt/summary.md`.

1. Create at most 4 concurrent branch worktrees (`git worktree add -b fix/bh-<id> .temp/worktrees/patch-<id>` or `workspace: "share"`) per disjoint cluster.
2. Apply the minimal fix and in-slice sibling fixes inside the patch worktree.
3. Add a typed regression test (`from __future__ import annotations`, `-> None`, `Bug / Root cause / Fix` docstring) in `tests/test_<module>.py`.
4. Run file-scoped verification inside the patch worktree:

```bash
PYTHONPATH="$PWD/src" UV_PROJECT_ENVIRONMENT="<root>/.venv" uv run --no-sync pytest --no-cov <root>/.temp/bug-hunt/repro/test_bh_<id>.py tests/test_<module>.py
UV_PROJECT_ENVIRONMENT="<root>/.venv" uv run --no-sync ruff check <modified_files>
UV_PROJECT_ENVIRONMENT="<root>/.venv" uv run --no-sync pyrefly check <modified_files>
```

5. Commit verified changes to `fix/bh-<id>`, remove `.temp/worktrees/patch-<id>` immediately, and present `git diff HEAD...fix/bh-<id>` for approval.

---

## 4. Landing & Cleanup

After human approval, merge approved branches sequentially and run the full repository quality gate once in the main tree:

```bash
git merge --no-ff fix/bh-<id>
git branch -d fix/bh-<id>
git worktree prune
rm -rf .temp/worktrees
uv run poe test
uv run poe code-quality
```

Remove `.temp/bug-hunt` only when all planned waves in `.temp/bug-hunt/scope.md` are complete.
