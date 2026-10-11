# AIGC character skill · 2.0

**从一句人物剧情到提示词、生成交接和真实视频后期。**

保留1.0的中文表演导演：动机、目光、呼吸、微表情、动作、道具交换、对白与镜头时间轴。新增通用人物视频生产模式，整合《贵妃醉酒》完整MV流程及anime-video-skill的配音、本地视频、连续性和后期经验。

## 这一版有什么

- [通用人物视频产品PRD](docs/PRD-character-video-production.md)与[贵妃醉酒制作PRD](docs/PRD-guifei-mv.md)：brief、母版、参考职责、画布、五幕生成/导入、歌曲、字幕、混音、编码、QA与交付。
- [六套技能统一接入](references/production/integrations.md)：HyperFrames、video-use、Remotion Skills、Generative Media Skills、VideoCut / chengfeng-videocut-skills、专门Seedance2.5技能。完整196个公开模块入口有固定SHA，可按需或全部缓存。
- 可执行本地配音CLI/MCP：VOICEVOX整句自然声线、时长槽位、原始WAV/query/署名/哈希；[说明](references/production/audio-finishing.md)。
- loopback-only ComfyUI CLI/MCP：[本地生成与单镜头验收](references/production/local-video.md)，无付费fallback。
- 参数化FFmpeg后期：定长拼接/CFR、主歌曲或低量自带音轨混合、片头、双语ASS/SRT/确定性烧入、编码后峰值修复、probe/全解码/接触表。
- [从anime迁移了什么](docs/migration-from-anime.md)；原有10场景、12份中文Prompt和离线检查保留。

这是制作与编排skill，**不是独立视频生成模型**。有工具和素材时可真正执行后期/本地适配器；Seedance生成仍由可用UI/API执行，外部模型、账号和运行时需分别准备。未验证的人物运动和试听状态不会写成PASS。

## 安装 / 更新

同名目录不存在时：

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/Simonxz578/aigc-character-skill.git ~/.codex/skills/aigc-character-skill
```

已安装时先保留自己的改动，再 `git pull --ff-only`。自定义CODEX_HOME则安装到对应skills目录。开启新会话后用 `$aigc-character-skill`，也支持按任务自动发现。

仅编写Prompt仍只需Python3.9+，无GPU/API。可执行媒体模块要求Python3.10+及本地FFmpeg/ffprobe：

```bash
cd ~/.codex/skills/aigc-character-skill
python -m pip install -e '.[render]'
python scripts/doctor.py
# 可选MCP包装，SDK是额外依赖：
python -m pip install -e '.[mcp,render]'
aigc-character-mcp
```

MCP以stdio运行，不打印启动横幅。提供 local_voice_health、synthesize_local_voice、local_video_health、submit_local_video、local_video_status；原生声音模型/字典和ComfyUI必须另行准备。Codex配置示例：

```toml
[mcp_servers.aigc_character_media]
command = "/absolute/path/to/your/venv/bin/aigc-character-mcp"
```

## 六套参考能力

```bash
python3 scripts/integrations.py list
python3 scripts/integrations.py sync --family seedance-2-5
python3 scripts/integrations.py resolve --module seedance-2-5
# 一次取得六套全部已登记公开模块资料：
python3 scripts/integrations.py sync --family all
```

缓存保留在本地 `.integrations/sources`，不覆写全局用户skills；只下载固定提交，不执行上游安装器，不调用provider。入口和资料可用不等于CLI/云服务/模型全部运行成功。版本/许可见 [upstream清单](config/upstream-skills.lock.json)与[第三方说明](THIRD_PARTY_NOTICES.md)。

## 直接这样说

> $aigc-character-skill 她听到心上人叫自己的名字，给我一份可复制短词。

> $aigc-character-skill 用我的贵妃母版和舞蹈参考制作60秒MV，720p 9:16。你准备画布，我点击生成；英文歌词在中文上面，原歌曲不变速。

> $aigc-character-skill 五段视频已经生成，按10/10/15/15/10秒合成，片头叠在0–4秒，用原歌曲为主、生成声音低量混入。

> $aigc-character-skill 只修男生不自然的语音，人物、女孩声音、对白内容和画面保留。

> $aigc-character-skill 用HyperFrames做导演参考，或沿用我的Remotion工程加可编辑字幕；不要重新生成角色。

> $aigc-character-skill 本地ComfyUI先做4–6秒递笔记本测试，真正运动和身份通过后才批量；不调用付费API。

## 后期配置与输出

复制 [贵妃配置示例](examples/guifei/production.json)到自己的project目录，按实际文件替换路径，填入基于实际歌曲的字幕并设置有授权的本地字体。相对路径均以配置文件目录为基准。

```bash
aigc-character-finish project/production.json --dry-run
aigc-character-finish project/production.json
```

输出 final.mp4、picture/styled_picture.mp4、mix.wav、ASS/SRT（有字幕时）、render_manifest.json、probe/full-decode日志与接触表。默认不覆盖已有final。用户明确720p优先；新项目未指定时skill建议1080p/30fps。严格ASS直烧用caption_backend=ass；FFmpeg缺少libass时不会伪报成功，auto模式可记录PNG字幕降级。

## 验证与已知边界

```bash
python3 scripts/validate_prompt.py prompt.txt --duration 15 --max-chars 5000 --json
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

1.0历史：44项自动测试、10组/12次独立Prompt试用。2.0新增真实短视频渲染回归、强峰值音轨修复、双语字幕/片头、输入边界与本地provider约束。具体本次结果见 [发布验证](docs/release-validation-v2.md)。

贵妃案例的最终历史文件技术通过；歌词少数专名未逐字试听，混音未完成感知试听。[历史QA摘要](examples/guifei/recorded-qa.json)不证明所有生成模型可运行。本地Wan5B未通过人物动画门槛，14B/LTX2.5未实测；Remotion与VideoCut运行时未因此发布而自动通过。

## 文件与许可

入口 [SKILL.md](SKILL.md)保留快速Prompt与生产路由；导演资料在references，生产资料按需加载；源代码在src/aigc_character_media；配置与示例可以直接复用。

MIT覆盖本库原创与迁移的MIT代码。外部196份skill正文按需从原仓库获取并保留其许可，没有重新发行成MIT。用户歌曲、照片、参考演员视频、成片、模型权重和声纹不随源码发布。VOICEVOX音色署名与Remotion使用条款等独立处理。
