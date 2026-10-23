# AI Usage & Contribution Policy

The **Zenith** project welcomes the responsible use of AI coding assistants (such as
Claude Code, Antigravity, Cursor, and GitHub Copilot) to augment development. To
preserve template reliability, strict tooling standards, and maintainer time, all
contributors must adhere to the following principles:

## 1. Human-in-the-Loop & Full Accountability

- **Human Ownership**: All AI-assisted code, template files, and documentation must be
  thoroughly understood, reviewed, and edited by a human contributor before submission.
- **Full Accountability**: Contributors accept full responsibility for all changes,
  including template hooks, test coverage, and documentation consistency.

## 2. Verification Gate Before Submitting

- **Mandatory Local Verification**: Before submitting a PR, verify all template tests,
  linting, formatting, and prek checks locally:

  ```bash
  uv run poe test
  uv run poe code-quality
  uv run prek run --all-files
  ```

- **Hermetic Testing**: Never submit untested template Jinja2 modifications or hook
  changes. Always verify that both default and edge-case project renderings succeed
  cleanly.

## 3. No Unattended Bots or PR Floods

- **Automated Agents Restricted**: Unattended bot scripts are strictly forbidden from
  directly opening pull requests or creating automated issue spam.
- **Targeted Contributions**: AI-assisted PRs must address accepted issues or
  coordinated feature requests.
- **Search Before Opening (No Duplicates)**: Before opening a pull request, search open
  and closed pull requests, issues, and discussions. Do not open a pull request when the
  same change has already been proposed or is currently in progress. Submitting
  duplicate pull requests wastes maintainer bandwidth.
- **Contribute at Human Speed, Not AI Speed**: AI tools make it trivial to generate
  large volumes of code and prose quickly, but review bandwidth moves at human speed.
  Do not post rapid-fire pull requests, mass-claim open issues, or flood trackers with
  automated solutions.
- **Do Not Communicate via LLM-Generated Text**: Do not rely on AI assistants to speak
  for you in issues, pull request discussions, or reviews. Maintainers expect direct,
  thoughtful communication written by the contributor, not raw LLM summaries.

## 4. Transparent Disclosure

- **PR Disclosure**: State the AI tools used and the general scope of assistance in the
  pull request description.
- **Commit Attribution**: When AI coding assistants contribute directly to code
  generation or commits, credit them in Git commit messages using standard
  `Co-authored-by` trailers (e.g. `Co-authored-by: Claude <noreply@anthropic.com>`).
- **Protecting Newcomer Issues**: Issues labeled `good first issue` are reserved for
  human contributors learning the codebase.

## 5. Concise Code & Clean Comments

- **Default to Zero Inline Comments Unless Explaining 'Why'**: Comments should default
  to none. Only add inline comments when explaining a non-obvious rationale, hidden
  constraint, workaround, or subtle architectural invariant.
- **No AI Slop or Diff-Narrative Comments**: Any comments added must be concise and
  relevant for the *current* state of the code. Remove any AI-generated comments that
  describe changes relative to the previous state of the code, narrate what the agent
  did or did not do, or restate obvious syntax.
- **Adhere to AGENTS.md**: Respect architectural boundaries, hermetic `uv` usage, and
  tool guidance documented in `.agents/skills/`.
