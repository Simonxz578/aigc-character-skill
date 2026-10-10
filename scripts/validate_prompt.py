#!/usr/bin/env python3
"""Offline, heuristic prompt checks. Semantic warnings always exit 0."""
import argparse
import json
import math
import re
import sys
from pathlib import Path

TOKEN = r"-?\d+(?::\d{1,2}){0,2}(?:\.\d+)?"
INTERVAL = re.compile(
    r"(?:^|(?<=[。；\n’”]))\s*(?:[-*]\s+)?(" + TOKEN + r")\s*(?:秒|s)?\s*"
    r"(?:-|–|—|~|～|至|到|→)\s*(" + TOKEN + r")\s*(?:秒|s)?"
    r"(?=\s|[：:,，、]|$)", re.MULTILINE
)
CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\U00020000-\U0002fa1f]")
NEGATION = re.compile(r"(?:不要|不得|禁止|避免|不能|不允许|不产生|不出现|无)[^，。；\n]{1,36}")
NEGATED_CLAUSE = re.compile(
    r"(?:不要|不得|禁止|避免|不能|不允许|不再|不配|不添加|不加|不急着|不先|不说|尚未|还未|没有|不生成|不出现|无)[^，。；\n]*"
)
QUOTED_DIALOGUE = re.compile(r"(?:台词|说道|说|问|回答|轻声|低声|念|喊)(?:原文)?\s*[：:]?\s*[‘“\"]([^’”\"]+)[’”\"]")


def seconds(token):
    parts = token.split(":")
    if len(parts) > 1 and (token.startswith("-") or any(float(p) >= 60 for p in parts[1:])):
        raise ValueError("invalid clock timestamp")
    value = 0.0
    for part in parts:
        value = value * 60 + float(part)
    return value


