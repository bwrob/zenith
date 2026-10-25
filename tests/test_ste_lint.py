"""Unit tests for .agents/skills/guide-ste100/scripts/ (ste modular linter package)."""

from __future__ import annotations

import contextlib
import io
from typing import TYPE_CHECKING

import pytest
from ste import markdown as ste_markdown
from ste.cli import main, run_selftest
from ste.directives import Action, Directive, build_suppressions, parse_directive
from ste.engine import lint_document
from ste.fixer import fix_line, fix_text
from ste.inline import mask_inline
from ste.markdown import parse, split_table_row
from ste.model import Block, BlockKind, Finding, Severity, Span, Suppressions
from ste.reporter import compute_compliance_score, format_json, format_text
from ste.rules.registry import ALL_RULES, get_rules

if TYPE_CHECKING:
    from pathlib import Path

# Accessor for the private, module-level frontmatter parser helper.
frontmatter = vars(ste_markdown)["_frontmatter"]

# Mirrors the Finding fixture in test_finding_properties_and_dict.
FILE_LINE = 2
FILE_COLUMN = 4
# _frontmatter returns index 3 after consuming a closed three-line frontmatter.
EXPECTED_FRONTMATTER_INDEX = 3
# The rule registry currently ships 17 rules, 15 of them active by default.
TOTAL_RULE_COUNT = 17
EXPECTED_ACTIVE_RULES = 15
# fix_line("don't utilize this") applies two replacements.
EXPECTED_FIXER_REPLACEMENTS = 2

PERFECT_SCORE = 100.0
HARD_PENALTY_SCORE = 85.0
ADVISORY_PENALTY_SCORE = 95.0
CLAMPED_SCORE = 0.0


def test_span_and_block_locate() -> None:
    """Test Span and Block coordinate mapping."""
    block = Block(
        kind=BlockKind.PARAGRAPH,
        text="First line. Second line.",
        spans=(
            Span(offset=0, line=10, column=1),
            Span(offset=12, line=11, column=5),
        ),
    )
    # First span
    assert block.locate(0) == (10, 1)
    assert block.locate(5) == (10, 6)
    # Second span
    assert block.locate(12) == (11, 5)
    assert block.locate(18) == (11, 11)


def test_suppressions_silencing() -> None:
    """Test Suppressions matching and line ranges."""
    sup = Suppressions(
        ranges=(
            (5, 7, frozenset({"semicolon"})),
            (10, 12, frozenset()),  # silences all
        )
    )
    assert sup.silences(6, "semicolon")
    assert not sup.silences(6, "long-sentence")
    assert not sup.silences(4, "semicolon")
    assert not sup.silences(8, "semicolon")
    # All rules silenced in 10..12
    assert sup.silences(10, "semicolon")
    assert sup.silences(11, "anything")
    assert not sup.silences(13, "anything")


def test_finding_properties_and_dict() -> None:
    """Test Finding dataclass methods."""
    f = Finding(
        file="test.md",
        line=FILE_LINE,
        column=FILE_COLUMN,
        rule="semicolon",
        severity=Severity.HARD,
        match=";",
        message="STE bans the semicolon.",
    )
    assert f.sort_key == ("test.md", FILE_LINE, FILE_COLUMN, "semicolon")
    d = f.to_dict()
    assert d["file"] == "test.md"
    assert d["line"] == FILE_LINE
    assert d["column"] == FILE_COLUMN
    assert d["rule"] == "semicolon"
    assert d["severity"] == "hard"
    assert d["match"] == ";"


def test_mask_inline_preserves_length() -> None:
    """Verify inline masking preserves string length and column alignment."""
    cases = [
        "Plain text without markup.",
        "Use `code span` inline.",
        "Check [link label](https://example.com/path).",
        "Look at ![image alt](img.png).",
        "See <https://example.com> autolink.",
        "Visit https://example.com/raw naked url.",
        "<span>HTML tag</span>",
        "&amp; and &#123; entities",
        "**bold** and *italic* and ~~strike~~ and `code`",
        "Escaped \\*asterisk\\* in prose",
    ]
    for case in cases:
        masked = mask_inline(case)
        assert len(masked) == len(case), f"Length changed for: {case!r}"


