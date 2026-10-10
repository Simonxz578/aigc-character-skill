# AIGC character skill

**说一句人物剧情，得到一份可复制的中文表演 Prompt。**

把“她有些委屈”写成有动机的目光、呼吸和动作，把双人互动写成有因果的回应。适合古风、写实、日漫、对话、歌舞与战斗提示词。

这是 Agent 的**文字角色导演 skill**，不是视频生成模型。它不生成 mp4，不下载权重，也不调用付费 API。最终正文可交给小云雀、Seedance、Kling、Veo、Sora 等平台；实际型号与生成能力需在制作时核实。

## 安装到 Codex

需要 Git 和支持本地 skills 的 Codex。确认同名目录不存在后：

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/Simonxz578/aigc-character-skill.git ~/.codex/skills/aigc-character-skill
```

重新启动/开启新的 Codex 会话，使 skill 被发现；随后用 `$aigc-character-skill` 显式调用，也支持根据描述自动选择。如果已经安装，先检查本地改动，再在安装目录运行 `git pull --ff-only`。自定义 CODEX_HOME 时用该目录下的 `skills/` 替代上述位置。

## 直接这样说

**最短调用**

> $aigc-character-skill 她听到心上人叫自己的名字，给我一份能直接复制的短词。

**详细表演**

> $aigc-character-skill 15秒，古风女子发现友人替她留了回乡船位，但他不能同行。cinematic，含泪不落，不说话。

**双人场景**

> $aigc-character-skill 12秒，湊把捡到的笔记本还给夏帆，化解误会。沿用我上传的男女母版，无字幕。

**局部改写**

> $aigc-character-skill 只把下面男生的语气改自然，人物、衣服、女孩台词、镜头和其他句子都保留：……

默认交付 prompt_only 中文正文，不要求填表。standard 通常450–900汉字；concise 180–350；明确要细描才用 cinematic 1100–1700。custom 按字符上限核算，包含空格、标点与换行。七种形式还包含时间轴、对白表演、双人、角色基线、局部修订和 QA。

## 例子

> 8秒写实中近景，女子坐在桌边，对方在右侧画外。0–3秒：解释被打断后，她把抬起的手放回膝上，视线落到空杯，嘴角的礼貌笑渐淡。3–6秒：她抬眼确认对方仍未听，嘴唇轻合，把话留住，肩线保持平稳。6–8秒：完整呼气后重新看向对方，留出继续谈话的余地。镜头固定，无新增台词、字幕或落泪，环境声保持自然。

[10份原创场景 / 12份正文](examples/01-ancient-joy-to-regret.md)，包括两份1200–1700汉字的15秒演示与[同一需求三档长度](examples/04-shy-romance.md)。完整目录位于 `examples/`。

## 离线检查

Python 3.9+，仅标准库，无需 pip install：

```bash
python3 scripts/validate_prompt.py prompt.txt --duration 15 --max-chars 5000
python3 scripts/validate_prompt.py prompt.txt --duration 15 --json
python3 -m unittest discover -s tests -v
```

输入是 UTF-8 正文；`-` 或不提供路径时读取 stdin。Unicode 字符数计入换行。检查时序覆盖、重叠、字数、重复否定、部分声音/字幕/镜头冲突、对白粗预算和递物链提示。语义 warnings 退出0，输入或参数错误退出2。无 warning 不代表真实视频必定成功；启发式检查可能误报或漏报。

## 文件与验证

v1.0.0本地验收：**44项自动测试 PASS**，skill-creator frontmatter检查通过；完成10组、12次独立自然语言试用。参考未输入的用例只验证文字行为，未验证实际角色相似度；朗诵超时用例验证的是冲突处理。

- [SKILL.md](SKILL.md)：入口、推断、路由、生成与自查。
- `agents/openai.yaml`：展示名称与默认调用。
- `references/`：9份按需读取的导演资料，情绪索引44项。
- `examples/`：10个独立原创场景，包括三档对比。
- `scripts/`、`tests/`：可执行检查器、自动测试与[自然语言回归记录](tests/forward-results.md)。

使用MIT许可，覆盖本仓库原创文字与代码。仓库不包含用户原截图、逐字转写、照片、视频或声纹素材。结构参考 [Agent Skills 规范](https://agentskills.io/specification) 与 [OpenAI Skills 文档](https://developers.openai.com/plugins/build/skills)，开发使用 skill-creator 指导；不复制外部示例正文。

字幕、精确书写文字及原音轨保留应交给确定性后期。已有视频像素级局部修复需要跟踪/遮罩/合成工具，本 skill 不承诺通过文字指令保证这些结果。
