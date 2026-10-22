{% if cookiecutter.include_ci_testing in [True, "yes", "true", "True", "1"] %}
[![CI](https://github.com/{{ cookiecutter.github_username }}/{{
cookiecutter.project_slug
}}/actions/workflows/python_tests.yaml/badge.svg)](https://github.com/{{
cookiecutter.github_username }}/{{ cookiecutter.project_slug
}}/actions/workflows/python_tests.yaml)
{% endif %}
[![Python: {{ cookiecutter.python_version }}+](https://img.shields.io/badge/python-{{ cookiecutter.python_version }}+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type Checked: Pyrefly](https://img.shields.io/badge/types-pyrefly-blueviolet.svg)](https://github.com/facebook/pyrefly)
[![Coverage: pytest-cov](https://img.shields.io/badge/coverage-80%25%2B-brightgreen.svg)](.coveragerc)
{% if cookiecutter.license != "None" %}
[![License: {{ cookiecutter.license }}](https://img.shields.io/badge/license-{{ cookiecutter.license }}-green.svg)](LICENSE)
{% endif %}