def test_directives_parsing() -> None:
    """Test parsing HTML comment directives."""
    assert parse_directive("not a directive", 1) is None
    d1 = parse_directive("ste-lint-disable", 5)
    assert d1 == Directive(5, Action.DISABLE, frozenset())
    d2 = parse_directive("ste-lint-disable-next-line semicolon, long-sentence", 8)
    assert d2 is not None
    assert d2.action == Action.DISABLE_NEXT_LINE
    assert d2.rules == frozenset({"semicolon", "long-sentence"})

    # Test folding directives into suppressions
    dirs = [
        Directive(3, Action.DISABLE_FILE, frozenset({"passive-voice"})),
        Directive(5, Action.DISABLE, frozenset({"semicolon"})),
        Directive(8, Action.ENABLE, frozenset({"semicolon"})),
        Directive(10, Action.DISABLE_NEXT_LINE, frozenset({"phrasal-verb"})),
    ]
    sup = build_suppressions(dirs, last_line=20)
    assert sup.silences(1, "passive-voice")
    assert sup.silences(20, "passive-voice")
    assert sup.silences(6, "semicolon")
    assert not sup.silences(9, "semicolon")
    assert sup.silences(11, "phrasal-verb")
    assert not sup.silences(12, "phrasal-verb")


def test_split_table_row() -> None:
    """Test GFM table row splitting."""
    assert split_table_row("no pipe here") is None
    assert split_table_row("| only one |") is None

    cells = split_table_row("| Col A | Col B | Col C |")
    assert cells is not None
    assert [c[0] for c in cells] == ["Col A", "Col B", "Col C"]

    escaped = split_table_row("| a \\| b | c |")
    assert escaped is not None
    assert escaped[0][0] == "a \\| b"
    assert escaped[1][0] == "c"


def test_markdown_scanner_structures() -> None:
    """Test markdown parser handling various constructs."""
    text = (
        "---\n"
        "name: test-skill\n"
        "description: >-\n"
        "  First line of description.\n"
        "  Second line of description.\n"
        "---\n"
        "# Main Heading\n"
        "\n"
        "A paragraph with reflowed\n"
        "lines that should join.\n"
        "\n"
        "```python\n"
        "x = 1; y = 2\n"
        "```\n"
        "\n"
        "$$\n"
        "e = mc^2;\n"
        "$$\n"
        "\n"
        "> [!NOTE]\n"
        "> An admonition paragraph inside\n"
        "> a blockquote.\n"
        "\n"
        '!!! tip "Admonition"\n'
        "    Indented admonition text.\n"
        "\n"
        "- First list item and\n"
        "- Second list item\n"
    )
    doc = parse(text, filename="doc.md")
    assert doc.filename == "doc.md"

    kinds = [b.kind for b in doc.blocks]
    assert BlockKind.FRONTMATTER in kinds
    assert BlockKind.HEADING in kinds
    assert BlockKind.PARAGRAPH in kinds
    assert BlockKind.LIST_ITEM in kinds

    # Verify description extraction
    fm_block = next(b for b in doc.blocks if b.kind == BlockKind.FRONTMATTER)
    assert "First line of description" in fm_block.text
    assert "Second line of description" in fm_block.text


