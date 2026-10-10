import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_prompt.py"
SPEC = importlib.util.spec_from_file_location("validate_prompt", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def codes(text, **kwargs):
    return {w["code"] for w in MODULE.validate(text, **kwargs)["warnings"]}


class ValidatePromptTests(unittest.TestCase):
    def test_standard_timeline(self):
        self.assertEqual(codes("0–4秒：看向门。\n4–10秒：坐稳。", duration=10), set())

    def test_inline_timeline_after_sentence_and_quote(self):
        text = "10秒，中景固定。0–4秒：女生说：‘你终于来了。’4–8秒：男生说：‘路上有点堵。’8–10秒：看向窗外。"
        self.assertEqual(codes(text, duration=10), set())
        self.assertEqual(len(MODULE.validate(text)["intervals"]), 3)

    def test_unicode_count_includes_newline_and_emoji(self):
        result = MODULE.validate("中文\n🌧️")
        self.assertEqual(result["characters"], 5)
        self.assertEqual(result["chinese_characters"], 2)

    def test_overlength(self):
        self.assertIn("overlength", codes("你好\n", max_chars=2))

    def test_overlap(self):
        self.assertIn("overlap", codes("0–4秒：看。\n3–6秒：听。", duration=6))

    def test_gap(self):
        self.assertIn("gap", codes("0–2秒：看。\n3–6秒：听。", duration=6))

    def test_start_nonzero(self):
        self.assertIn("start_not_zero", codes("1–5秒：听。", duration=5))

    def test_overrun(self):
        self.assertIn("duration_overrun", codes("0–11秒：听。", duration=10))

    def test_undercoverage(self):
        self.assertIn("duration_mismatch", codes("0–9秒：听。", duration=10))

    def test_reversed(self):
        self.assertIn("invalid_interval", codes("0–2秒：看。\n2–1秒：听。"))

    def test_negative_time(self):
        self.assertIn("invalid_interval", codes("-1–2秒：看。"))

    def test_out_of_order(self):
        self.assertIn("out_of_order", codes("0–3秒：看。\n3–5秒：听。\n1–2秒：转。"))

    def test_clock_timestamp(self):
        self.assertEqual(codes("00:00-00:04，看。\n00:04-00:15，听。", duration=15), set())

    def test_fullwidth_clock(self):
        self.assertEqual(codes("00：00–00：04，看。", duration=4), set())

    def test_invalid_clock(self):
        self.assertIn("invalid_timestamp", codes("00:70–01:20，看。"))

    def test_decimal_and_word_delimiter(self):
        self.assertEqual(codes("0秒至1.5秒：看。\n1.5到4秒：听。", duration=4), set())

    def test_timeline_missing(self):
        self.assertIn("timeline_missing", codes("她看着门。", duration=10))

    def test_repeated_negatives(self):
        self.assertIn("repeated_negative", codes("不要变脸。不要变脸。不要变脸。"))

    def test_sound_conflict(self):
        self.assertIn("sound_conflict", codes("完全无声。可听见门响。"))

    def test_silent_spoken_dialogue(self):
        self.assertIn("sound_conflict", codes("全程静音，女生说：‘你好。’"))

    def test_no_dialogue_spoken_conflict(self):
        self.assertIn("dialogue_conflict", codes("无对白，女生说：‘你好。’"))

    def test_no_dialogue_negated_speech(self):
        self.assertNotIn("dialogue_conflict", codes("无对白，女生不说：‘你好。’"))

    def test_no_dialogue_is_not_silent(self):
        self.assertNotIn("sound_conflict", codes("无对白，保留环境声。"))

    def test_silent_negated_audio(self):
        self.assertNotIn("sound_conflict", codes("全程静音，不加配乐，不再有环境声。"))

    def test_silent_without_audio(self):
        self.assertNotIn("sound_conflict", codes("全程静音，无配乐，无环境声。"))

    def test_subtitle_conflict(self):
        self.assertIn("subtitle_conflict", codes("不要字幕。添加日中双语字幕。"))

    def test_no_subtitle_not_added(self):
        self.assertNotIn("subtitle_conflict", codes("不要字幕，不添加中文字幕。"))

    def test_camera_conflict(self):
        self.assertIn("camera_conflict", codes("固定机位，摄影机缓慢推近。"))

    def test_negated_camera_move(self):
        self.assertNotIn("camera_conflict", codes("固定机位，不要推近。"))

    def test_handoff_complete(self):
        self.assertNotIn("handoff_check", codes("两人，甲递出书，乙接触并握稳，甲松开。"))

    def test_handoff_missing_release(self):
        self.assertIn("handoff_check", codes("甲递出书，乙接住。"))

    def test_handoff_wrong_order(self):
        self.assertIn("handoff_check", codes("甲松开，甲递出书，乙握稳。"))

    def test_dialogue_budget(self):
        self.assertIn("dialogue_budget", codes("台词：“" + "明天" * 45 + "”", duration=15))

    def test_short_speaking_segment(self):
        text = "0–12秒：等待。\n12–15秒：台词：“" + "明天" * 15 + "”"
        self.assertIn("segment_dialogue_budget", codes(text, duration=15))

    def test_empty(self):
        self.assertIn("empty_prompt", codes("  "))

    def test_cli_stdin_json_and_warning_success(self):
        process = subprocess.run([sys.executable, str(SCRIPT), "--max-chars", "1", "--json"],
                                 input="中文", text=True, capture_output=True)
        self.assertEqual(process.returncode, 0)
        self.assertEqual(json.loads(process.stdout)["warnings"][0]["code"], "overlength")

    def test_cli_input_error(self):
        process = subprocess.run([sys.executable, str(SCRIPT), "/nonexistent/prompt.txt"], capture_output=True)
        self.assertEqual(process.returncode, 2)

    def test_cli_preserves_crlf_character_count(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "prompt.txt"
            path.write_bytes("中文\r\n".encode("utf-8"))
            process = subprocess.run([sys.executable, str(SCRIPT), str(path), "--json"],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 0)
            self.assertEqual(json.loads(process.stdout)["characters"], 4)

    def test_cli_invalid_duration(self):
        process = subprocess.run([sys.executable, str(SCRIPT), "--duration", "nan"], capture_output=True)
        self.assertEqual(process.returncode, 2)


if __name__ == "__main__":
    unittest.main()
