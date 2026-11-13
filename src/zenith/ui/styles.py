"""CSS styling constants for the Zenith Textual setup wizard."""

from __future__ import annotations

ZENITH_CSS = """
Screen {
    background: #020408;
    color: #e0f2fe;
}
Header {
    background: #0f172a;
    color: #38bdf8;
}
Footer {
    background: #0f172a;
}
VerticalScroll {
    padding: 1 2;
    background: #020408;
    scrollbar-color: #38bdf8;
    scrollbar-background: #0f172a;
}
Vertical {
    height: auto;
}
.brand-title {
    text-style: bold;
    color: #38bdf8;
    margin-top: 1;
    margin-bottom: 0;
}
.brand-subtitle {
    color: #94a3b8;
    margin-bottom: 1;
}
.section-title {
    text-style: bold;
    color: #38bdf8;
    margin-top: 1;
    margin-bottom: 1;
}
.field-label {
    color: #94a3b8;
    margin-top: 1;
}
.target-preview {
    color: #38bdf8;
    margin-top: 0;
    margin-bottom: 1;
}
.target-warning {
    color: #f43f5e;
    text-style: bold;
}
Input {
    background: #1e293b;
    border: tall #334155;
    color: #e0f2fe;
}
Input:focus {
    border: tall #38bdf8;
}
Input.-invalid {
    border: tall #f43f5e;
}
Input.-invalid:focus {
    border: tall #f43f5e;
}
.field-error {
    color: #f43f5e;
    margin-top: 0;
    margin-bottom: 0;
    display: none;
}
.field-error.visible {
    display: block;
}
.prereq-warning {
    color: #f59e0b;
    text-style: bold;
    margin-bottom: 1;
    display: none;
}
.prereq-warning.visible {
    display: block;
}
.overwrite-checkbox {
    display: none;
    margin-bottom: 1;
}
.overwrite-checkbox.visible {
    display: block;
}
.step-summary {
    color: #94a3b8;
    background: #0f172a;
    border: solid #1e293b;
    padding: 0 1;
    margin-bottom: 1;
}
Select {
    background: #1e293b;
    border: tall #334155;
    color: #e0f2fe;
}
Select:focus {
    border: tall #38bdf8;
}
Checkbox {
    color: #e0f2fe;
    margin-top: 0;
    margin-bottom: 0;
}
.preset-bar {
    height: auto;
    margin-top: 1;
    margin-bottom: 1;
}
.preset-bar Button {
    margin-right: 1;
    background: #1e293b;
    color: #e0f2fe;
    border: solid #334155;
}
.preset-bar Button:hover {
    border: solid #38bdf8;
    color: #38bdf8;
}
#preset-recommended {
    border: solid #0284c7;
    color: #38bdf8;
}
#ai-tools-list {
    height: 14;
    border: solid #0284c7;
    background: #0f172a;
    color: #e0f2fe;
    margin-bottom: 1;
}
#ai-tools-list:focus {
    border: solid #38bdf8;
}
.actions-bar {
    height: auto;
    margin-top: 2;
    margin-bottom: 2;
}
.actions-bar Button {
    margin-right: 2;
}
#next-btn {
    background: #0284c7;
    color: #ffffff;
    border: solid #38bdf8;
}
#back-btn {
    background: #1e293b;
    color: #e0f2fe;
    border: solid #334155;
}
#submit-btn {
    background: #0ea5e9;
    color: #ffffff;
    border: solid #38bdf8;
}
#cancel-btn {
    background: #1e293b;
    color: #f43f5e;
    border: solid #f43f5e;
}
"""
