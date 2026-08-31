"""Render the universe into a self-contained page.

`web/template.html` is a fragment: title, styles, markup and script, with the
universe injected as inline JSON. The fragment is what gets published to a
host that supplies its own document skeleton; `build()` wraps the same
fragment in a full document so `web/index.html` opens straight from disk.
"""

from __future__ import annotations

import json
import os

from .config import UI_OUTPUT_PATH, UI_TEMPLATE_PATH

PLACEHOLDER = "__UNIVERSE_JSON__"
HISTORY_PLACEHOLDER = "__HISTORY_JSON__"

DOCUMENT = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{fragment}
</body>
</html>
"""


def _inline(payload) -> str:
    # `</` inside an inline JSON block would close the script tag early.
    return json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")


def render_fragment(
    universe: dict,
    history_index: dict | None = None,
    template_path: str = UI_TEMPLATE_PATH,
) -> str:
    """Inline the universe, and the history index when one has been built.

    The page carries per-name coverage and a thinned price series, not the
    full history: enough to inspect what loaded without shipping every bar.
    """
    with open(template_path, encoding="utf-8") as handle:
        template = handle.read()
    for placeholder in (PLACEHOLDER, HISTORY_PLACEHOLDER):
        if placeholder not in template:
            raise ValueError(f"{template_path} is missing {placeholder}")
    return template.replace(PLACEHOLDER, _inline(universe)).replace(
        HISTORY_PLACEHOLDER, _inline(history_index)
    )


def render_document(
    universe: dict,
    history_index: dict | None = None,
    template_path: str = UI_TEMPLATE_PATH,
) -> str:
    fragment = render_fragment(universe, history_index, template_path)
    head, _, body = fragment.partition("<script id=\"universe-data\"")
    return DOCUMENT.format(
        fragment=f"{head}</head>\n<body>\n<script id=\"universe-data\"{body}"
    )


def build(
    universe: dict,
    history_index: dict | None = None,
    output_path: str = UI_OUTPUT_PATH,
    template_path: str = UI_TEMPLATE_PATH,
) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(render_document(universe, history_index, template_path))
    return output_path