def validate(text, duration=None, max_chars=None):
    """Return JSON-compatible measurements and warnings, not a quality score."""
    warnings = []

    def warn(code, message):
        warnings.append({"code": code, "message": message})

    if not text.strip():
        warn("empty_prompt", "正文为空。")
    count = len(text)
    if max_chars is not None and count > max_chars:
        warn("overlength", "Unicode 字符数 %d 超过上限 %d（包含空格与换行）。" % (count, max_chars))
    intervals = []
    normalized = text.replace("：", ":")
    matches = list(INTERVAL.finditer(normalized))
    for match in matches:
        try:
            start, end = seconds(match[1]), seconds(match[2])
        except ValueError:
            warn("invalid_timestamp", "时间格式无效：" + match[0].strip())
            continue
        intervals.append({"start": start, "end": end})
        if start < 0 or end <= start:
            warn("invalid_interval", "区间须非负且终点大于起点：%g–%g。" % (start, end))
    eps = 1e-6
    if intervals:
        if abs(intervals[0]["start"]) > eps:
            warn("start_not_zero", "时间轴未从 0 秒开始。")
        previous = intervals[0]
        for current in intervals[1:]:
            if current["start"] < previous["start"] - eps:
                warn("out_of_order", "时间区间未按起点递增。")
            if current["start"] < previous["end"] - eps:
                warn("overlap", "时间区间重叠。")
            elif current["start"] > previous["end"] + eps:
                warn("gap", "时间区间之间有空缺。")
            previous = current
        if duration is not None:
            if any(i["end"] > duration + eps for i in intervals):
                warn("duration_overrun", "区间终点超过目标时长。")
            if abs(intervals[-1]["end"] - duration) > eps:
                warn("duration_mismatch", "最后终点与目标时长不一致。")
    elif duration is not None:
        warn("timeline_missing", "未发现行首或句段开头的时间区间，请人工核对覆盖。")

    negatives = NEGATION.findall(text)
    repetitions = sorted({n for n in negatives if negatives.count(n) >= 3})
    if repetitions:
        warn("repeated_negative", "同一否定约束重复至少三次：" + "；".join(repetitions))
    if len(negatives) >= 15:
        warn("negative_density", "否定约束较多，请合并为少量针对性限制。")
    positive = NEGATED_CLAUSE.sub("", text)
    silent = bool(re.search(r"完全无声|完全静音|全程静音|全程无声|音轨静音", text))
    voiced = bool(re.search(r"可听(?:见|到)|听见|环境声|呼吸声|脚步声|配乐|台词[：:]", positive)
                  or QUOTED_DIALOGUE.search(positive))
    if silent and voiced:
        warn("sound_conflict", "同时要求完全无声与可听事件/台词。")
    if re.search(r"无对白|无台词|不要对白|不要台词", text) and QUOTED_DIALOGUE.search(positive):
        warn("dialogue_conflict", "同时要求无对白与人物发言，请核对是否引用了未说出口的话。")
    if re.search(r"不要字幕|无字幕|禁止字幕", text) and re.search(r"(?:添加|显示|加入|烧录|配上)(?:日中双语|中日双语|中文|英文)?字幕", positive):
        warn("subtitle_conflict", "同时要求无字幕和添加字幕。")
    if re.search(r"固定机位|机位固定|零位移", positive) and re.search(r"慢推|推近|推进|横移|摇镜|环绕", positive):
        warn("camera_conflict", "固定机位与摄影机移动同时出现，请核对主语。")

    # A clue, not ownership verification: explicit prose still needs human review.
    if re.search(r"递出|递给|递过", positive) and re.search(r"两人|双人|甲|乙|对方", positive):
        markers = [re.search(pattern, positive) for pattern in
                   (r"递出|递给|递过", r"接触|接住|接稳|握稳", r"松开|松手|放开")]
        if not all(markers) or not (markers[0].start() < markers[1].start() < markers[2].start()):
            warn("handoff_check", "请人工确认递出 → 接触握稳 → 原持有者松开，不能瞬间换归属。")

    dialogue = QUOTED_DIALOGUE.findall(text)
    dialogue_chars = sum(len(re.findall(r"[^\s，。！？、；：,.!?;:]", d)) for d in dialogue)
    if duration is not None and dialogue_chars > duration * 5:
        warn("dialogue_budget", "对白约 %d 字，按目标时长估算可能缺少停顿/反应时间；请排练核对。" % dialogue_chars)
    # Also catch a short speaking interval inside a longer scene.
    for index, match in enumerate(matches):
        end_pos = matches[index + 1].start() if index + 1 < len(matches) else len(normalized)
        segment = normalized[match.end():end_pos]
        spoken = QUOTED_DIALOGUE.findall(segment)
        try:
            span = seconds(match[2]) - seconds(match[1])
        except ValueError:
            continue
        words = sum(len(re.findall(r"[^\s，。！？、；：,.!?;:]", d)) for d in spoken)
        if span > 0 and words > span * 5:
            warn("segment_dialogue_budget", "某发言区间约 %g 秒却含 %d 字台词，请增加说话时间。" % (span, words))
    return {"characters": count, "chinese_characters": len(CJK.findall(text)),
            "counting": "Unicode code points including spaces, punctuation and newlines",
            "duration": duration, "max_characters": max_chars, "intervals": intervals,
            "dialogue_characters_estimate": dialogue_chars, "warnings": warnings}


def positive_float(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be finite and positive")
    return number


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="-", help="UTF-8 file, or - for stdin")
    parser.add_argument("--duration", type=positive_float, help="target seconds")
    parser.add_argument("--max-chars", type=positive_int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        # Preserve CRLF: the reported Unicode count must not normalize newlines.
        text = sys.stdin.buffer.read().decode("utf-8") if args.path == "-" else Path(args.path).read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as exc:
        parser.exit(2, "Input error: %s\n" % exc)
    result = validate(text, args.duration, args.max_chars)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("字符：%d；汉字：%d；区间：%d（字符计入换行）" %
              (result["characters"], result["chinese_characters"], len(result["intervals"])))
        for warning in result["warnings"]:
            print("WARNING [%s] %s" % (warning["code"], warning["message"]))
        if not result["warnings"]:
            print("未发现静态检查问题；仍需人工核对表演及语义。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
