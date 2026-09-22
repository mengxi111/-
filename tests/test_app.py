import json
import unittest
from unittest.mock import Mock, patch

from backend.app import build_prompt, call_ollama_json, extract_json_substring


class AppFunctionTests(unittest.TestCase):
    def test_extracts_json_from_model_commentary(self):
        raw = '结果如下：\n{"topic":"Python","days":[]}\n完成'

        self.assertEqual(
            extract_json_substring(raw),
            '{"topic":"Python","days":[]}',
        )

    def test_returns_none_when_json_is_missing(self):
        self.assertIsNone(extract_json_substring("没有结构化内容"))

    def test_prompt_contains_requested_topic_and_days(self):
        prompt = build_prompt("FastAPI", 5)

        self.assertIn("topic=FastAPI", prompt)
        self.assertIn("days=5", prompt)

    @patch("backend.app.requests.post")
    def test_parses_strict_json_response(self, post: Mock):
        response = Mock()
        response.json.return_value = {"response": json.dumps({"ok": True})}
        post.return_value = response

        result = call_ollama_json("test-model", "test prompt")

        self.assertEqual(result, {"ok": True, "data": {"ok": True}})
        response.raise_for_status.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