def test_markdown_frontmatter_edge_cases() -> None:
    """Test frontmatter parser with missing boundaries or no description."""
    assert frontmatter([]) == (0, [])
    assert frontmatter(["# Not frontmatter"]) == (0, [])
    assert frontmatter(["---", "name: test"]) == (0, [])  # unclosed

    # No description key
    idx, blocks = frontmatter(["---", "name: test", "---"])
    assert idx == EXPECTED_FRONTMATTER_INDEX
    assert blocks == []

    # Single-line description with quotes
    idx, blocks = frontmatter(["---", 'description: "Quoted value"', "---"])
    assert idx == EXPECTED_FRONTMATTER_INDEX
    assert len(blocks) == 1
    assert "Quoted value" in blocks[0].text


def test_all_rules_and_get_rules() -> None:
    """Test rule retrieval and filtering."""
    assert len(ALL_RULES) == TOTAL_RULE_COUNT
    active = get_rules(disabled=["semicolon", "passive-voice"])
    assert len(active) == EXPECTED_ACTIVE_RULES
    rule_ids = {r.id for r in active}
    assert "semicolon" not in rule_ids
    assert "passive-voice" not in rule_ids
    assert "phrasal-verb" in rule_ids
    assert "unapproved-phrase" in rule_ids
    assert "unapproved-word" in rule_ids
    assert "contraction" in rule_ids
    assert "latin-abbrev" in rule_ids
    assert "ing-clause" in rule_ids
    assert "banned-modal" in rule_ids
    assert "trailing-condition" in rule_ids
    assert "paragraph-length" in rule_ids


def test_lint_engine_and_reporters() -> None:
    """Test engine aggregation and reporter outputs."""
    text = "The system is ready; spin up the cluster."
    doc = parse(text, filename="input.md")
    res = lint_document(doc)
    assert res.hard_count > 0
    assert res.violation_rate > 0.0

    txt_out = format_text(res.findings, res.words_total, res.hard_count, baseline=0)
    assert "violations" in txt_out
    assert "input.md" in txt_out

    json_out = format_json(res.findings, res.words_total, res.hard_count, baseline=0)
    assert '"hard_count":' in json_out
    assert '"violations":' in json_out


def test_cli_selftest() -> None:
    """Run CLI internal selftest directly."""
    assert run_selftest() == 0


def test_cli_execution_with_file_and_stdin(tmp_path: Path) -> None:
    """Test CLI invoking with file argument, stdin, list-rules, and flags."""
    test_file = tmp_path / "sample.md"
    test_file.write_text("All is clean and clear.\n", encoding="utf-8")

    # Clean file passes
    assert main([str(test_file)]) == 0

    # Non-existent file fails
    assert main([str(tmp_path / "missing.md")]) == 1

    # List rules exits 0
    assert main(["--list-rules"]) == 0

    # Selftest flag exits 0
    assert main(["--selftest"]) == 0

    # Stdin input with hard violation
    stdin_stream = io.StringIO("This sentence has; a semicolon.")
    assert main([], stdin=stdin_stream) == 1

    # Stdin with baseline tolerating violation
    stdin_stream2 = io.StringIO("This sentence has; a semicolon.")
    assert main(["--baseline", "1"], stdin=stdin_stream2) == 0

    # JSON output
    stdin_stream3 = io.StringIO("Clean text.")
    assert main(["--json"], stdin=stdin_stream3) == 0


def test_link_definition_skipped() -> None:
    """Verify markdown reference-style link definitions are skipped by scanner."""
    text = (
        "See [the reference][ref] for detail.\n\n"
        "[ref]: https://example.com/very/long/url/path/that/should/not/count/as/prose\n"
    )
    doc = parse(text)
    assert len(doc.blocks) == 1
    assert "the reference" in doc.blocks[0].text


def test_reporter_files_count() -> None:
    """Verify formatters correctly display multiple files count."""
    txt = format_text([], 50, 0, baseline=0, files_count=3)
    assert "in 3 files" in txt

    js = format_json([], 50, 0, baseline=0, files_count=3)
    assert '"files": 3' in js


