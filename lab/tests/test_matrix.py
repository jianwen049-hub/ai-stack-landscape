"""Unit tests for matrix integrity and recommend heuristics."""
from __future__ import annotations

import unittest

from stack_lab.matrix import LAYER_ORDER, LAYERS
from stack_lab.recommend import RULES, recommend
from stack_lab.compare import format_table, format_all

REQUIRED = {"id", "label", "pros", "cons", "best_for", "watchouts"}

NEW_DEBATE_OPTIONS = {
    "frameworks": {"pydantic_ai", "ts_edge_sdk"},
    "agents": {"crewai_autogen", "openai_agents_sdk"},
    "retrieval": {"store_qdrant", "graph_rag", "contextual_chunks"},
    "protocols": {"a2a"},
    "serving": {"llm_gateway", "batch_api"},
    "obs": {"otel_genai", "llm_judge"},
    "cost": {"prompt_cache", "semantic_cache"},
}


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

    def test_new_debate_options_present(self):
        for layer_key, needed in NEW_DEBATE_OPTIONS.items():
            ids = {o["id"] for o in LAYERS[layer_key]["options"]}
            for need in needed:
                self.assertIn(need, ids, f"{layer_key}/{need}")

    def test_option_ids_unique_per_layer(self):
        for key in LAYER_ORDER:
            ids = [o["id"] for o in LAYERS[key]["options"]]
            self.assertEqual(len(ids), len(set(ids)), key)

    def test_format_smoke(self):
        text = format_table("frameworks")
        self.assertIn("Spring AI", text)
        all_text = format_all()
        self.assertIn("MCP", all_text)
        self.assertIn("Hybrid", all_text)
        self.assertIn("Qdrant", all_text)
        self.assertIn("OpenTelemetry GenAI", all_text)

    def test_recommend_rules_reference_real_options(self):
        for kw, layer, opt_id, weight, reason in RULES:
            self.assertIn(layer, LAYERS, f"rule kw={kw!r} layer={layer!r}")
            ids = {o["id"] for o in LAYERS[layer]["options"]}
            self.assertIn(opt_id, ids, f"rule kw={kw!r} option={opt_id!r}")
            self.assertGreater(weight, 0)
            self.assertTrue(reason)

    def test_recommend_java_spring(self):
        ranked = recommend("java spring enterprise rag with approval 退款")
        labels = [s.label for s in ranked]
        self.assertTrue(any("Spring" in x for x in labels))
        self.assertTrue(any("Graph" in x or "graph" in x.lower() for x in labels))
        self.assertTrue(any("Hybrid" in x for x in labels))

    def test_recommend_mcp_ide(self):
        ranked = recommend("expose tools to IDE via mcp across apps")
        self.assertTrue(any(s.option_id == "mcp" for s in ranked))

    def test_recommend_new_stack_pain(self):
        ranked = recommend("多供应商 qdrant otel 语义缓存 护栏")
        ids = {(s.layer, s.option_id) for s in ranked}
        self.assertIn(("serving", "llm_gateway"), ids)
        self.assertIn(("retrieval", "store_qdrant"), ids)
        self.assertIn(("obs", "otel_genai"), ids)
        self.assertIn(("cost", "semantic_cache"), ids)
        self.assertIn(("cost", "guardrails"), ids)

    def test_recommend_multiagent_frameworks(self):
        ranked = recommend("crewai autogen 多 agent handoff")
        ids = {s.option_id for s in ranked}
        self.assertIn("crewai_autogen", ids)
        self.assertIn("openai_agents_sdk", ids)


if __name__ == "__main__":
    unittest.main()