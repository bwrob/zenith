---
name: asd-ste100
description: >-
  Use when text must be parsed without human review.
  Applies to tool descriptions, error messages, inter-agent instructions, system prompts, and status reports.
  Triggers: disambiguate, STE100 rewrite, apply Simplified Technical English, plain-language rewrite, controlled-language rewrite, rewrite so an agent cannot misread this.
  Not for creative or marketing copy.
version: 0.4.0
---

# Simplified Technical English (ASD-STE100)

> [!NOTE]
> **Attribution**: Based on the [`asd-ste100-skill`](https://github.com/danyuchn/asd-ste100-skill)
> created by [Dustin Yuchen Teng](https://github.com/danyuchn), licensed under the MIT License.
> Adapted and extended for Zenith with modular architecture, GFM blockquote alerts,
> Zensical admonitions, reflowed Markdown support, and inline suppressions.

ASD-STE100 is a controlled-language standard created by the aerospace and defense industry (ASD).
It prevents maintenance technicians from misreading English instructions.
The standard removes two major sources of errors: words with multiple meanings
and ambiguous sentence structures.

This skill applies that same discipline for a different reader: an **AI agent or downstream system**.
The agent must parse text without human intervention to resolve ambiguity.
If a technician can misread "close the valve" as an adjective, so can a language model.

## When to Use This Skill

- An agent's output (explanation, instruction, log message, tool description) reads as dense, jargon-heavy, or ambiguous.
- Text will be consumed by another agent, a translation pipeline, or a non-native English reader, and misparsing has a real cost.
- You are writing a prompt, system message, or tool description and want to remove ambiguity before a model ever sees it.
- You want a **before/after** comparison showing which rule the source violated and how the rewrite fixes it. Ask for it — the default output is the rewritten text alone (see Output Format).

This skill is not for creative or marketing copy — STE is deliberately flat and literal. Do not apply it to text where voice, nuance, or persuasion is the point.

## Two Modes

Pick a mode before rewriting. If the user does not say which, infer from the text type and state the choice in one line.

**Strict** — procedures, error messages, tool and function descriptions, inter-agent instructions, safety text. Anywhere a wrong reading has a cost. Apply every rule below, including the hard length caps and one-word-one-meaning discipline.

**STE-flavored** — READMEs, PR descriptions, changelogs, explanatory prose.
Apply structural rules in full and treat lexical rules as advisory.
Keep sentence length caps, active voice, and simple tenses.
Do not use phrasal verbs, semicolons, nominalizations, or marketing adjectives.
Allow natural synonyms so prose does not sound rigid.

The two modes and the structural/lexical split are the same distinction seen from two directions. The split says which rules this skill can verify without ASD's dictionary. The modes say which of them to enforce for a given kind of text.

## Source and Scope

This skill encodes the rule categories of ASD-STE100 Issue 9 (Jan 2025).
The standard contains 53 writing rules across 9 sections covering word choice,
grammar, sentence structure, and style.
It includes a base dictionary of approved words and words to avoid.
See [references/writing-rules.md](./references/writing-rules.md) for details.

It does **not** reproduce ASD's approved dictionary verbatim.
ASD-STE100 is free to download, but it is not free to redistribute.
ASD prohibits unauthorized publication or reproduction.
Therefore, the dictionary remains out of this repository.

Instead, this skill applies the core principle: pick the plainest common word
and use it consistently.
When exact approved wording matters, inspect the standard against the official dictionary.
Request the specification from the [official downloads page](https://www.asd-ste100.org/STE_downloads.html).

## Core Rewrite Rules

STE's rules divide into two kinds, and this skill can only fully deliver one of them. **Structural rules** are self-contained: they describe sentence shape, and you can apply them from the description alone. The official ~900-word dictionary defines **lexical rules** entirely. This skill deliberately does not reproduce that dictionary (see Source and Scope). Without that dictionary, the lexical rules degrade from a checkable standard into a preference for plain words.

Apply the structural rules with confidence. Apply the lexical rules as a direction of travel, and say so in your output rather than implying dictionary compliance you cannot verify.

### Structural rules — apply these

<!-- ste-lint-disable -->
| Rule | Do | Don't |
|---|---|---|
| Active voice | "The agent deletes the file." | "The file is deleted (by the agent)." — unless the actor is genuinely unknown or irrelevant |
| No phrasal verbs (Rule 9.3) | "Remove the panel." / "Start the job." | "Take off the panel." / "Spin up the job." — a two-word verb has meanings the parts do not predict |
| One instruction per sentence | "Open the file. Read line 3." | "Open the file and read line 3, then check if it matches." |
| Sentence length | ≤20 words for instructions/procedures, ≤25 words for descriptions | Long compound/subordinate-clause sentences |
| No semicolons (Rule 8.1) | Split into separate sentences | Any semicolon at all — STE bans the mark outright, not only as a clause join. (Rule 8.1 permits every other standard punctuation mark. The em dash is *not* banned by STE, though it often signals a sentence that should be split.) |
| Noun clusters | ≤3 words stacked as a noun phrase ("fuel pump valve") | 4+ word noun stacks ("high pressure fuel pump inlet valve assembly") |
| No ellipsis | Keep the subject, verb, and article explicit even if it reads longer | Drop words to save space ("Files not backed up will be lost" → ambiguous which files) |
| Keep modality | "The request **may have** failed." stays "may have" | Promote a hedge to a fact ("The request failed.") or invent a certainty the source did not state |
| Paragraph limits | One topic per paragraph, ≤6 sentences | Multi-topic paragraphs |
| Lists for sequences | Use a numbered or bulleted list for 3+ steps or conditions | Bury a sequence inside one prose sentence |
<!-- ste-lint-enable -->

### Lexical rules — direction of travel only

<!-- ste-lint-disable -->
| Rule | Do | Don't | Why it is weaker here |
|---|---|---|---|
| One word, one meaning | Pick one verb for one action and reuse it every time (e.g. always "check", never mix "check"/"verify"/"confirm" for the same action) | Rotate synonyms for the same idea across a document | Consistency within a document is checkable. Which word is the *approved* one is not, without the dictionary. |
| One part of speech per word | "Apply oil to the valve" (oil = noun) | "Oil the valve" (oil = verb) | Whether "oil" is approved as a noun only is a dictionary fact. Prefer the noun form when both read equally well. Do not claim compliance. |
| Verb, not noun (Rule 3.7) | "Analyze the log." | "Perform an analysis of the log." — a noun form of an action makes the sentence longer and hides who acts | Rule 3.7 says "use an **approved** verb to describe an action." Preferring the verb form is safe to apply anywhere. Knowing which verb is the approved one needs the dictionary. |
| Domain terms | Keep necessary technical nouns/verbs, but define them once if not common English (STE allows a project-specific glossary beyond its base dictionary) | Use jargon without ever defining it | The glossary allowance is real STE, but the base dictionary it extends is absent. |
<!-- ste-lint-enable -->

### Simple tenses — apply with one exception
<!-- ste-lint-disable -->
STE permits infinitive, imperative, simple present, simple past, simple future, and past participle as adjective. It excludes present perfect and other compound forms: "we received the report", not "we have received the report".

Aircraft manuals rarely need present perfect tenses.
Other text types sometimes need compound forms to show current relevance.
"The job has completed" and "the job completed" make different statements.
Where the compound form carries unique information or hedges, keep it and flag the departure.
<!-- ste-lint-enable -->
Elsewhere, follow the simple tense rule.

## Scan Checklist

These six habits cover most of what makes machine-written English hard to parse. Each one is mechanical: you can point at the exact word or punctuation mark that breaks the rule, with no judgment call. Scan for all six before you rewrite anything.

1. **Synonym rotation** — the same thing gets several names in one document ("the user", "the customer", "the client"). The reader cannot tell whether they are one thing or three. Fix: pick one name, use it every time.
2. **Hedge stacking** — helper verbs and qualifiers pile up until the sentence asserts nothing. Fix: state the claim, or delete it.
3. **Nominalization** — an action frozen into a noun (such as `"perform an analysis of"` or `"provides assistance to"`). Fix: use the verb (`"analyze"`, `"helps"`).
4. **Marketing adjectives** — words that claim quality instead of showing it: `"seamless"`, `"robust"`, `"powerful"`, `"cutting-edge"`, `"effortless"`, `"blazing-fast"`. Fix: delete, or replace with the measurement that earns the claim.
5. **Run-on sentences** — several ideas joined by semicolons or em dashes. Fix: one idea per sentence.
6. **Soft phrasal verbs** — `"spin up"`, `"reach out"`, `"dive into"`, `"kick off"`. Fix: use the single plain verb (`"start"`, `"contact"`, `"read"`, `"begin"`).

## Process

1. Pick the mode (Strict or STE-flavored). Say which only when the user asked for the rule table — see Output Format.
2. Read the input text once for meaning — do not start rewriting before you understand what it must still say afterward.
3. Inspect the text sentence by sentence.
   Flag every rule violation from the Core Rewrite Rules and Scan Checklist.
   In STE-flavored mode, flag lexical rules as advisory.
   Run `scripts/ste-lint.py` for automated checks of structural rules.
   The linter checks sentence lengths, semicolons, phrasal verbs, nominalizations, and marketing adjectives.
   It also checks synonym rotation, dangling list conjunctions, and compound tenses.
   Use `--baseline N` to tolerate existing violations. Use `--disable` to silence named rules.
4. Rewrite each flagged sentence to fix the violation while preserving the original meaning exactly. A rewrite might drop necessary precision, such as safety conditions or numbers. In this case, keep the longer phrasing and flag it.
   - **Check modality before you commit to a rewrite.** Hedges ("may", "could", "sometimes", "is likely to") carry the author's confidence, and confidence is content. A shorter sentence that upgrades a hedge to a fact is not a simplification — it is a different claim. This is the most common way a well-intentioned STE rewrite goes wrong, because hedges are exactly what a length cap tempts you to cut.
   - Never add a fact the source did not state. A rewrite that reads better because it supplies a cause, a frequency, or a mechanism is no longer a rewrite.
5. Output the rewritten text (see Output Format). Keep the mode choice and the rule analysis internal unless the user asked to see them.
6. If the input already complies, say so — do not force changes onto compliant text.

## Output Format

**Default: the rewritten text, and nothing else.** Most callers want a result they can paste straight into a tool description, an error string, or a prompt. Print the simplified text on its own. Do not add a preamble, mode announcement, violation count, or change summary. Do not add a rule table or a closing offer to explain further.

You may add one line after the text if step 4 kept a longer phrasing on purpose. Prefix this line with `Kept as-is:`. Name the phrase and the precision that you would lose. Omit the line when you have nothing to report.

**On request: the rule table.** Output this table when the user asks to see the reasoning. Examples include requests like "show the diff", "explain the changes", or "before/after":

```markdown
| Rule violated | Original | Simplified |
|---|---|---|
| Present perfect tense | "We have received your request." | "We received your request." |
| Noun cluster (4+ words) | "the agent task queue priority handler" | "the handler that sets task-queue priority" |

Mode: Strict. 7 violations found.
```

Follow the table with a one-line note on anything you deliberately did **not** simplify, and why (usually: simplifying would lose required precision).

## Boundaries

**Will:**
- Rewrite ambiguous or dense English into short, single-meaning, active-voice sentences.
- Return the rewritten text alone by default, and name the rules it applied when the user asks.
- Preserve every fact, condition, and scope qualifier in the original.
- Preserve the strength of every hedge, and add no claim the source did not make.
- Suggest a one-line glossary entry for domain terms that must stay.

**Will not:**
- Reproduce the official ASD dictionary (~900 words) from memory. Always treat the official download as the source of truth for approved words.
- Simplify creative, marketing, or persuasive copy where voice and nuance are the point.
- Silently drop a safety condition, exception, or scope qualifier to shorten a sentence — it will flag the trade-off instead.
- Convert "may have failed" into "failed", or "could be caused by X" into "X is the cause" — losing a hedge changes the claim.
- Guarantee an aerospace/defense-grade STE-compliant document. This is a general-purpose clarity tool inspired by STE, not a certified STE authoring tool.
- Make weak content true or useful. STE fixes the *form* of a text, not its substance. A hollow paragraph rewritten under these rules becomes a clean, short, well-punctuated hollow paragraph. If the text has nothing to say, no rewrite fixes that — say so instead of polishing it.
- Shorten past the point of clarity. Cutting words is not the goal. Removing ambiguity is the goal. Extreme compression costs reader time. Stop when the sentence is unambiguous, not when it is shortest.

## Additional Resources

- [references/writing-rules.md](./references/writing-rules.md) — fuller summary of the 9 rule sections and dictionary structure, with citations to the official standard and secondary sources.
- [examples/before-after.md](./examples/before-after.md) — worked examples, including official STE examples and agent-output examples built for this skill.
- **`scripts/ste-lint.py`** — modular deterministic linter for structural STE rules (`ste/` package). It supports reflowed Markdown, GitHub alert blockquotes (`> [!NOTE]`), Zensical admonitions (`!!! note`), table cells, frontmatter descriptions, and inline suppressions (`<!-- ste-lint-disable -->`). The script returns exit code 1 when hard violations exceed `--baseline` (default 0). Advisory findings like passive voice never fail the run. Use `--disable` to silence named rules. Run `--selftest` to execute internal verification suites.
