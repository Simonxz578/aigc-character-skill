import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("prompt_checks", ROOT / "scripts" / "validate_prompt.py")
CHECKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKS)


class ExampleTests(unittest.TestCase):
    def test_ten_original_examples_and_twelve_prompts(self):
        examples = sorted((ROOT / "examples").glob("*.md"))
        self.assertEqual(len(examples), 10)
        prompts = 0
        for path in examples:
            doc = path.read_text(encoding="utf-8")
            for heading in ("## 用户输入", "## 分类与约束"):
                self.assertIn(heading, doc, path.name)
            blocks = re.findall(r"```text\n(.*?)\n```", doc, re.S)
            self.assertTrue(blocks, path.name)
            for text in blocks:
                prompts += 1
                duration = float(re.match(r"(\d+)秒", text)[1])
                result = CHECKS.validate(text, duration, 5000)
                self.assertEqual(result["warnings"], [], (path.name, result["warnings"]))
        self.assertEqual(prompts, 12)

    def test_cinematic_demo_chinese_length(self):
        for name in ("01-ancient-joy-to-regret.md", "02-silent-crying.md"):
            text = re.search(r"```text\n(.*?)\n```", (ROOT / "examples" / name).read_text(), re.S)[1]
            count = CHECKS.validate(text)["chinese_characters"]
            self.assertGreaterEqual(count, 1200)
            self.assertLessEqual(count, 1700)

    def test_three_length_modes(self):
        blocks = re.findall(r"```text\n(.*?)\n```", (ROOT / "examples" / "04-shy-romance.md").read_text(), re.S)
        for text, (low, high) in zip(blocks, ((180, 350), (450, 900), (1100, 1700))):
            count = CHECKS.validate(text)["chinese_characters"]
            self.assertGreaterEqual(count, low)
            self.assertLessEqual(count, high)

    def test_knight_emotional_closeup_is_three_seconds(self):
        text = (ROOT / "examples" / "07-anime-sword-duel.md").read_text()
        self.assertIn("14–17秒：", text)
        intervals = CHECKS.validate(re.search(r"```text\n(.*?)\n```", text, re.S)[1])["intervals"]
        self.assertEqual(next(i["end"] - i["start"] for i in intervals if i["start"] == 14), 3)

    def test_markdown_local_links_resolve(self):
        for path in ROOT.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" in target or target.startswith("#"):
                    continue
                self.assertTrue((path.parent / target.split("#")[0]).is_file(), (path.name, target))


if __name__ == "__main__":
    unittest.main()
