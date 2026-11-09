"""Unit tests for matrix integrity and recommend heuristics."""
from __future__ import annotations

import unittest

from stack_lab.matrix import LAYER_ORDER, LAYERS
from stack_lab.recommend import recommend
from stack_lab.compare import format_table, format_all


REQUIRED = {"id", "label", "pros", "cons", "best_for", "watchouts"}


class TestMatrix(unittest.TestCase):
    def test_seven_layers(self):
        self.assertEqual(
            LAYER_ORDER,
            ["frameworks", "agents", "retrieval", "protocols", "serving", "obs", "cost"],
        )
        for key in LAYER_ORDER:
            self.assertIn(key, LAYERS)
            layer = LAYERS[key]
            self.assertGreaterEqual(len(layer["options"]), 3, key)
            for opt in layer["options"]:
                self.assertTrue(REQUIRED.issubset(opt.keys()), opt)

    def test_frameworks_cover_big_four(self):
        ids = {o["id"] for o in LAYERS["frameworks"]["options"]}
        for need in ("langchain_langgraph", "llamaindex", "spring_ai", "raw_sdk"):
            self.assertIn(need, ids)

    def test_format_smoke(self):
        text = format_table("frameworks")
        self.assertIn("Spring AI", text)
        all_text = format_all()
        self.assertIn("MCP", all_text)
        self.assertIn("Hybrid", all_text)

    def test_recommend_java_spring(self):
        ranked = recommend("java spring enterprise rag with approval 退款")
        labels = [s.label for s in ranked]
        self.assertTrue(any("Spring" in x for x in labels))
        self.assertTrue(any("Graph" in x or "graph" in x.lower() for x in labels))
        self.assertTrue(any("Hybrid" in x for x in labels))

    def test_recommend_mcp_ide(self):
        ranked = recommend("expose tools to IDE via mcp across apps")
        self.assertTrue(any(s.option_id == "mcp" for s in ranked))


if __name__ == "__main__":
    unittest.main()
