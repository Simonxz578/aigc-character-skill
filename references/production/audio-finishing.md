# 自然配音、歌曲、字幕与确定性后期

## 配音

声音基线记角色id、语言、音色provider/style、自然音域、节奏与署名。VOICEVOX示例来自《雨》v3，使用整句、原生pitch、适度停顿、48kHz转换；男声自然化不靠逐音节拼接或粗暴时间拉伸。config/voice-presets.json只是有据的历史预设，实际local_voice.py使用对应固定实例。其他声音可以按可用provider编写新的preset，但不可把宽泛音色描述写成真人参与或声纹克隆的事实。

局部修声保留未指定角色的音轨、画面与台词。重新合成目标整句，检查时隙和呼吸边界，5–10ms包络只用于避免接点click；不保证所有句子同一长度。不超过槽位才交付；超时保留原件并调整时间轴，不能截尾。

```bash
python -m pip install -e '.[render]'
aigc-character-voice health
aigc-character-voice synthesize --speaker male --text 'こんにちは。' --max-duration 4
```

VOICEVOX0.17 wheel、ONNX runtime、OpenJTalk字典和对应vvm须按官方来源单独准备；默认放outputs/local-voice-provider/runtime，可用VOICEVOX_RUNTIME/VOICEVOX_ONNXRUNTIME指定。见 [VOICEVOX Core](https://github.com/VOICEVOX/voicevox_core)。原生模型许可及音色署名不被本仓库MIT替代。

## 音乐与混音

原歌曲做母本时保持速度和首样本时间。默认audio.mode=replace；只有用户要求才mix_generated。生成声音能含另一首音乐/人声；低量混入不能被说成已完成分轨或调性匹配。有主唱时原曲主导，避免双主唱/双节拍抢占；保留清洁版本可对比。

混到PCM48kHz stereo，边缘短包络，保留stems与实际增益。sample limiter不能替代AAC后解码峰值；再次测量、必要时从PCM重新编码音轨并copy视频。默认最终解码峰值预算-1.5dBFS是工程值，不是dBTP真峰值标准。用户要广播/平台LUFS/dBTP时使用loudnorm/ebur128测量；不要把脚本的sample-peak标成true-peak认证。

## 歌词与字幕

从实际歌曲/对白取得词级识别，保留raw ASR与低置信/专名修改。唱腔可比较本地模型、降调分析副本或已授权转录；不改交付歌曲。若不能试听，写not_verified，不用记忆/搜索来的歌词冒充逐字听验。英文是译文，不用模型生成画面文字。

captions逐条包含start/end/zh/en及review状态，时间不得越出整片。英文在中文上方、中文更大，留出平台安全区；长句分屏或缩字号至可读范围，不切掉文字。输出editable ASS/SRT；有libass时直接确定性烧入，缺失时显式记录Pillow字形板降级，不能报告ASS已直烧。

## 后期命令

```bash
# 按实际本地文件填写examples/guifei/production.json的副本
# 依赖：FFmpeg / ffprobe；需要叠字时Pillow与可用字体
python -m pip install -e '.[render]'
aigc-character-finish project/production.json --dry-run
aigc-character-finish project/production.json
```

相对输入路径以配置文件父目录为准；输出目录也相对该目录。已有成片不默认覆盖。规格和全部音轨策略记录在配置，片头只占既定时间，音轨长度不足则失败而不是静默循环。QA覆盖实际尺寸/fps/帧数/时长、音轨格式、全解码、峰值和接触表；身份/歌词/试听状态另记。
