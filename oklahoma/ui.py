"""Render the universe and its history into web/index.html.

`web/template.html` is a complete HTML document with two JSON placeholders;
rendering is a straight substitution. The page inlines per-name coverage
and thinned series, not the full history — enough to inspect what loaded
without shipping every bar.
"""

from __future__ import annotations

import json
import os

from .config import UI_OUTPUT_PATH, UI_TEMPLATE_PATH

UNIVERSE_PLACEHOLDER = "__UNIVERSE_JSON__"
HISTORY_PLACEHOLDER = "__HISTORY_JSON__"


def _inline(payload) -> str:
    # `</` inside an inline JSON block would close the script tag early.
    return json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")


def render(
    universe: dict,
    history_index: dict | None = None,
    template_path: str = UI_TEMPLATE_PATH,
) -> str:
    with open(template_path, encoding="utf-8") as handle:
        template = handle.read()
    for placeholder in (UNIVERSE_PLACEHOLDER, HISTORY_PLACEHOLDER):
        if placeholder not in template:
            raise ValueError(f"{template_path} is missing {placeholder}")
    return template.replace(UNIVERSE_PLACEHOLDER, _inline(universe)).replace(
        HISTORY_PLACEHOLDER, _inline(history_index)
    )


def build(
    universe: dict,
    history_index: dict | None = None,
    output_path: str = UI_OUTPUT_PATH,
    template_path: str = UI_TEMPLATE_PATH,
) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(render(universe, history_index, template_path))
    return output_path
