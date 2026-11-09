#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stack_lab.cli import cmd_compare, cmd_layers, cmd_recommend, cmd_decide
from stack_lab.matrix import LAYER_ORDER, LAYERS


def main() -> int:
    assert LAYER_ORDER == [
        "frameworks",
        "agents",
        "retrieval",
        "protocols",
        "serving",
        "obs",
        "cost",
    ]
    for key in LAYER_ORDER:
        assert key in LAYERS and len(LAYERS[key]["options"]) >= 3, key

    fw_ids = {o["id"] for o in LAYERS["frameworks"]["options"]}
    for need in ("langchain_langgraph", "llamaindex", "spring_ai", "raw_sdk"):
        assert need in fw_ids, need

    assert cmd_layers() == 0
    assert cmd_compare("frameworks") == 0
    assert cmd_compare("all") == 0
    assert cmd_recommend("java spring rag mcp 审批 pii") == 0
    assert cmd_decide() == 0

    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        return 1
    print("smoke_check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
