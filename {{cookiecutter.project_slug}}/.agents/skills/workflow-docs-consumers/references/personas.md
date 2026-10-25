# Persona Archetypes for Documentation Review

Use these persona archetypes to evaluate documentation from diverse developer perspectives.

## 1. The Newcomer Developer

- **Background**: Software engineer with zero prior knowledge of the project.
- **Evaluation Mandate**:
  - Evaluate the elevator pitch on the landing page.
  - Verify that the core project identity is immediately clear.
  - Verify that documentation states prerequisites early.
  - Identify jargon that appears without context.
- **Key Questions**:
  - What is this project at its core?
  - Can I complete the primary tutorial in under five minutes?
  - Where did I pause because an explanation was missing?

## 2. The Junior Developer

- **Background**: Beginner engineer comfortable with basic scripts, now building a first production service.
- **Evaluation Mandate**:
  - Identify scary, overwhelming, or overly academic explanations.
  - Expose common beginner misconceptions (such as virtual environments or package managers).
  - Test the clarity of quality-gate failure messages.
- **Key Questions**:
  - Do I know where to write my code?
  - What do I do when a test or linter gate fails?
  - Does the guide assume advanced architecture knowledge?

## 3. The Opinionated Senior Pythonista

- **Background**: Experienced Python engineer with established preferences (mypy, pyright, pre-commit, make).
- **Evaluation Mandate**:
  - Interrogate architectural trade-offs and tool selections.
  - Identify dogmatic rules that lack engineering justification.
  - Evaluate escape hatches for edge cases and operating system margins.
- **Key Questions**:
  - Why this specific toolstack instead of standard ecosystem tools?
  - Does the coverage rule allow pragmatic exclusions?
  - What are the editor and language server implications?

## 4. The Tech Lead & Engineering Manager

- **Background**: Engineering leader managing delivery velocity, onboarding speed, and maintenance liability.
- **Evaluation Mandate**:
  - Evaluate team-level economics and time-to-first-pull-request.
  - Identify business ROI arguments to defend strictness to leadership.
  - Assess upstream toolchain churn and configuration drift across services.
- **Key Questions**:
  - Will these quality gates accelerate or slow down our sprint commitments?
  - How long does a new hire need to submit their first change?
  - How do we maintain template updates over two years?

## 5. The DevOps & Platform Engineer

- **Background**: Infrastructure engineer responsible for containers, CI pipelines, and cloud deployments.
- **Evaluation Mandate**:
  - Evaluate containerization strategies and image sizes.
  - Verify CI runner cache mechanics and execution durations.
  - Verify supply-chain security and provenance standards.
- **Key Questions**:
  - How do I build a lean multi-stage container image?
  - Are dependency hashes and lockfiles strictly verified?
  - Does CI deploy credential-free through OpenID Connect?

## 6. The Open-Source Library Maintainer

- **Background**: Library author publishing standalone packages to the Python Package Index.
- **Evaluation Mandate**:
  - Verify semantic versioning and breaking API change detection.
  - Verify clean wheel builds without bundled test assets.
  - Ensure documentation supports both applications and lean libraries.
- **Key Questions**:
  - How does the project protect public API contracts?
  - Can I strip command-line interface dependencies for pure libraries?
  - How are release notes and changelogs automated?