def test_cli_directory_input(tmp_path: Path) -> None:
    """Test CLI scanning a directory containing markdown files and skipped dirs."""
    sub_dir = tmp_path / "skills"
    sub_dir.mkdir()
    (sub_dir / "clean1.md").write_text("All is clean and concise.\n", encoding="utf-8")
    (sub_dir / "clean2.md").write_text(
        "Second file is also concise.\n", encoding="utf-8"
    )

    # Skipped directory
    git_dir = sub_dir / ".git"
    git_dir.mkdir()
    (git_dir / "ignore.md").write_text("Has; semicolon\n", encoding="utf-8")

    assert main([str(sub_dir)]) == 0


def test_extended_rules() -> None:
    """Verify extended marketing adjectives, unapproved phrases, and synonym groups."""
    # Test unapproved phrase
    doc1 = parse("In the event that the file is missing, exit.")
    res1 = lint_document(doc1)
    assert any(f.rule == "unapproved-phrase" for f in res1.findings)

    # Test marketing adjective
    doc2 = parse("This provides a bulletproof setup.")
    res2 = lint_document(doc2)
    assert any(f.rule == "marketing-adjective" for f in res2.findings)

    # Test synonym rotation for allow / permit
    doc3 = parse("We allow read access. We also permit write access.")
    res3 = lint_document(doc3)
    assert any(f.rule == "synonym-rotation" for f in res3.findings)


def test_unapproved_words_and_bare_nominalization() -> None:
    """Verify unapproved-word rule and bare nominalizations without articles."""
    doc = parse(
        "We utilize this method and commence testing. "
        "We perform verification of the data."
    )
    res = lint_document(doc)
    rules_hit = {f.rule for f in res.findings}
    assert "unapproved-word" in rules_hit
    assert "nominalization" in rules_hit

    # Test expanded unapproved phrases
    doc_phrase = parse(
        "The agent is capable of running tasks in conjunction with other tools."
    )
    res_phrase = lint_document(doc_phrase)
    assert any(f.rule == "unapproved-phrase" for f in res_phrase.findings)

    doc_new = parse(
        "This operation is hazardous and precludes recovery. "
        "The agent is able to proceed."
    )
    res_new = lint_document(doc_new)
    rules_new = {f.rule for f in res_new.findings}
    assert "unapproved-word" in rules_new
    assert "unapproved-phrase" in rules_new


def test_compute_compliance_score() -> None:
    """Verify compliance scoring calculations and bounds."""
    # Empty text -> perfect score
    assert compute_compliance_score([], 0, 0) == pytest.approx(PERFECT_SCORE)

    # Clean text -> perfect score
    assert compute_compliance_score([], 100, 0) == pytest.approx(PERFECT_SCORE)

    # Advisory vs hard penalty
    f_hard = Finding(
        file="test.md",
        line=1,
        column=1,
        rule="semicolon",
        severity=Severity.HARD,
        match=";",
        message="Hard",
    )
    f_adv = Finding(
        file="test.md",
        line=2,
        column=1,
        rule="passive-voice",
        severity=Severity.ADVISORY,
        match="is done",
        message="Advisory",
    )
    # 1 hard in 100 words -> 100 - (15 * 1.0) = 85.0
    assert compute_compliance_score([f_hard], 100, 1) == pytest.approx(
        HARD_PENALTY_SCORE
    )
    # 1 advisory in 100 words -> 100 - (5 * 1.0) = 95.0
    assert compute_compliance_score([f_adv], 100, 0) == pytest.approx(
        ADVISORY_PENALTY_SCORE
    )

    # Extreme violations clamp to 0.0
    many_findings = [f_hard] * 10
    assert compute_compliance_score(many_findings, 50, 10) == pytest.approx(
        CLAMPED_SCORE
    )


