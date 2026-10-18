"""{{ cookiecutter.description }}"""

from __future__ import annotations

{% if cookiecutter.include_cli in [True, "yes", "true", "True", "1"] -%}
from typing import TYPE_CHECKING

from {{ cookiecutter.package_name }}._lazy import accessors

if TYPE_CHECKING:
    from {{ cookiecutter.package_name }}.cli import app
    from {{ cookiecutter.package_name }}.core import get_greeting

__version__ = "{{ cookiecutter.version }}"
__all__ = ["__version__", "app", "get_greeting"]

_LAZY_MEMBERS: dict[str, str] = {
    "app": ".cli",
    "get_greeting": ".core",
}

__getattr__, __dir__ = accessors(globals(), _LAZY_MEMBERS)
{%- else %}
from {{ cookiecutter.package_name }}.core import get_greeting

__version__ = "{{ cookiecutter.version }}"
__all__ = ["__version__", "get_greeting"]
{%- endif %}
