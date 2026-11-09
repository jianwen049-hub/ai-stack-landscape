"""Format decision-matrix tables as plain text (stdlib only)."""
from __future__ import annotations

from stack_lab.matrix import LAYER_ORDER, LAYERS, get_layer


def _join(items: list[str], sep: str = "; ") -> str:
    return sep.join(items)


def format_layers() -> str:
    lines = ["# AI engineering layers", ""]
    for i, key in enumerate(LAYER_ORDER, 1):
        layer = LAYERS[key]
        lines.append(f"{i}. [{key}] {layer['title']} / {layer['title_zh']}")
        lines.append(f"   {layer['purpose']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def format_table(layer_key: str) -> str:
    layer = get_layer(layer_key)
    lines = [
        f"# {layer['title']} ({layer['title_zh']})",
        f"# {layer['purpose']}",
        "",
        f"{'Option':<36} | {'Best for':<42} | Watchouts",
        f"{'-'*36}-+-{'-'*42}-+-{'-'*40}",
    ]
    for opt in layer["options"]:
        best = _join(opt["best_for"], ", ")
        watch = _join(opt["watchouts"], ", ")
        if len(best) > 42:
            best = best[:39] + "..."
        if len(watch) > 56:
            watch = watch[:53] + "..."
        lines.append(f"{opt['label']:<36} | {best:<42} | {watch}")
    lines.append("")
    lines.append("## Pros / Cons detail")
    lines.append("")
    for opt in layer["options"]:
        lines.append(f"### {opt['label']} (`{opt['id']}`)")
        lines.append(f"- Pros: {_join(opt['pros'])}")
        lines.append(f"- Cons: {_join(opt['cons'])}")
        lines.append(f"- Best for: {_join(opt['best_for'])}")
        lines.append(f"- Watchouts: {_join(opt['watchouts'])}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def format_all() -> str:
    parts = [format_layers(), ""]
    for key in LAYER_ORDER:
        parts.append(format_table(key))
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"
