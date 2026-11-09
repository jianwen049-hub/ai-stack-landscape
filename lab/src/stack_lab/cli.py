"""CLI entry for stack landscape decision matrices."""
from __future__ import annotations

import argparse
import sys

from stack_lab.compare import format_all, format_layers, format_table
from stack_lab.matrix import LAYER_ORDER
from stack_lab.recommend import format_recommend


def cmd_layers() -> int:
    sys.stdout.write(format_layers())
    return 0


def cmd_compare(layer: str) -> int:
    if layer == "all":
        sys.stdout.write(format_all())
        return 0
    if layer not in LAYER_ORDER:
        sys.stderr.write(f"unknown layer {layer!r}; choose: {', '.join(LAYER_ORDER)} or all\n")
        return 2
    sys.stdout.write(format_table(layer))
    return 0


def cmd_recommend(pain: str) -> int:
    sys.stdout.write(format_recommend(pain))
    return 0


def cmd_decide() -> int:
    """Offline checklist summarizing the comparison habit."""
    text = """# decide — offline checklist

1. Which layer changes most often? (framework vs retrieval vs orchestration)
2. Side effects? If yes → graph + gateway + idempotency (not unbounded ReAct).
3. Exact IDs in queries? Keep sparse; default hybrid+RRF.
4. Multiple hosts (IDE + service)? Consider MCP on top of HTTP gateway.
5. Can you trace one request end-to-end? If no → do not scale agents yet.
6. Golden set in CI? If no → prompt edits are gambling.
7. Budget caps (tokens/steps/$)? If no → expect bill spikes.

Run: compare all | recommend "<your pain>"
"""
    sys.stdout.write(text)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="stack_lab", description="AI stack landscape decision matrix")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("layers", help="list seven engineering layers")
    sp = sub.add_parser("compare", help="print trade-off table")
    sp.add_argument("layer", help="frameworks|agents|retrieval|protocols|serving|obs|cost|all")
    rp = sub.add_parser("recommend", help="heuristic picks from a pain string")
    rp.add_argument("pain", help="free text describing constraints / pain")
    sub.add_parser("decide", help="print offline decision checklist")

    args = p.parse_args(argv)
    if args.cmd == "layers":
        return cmd_layers()
    if args.cmd == "compare":
        return cmd_compare(args.layer)
    if args.cmd == "recommend":
        return cmd_recommend(args.pain)
    if args.cmd == "decide":
        return cmd_decide()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