def test_contractions_latin_and_ing_clause() -> None:
    """Verify contractions, Latin abbreviations, and subordinate -ing clauses."""
    # Test contraction
    doc1 = parse("Don't run this command; it's dangerous.")
    res1 = lint_document(doc1)
    assert any(f.rule == "contraction" for f in res1.findings)

    # Test Latin abbreviations
    doc2 = parse("Install required packages (e.g. pytest, ruff, etc.).")
    res2 = lint_document(doc2)
    assert any(f.rule == "latin-abbrev" for f in res2.findings)

    # Test subordinate -ing participle clause
    doc3 = parse("We configure the cache, enabling faster subsequent test runs.")
    res3 = lint_document(doc3)
    assert any(f.rule == "ing-clause" for f in res3.findings)

    # Test expanded slop word and slop phrase
    doc4 = parse("We delve into this problem when it comes to performance.")
    res4 = lint_document(doc4)
    rules4 = {f.rule for f in res4.findings}
    assert "unapproved-word" in rules4
    assert "unapproved-phrase" in rules4


def test_banned_modals_trailing_conditions_and_paragraphs() -> None:
    """Verify banned-modal, trailing-condition, and paragraph-length rules."""
    # Banned modal
    doc_modal = parse("You should verify the output. You ought to proceed.")
    res_modal = lint_document(doc_modal)
    assert any(f.rule == "banned-modal" for f in res_modal.findings)

    # Trailing condition
    doc_cond = parse("Shut down the process, if the memory exceeds limits.")
    res_cond = lint_document(doc_cond)
    assert any(f.rule == "trailing-condition" for f in res_cond.findings)

    # Paragraph length (more than 6 sentences)
    seven_sentences = (
        "One sentence. Two sentence. Three sentence. Four sentence. "
        "Five sentence. Six sentence. Seven sentence."
    )
    doc_para = parse(seven_sentences)
    res_para = lint_document(doc_para)
    assert any(f.rule == "paragraph-length" for f in res_para.findings)

    # Compliant paragraph (6 sentences or fewer)
    six_sentences = (
        "One sentence. Two sentence. Three sentence. Four sentence. "
        "Five sentence. Six sentence."
    )
    doc_para_ok = parse(six_sentences)
    res_para_ok = lint_document(doc_para_ok)
    assert not any(f.rule == "paragraph-length" for f in res_para_ok.findings)


def test_fixer_and_cli_fix(tmp_path: Path) -> None:
    """Verify deterministic fixer and CLI --fix flag."""
    sample = (
        "# Title\n\n"
        "In order to test, don't run `don't break this code`.\n"
        "Install tools (e.g. pytest).\n\n"
        "```python\n"
        "# in order to stay untouched\n"
        "val = don't\n"
        "```\n\n"
        "<!-- ste-lint-disable -->\n"
        "in order to ignore\n"
        "<!-- ste-lint-enable -->\n\n"
        "Subsequent to tests, utilize the cache.\n"
    )
    fixed, count = fix_text(sample)
    assert count > 0
    assert "To test, do not run `don't break this code`." in fixed
    assert "(for example, pytest)." in fixed
    assert "# in order to stay untouched" in fixed
    assert "in order to ignore" in fixed
    assert "After tests, use the cache." in fixed

    # Line without backticks
    plain_fixed, p_count = fix_line("don't utilize this")
    assert plain_fixed == "do not use this"
    assert p_count == EXPECTED_FIXER_REPLACEMENTS

    # CLI --fix on file
    f_path = tmp_path / "fix_me.md"
    f_path.write_text("Don't fail this.\n", encoding="utf-8")
    assert main(["--fix", str(f_path)]) == 0
    assert f_path.read_text(encoding="utf-8") == "Do not fail this.\n"

    # CLI --fix on stdin
    stdin_stream = io.StringIO("In order to proceed.\n")
    stdout_stream = io.StringIO()

    with contextlib.redirect_stdout(stdout_stream):
        assert main(["--fix"], stdin=stdin_stream) == 0
    assert stdout_stream.getvalue() == "To proceed.\n"
