# PRD：通用 AI 人物视频制作 Skill

版本：2.0.0 · 日期：2026-10-11 · 产品入口：aigc-character-skill

## 1. 用户与问题

面向使用 Agent 制作角色短片、短剧、歌舞 MV、动漫混剪和口播人物视频的创作者。痛点是角色漂移、参考关系错误、动作/运镜描述不可演、跨镜头重置状态、音轨冲突、字幕乱码、规格错误，以及将“提示词已写好”误报为“视频已完成”。产品把一句创意或已有素材推进到真实、可复核的交付文件，同时保留快速提示词入口。

## 2. 产品目标

- 一个角色导演入口贯通 brief → 母版 → 分镜 → 生成/导入 → 声音 → 字幕/包装 → 编码 → QA → 交付。
- 已有好镜头优先复用；局部修复只更换目标部位、台词或音轨。
- 将六套外部技能按任务接入，记录固定提交；按需阅读，不把所有工具作为每条视频的必经步骤。
- 区分生成动画、插画 animatic、镜头混剪、提示词方案及尚未运行的 provider。

## 3. 范围与模式

| 模式 | 输入 | 输出 | 执行条件 |
|---|---|---|---|
| Prompt | 一句剧情/旧提示词 | 中文正文或表演时间轴 | 无生成依赖 |
| Production | brief、母版、时长规格 | timeline、提示词包、素材清单、实际媒体 | 对应生成/编辑工具可用 |
| Finish | 已有视频和音轨 | MP4、ASS/SRT、命令记录和 QA | FFmpeg；PNG字幕降级需要Pillow和字体 |
| Repair | 已有文件、局部改动目标 | 修复文件与前后证据 | 追踪/遮罩、配音或合成工具按任务选择 |
| Pilot | 本地模型工作流和参考 | 单镜头MP4、运动验收、诊断 | 模型/节点/内存真实可用 |

模型服务、UI账号、声音模型、字体和模型权重是可选外部依赖。Skill 不提供虚构的万能视频生成器，也不自动开通付费 provider。用户已经选定模式和提交范围时，沿用授权，不重复开需求访谈。

## 4. 默认与显式规格

通用新项目默认竖屏1080×1920、30fps、H.264/yuv420p/AAC；源文件局部修复默认保留原规格。用户明确的720p、横屏、帧率和时长优先。记录 native_generation_spec 和 delivery_spec，升采样不叫原生高分辨率；CFR重复采样不叫人体运动生成。

时间轴以整数帧为可执行母本。固定总时长的视频不能额外增加片头，也不能无记录地使用转场重叠缩短长度。对白可溢出的槽位须修改时间轴或经授权调整文本；不截断音节。

## 5. 用户故事

- 只想复制提示词的用户直接得到中文表演正文。
- 有人物母版的创作者得到锁定脸、发型、妆发、衣服、道具的镜头包。
- 已在小云雀生成五段视频的用户得到统一帧率、主歌曲、字幕和署名的完整MV。
- 需要修男声的用户保留女声和画面，仅重合成有问题的整句并对齐时隙。
- 本地设备有限的用户先得到短镜头真实运动试验；测试不合格时不会自动批量烧资源。
- 已同意混剪的用户可收到明确标注的animatic/混剪，不冒充模型生成连续人体动画。

## 6. 功能需求

| ID | 要求 | 实现/资源 |
|---|---|---|
| F01 | brief记录需求、硬约束、禁止改动、音轨与生成提交权限 | production/workflow |
| F02 | 角色母版与参考职责分离；动作参考不接管身份/服装 | character references + role map |
| F03 | 每镜头起态、事件、终态、屏幕方向、道具持有者 | shot ledger |
| F04 | 机位、表演、台词和参考 token 编译为平台提示词 | 原导演流程 + Seedance2.5集成 |
| F05 | 当前UI/API事实核实，提交/查询/取回与验收分开 | generation receipt |
| F06 | 本地整句配音、自然音高、停顿修整、音色署名 | local_voice.py |
| F07 | loopback-only本地ComfyUI接口，无云fallback | local_video.py |
| F08 | 素材probe、定长裁剪、统一CFR、确定性合成 | finishing.py |
| F09 | 替换音轨或按明确要求低量混入生成音轨，PCM母版与编码后峰值检查 | finishing audio modes |
| F10 | 实际音频转录、词级时间、修订日志；英文在中文上方 | ASS/SRT + reviewed captions |
| F11 | 片头/包装、HyperFrames/Remotion可重复渲染 | integration routes |
| F12 | 编码帧数、时长、全解码、音轨状态、抽帧、连续性和试听状态 | QA manifest |
| F13 | 从阶段断点继续，失败只重做受影响步骤 | project state + immutable inputs |

## 7. 技能编排

- HyperFrames：HTML/CSS/GSAP、导演母版、片头、包装、音频时间轴和MP4；运行前读其入口及对应核心/CLI模块。
- video-use：已有视频的转录、剪辑、调色、overlay和项目记忆；不用其云端示例替换本项目的本地约束。
- Remotion Skills：React/帧驱动时间线、字幕、可交互预览和渲染；许可与运行时独立于本仓库。
- Generative Media Skills：角色/表演/镜头/灯光/美术连续性、音乐/拟音/配音、MV/动漫、后期合成、媒体QA与可选provider。
- VideoCut / chengfeng-videocut-skills：口播删词账本、字幕复核、HTML画面层、最终导出；MV不走口播删词账本。
- seedance2.5-skill：专门2.5生产brief、镜头、参考关系、连续性和失败修复；可用界面决定真实参数。

完整196条公开模块入口在 [固定清单](../config/upstream-skills.lock.json)，不是196个运行时通过验收。源码在需要时缓存，不将未知许可资料重新发行成MIT。

## 8. 数据契约

production.json包含 spec、shots、audio、title、captions、fonts、caption_backend、output_dir 与 review。角色生成项目还应保留 assets/role_map、shots/opening/ending_state、dialogue/line_id、provider/job_id/model/seed、continuity、stage和change_log。

最低文件结构：inputs（原件及哈希）、prompts、generation_receipts、audio/stems、subtitles、renders、qa、project.md、render_manifest.json。生成输出和缓存不进入Git。参考图、歌曲和成片不是这个PRD仓库的代码资产。

## 9. 阶段与状态

brief_locked → assets_ready → prompt_ready → generation_submitted → clips_received → picture_locked → audio_ready → captions_reviewed → rendered → technical_qa_pass。

perceptual_review是独立对象：identity、motion、lyrics、listening分别为 pass / fail / not_verified；技术PASS不自动推进为全部感知通过。用户亲自点生成时，job提交归属记为user，不记为Agent调用。

## 10. 失败处理

- 手递物/舞蹈/变脸问题：优先修单镜头或参考职责；仍无效时明确失败。按用户允许才采用混剪。
- CPU/MPS故障：固定输入、噪声、seed、采样参数，分别采样与交叉解码；区分采样失败与VAE解码失败。
- ASR不稳定：针对实际音轨比较模型或降调分析副本；原音轨不变。低置信词保留复核清单，不能靠记忆歌词宣称逐字听验。
- 没有libass：提供可编辑ASS并显式记录PNG确定性字形烧入降级；用户要求严格libass时先获取合适FFmpeg。
- AAC峰值超过预算：从PCM重新编码音轨并stream-copy画面，按测量降低总线；不逐次重编码视频。
- 上游缺失/运行时不兼容：保留已完成成果和依赖状态；不要宣称“安装全部=所有生成模型可运行”。

## 11. 质量门槛

| 门槛 | 验收 | 不等价的证据 |
|---|---|---|
| 角色运动 | 连续帧/播放中人物真正运动、身份稳定、动作方向正确 | zoom/pan、雨层、提交成功 |
| 音轨 | 主音轨正确、无变速/移位、边界无爆音、编码后余量、试听自然 | WAV存在、相关性或峰值单独通过 |
| 字幕 | 字词、时间、译文、换行、安全区、实际编码截图 | ASR文本存在 |
| 技术 | 实际尺寸/fps/帧数/时长、音频参数、全片解码 | 命令中设置目标参数 |
| 交付 | 可播放MP4、可编辑字幕、QA和原件出处 | 仅给链接名称或假称导出 |

通用脚本确认的是技术/输入契约；身份、观众体验与唱词必须如实记为Agent观测、人工试听或未验证。

## 12. 非功能与可恢复性

脚本无硬编码用户目录、歌曲词和角色脸。CLI参数及配置版本化；FFmpeg命令、probe与哈希留档。保留原始24fps等源文件；音轨-only修复用视频stream-copy；字幕已烧入后不做新构图覆盖。缓存不运行仓库install脚本，现有用户缓存不覆盖。批量成本、重试与生成提交范围沿用用户约束。

## 13. MVP / 2.0发布验收

保留1.0提示词回归；新增媒体契约和真实小样渲染验证；六套清单可解析且路径固定；验证本地voice/video适配器输入边界；贵妃制作案例脱敏；发布源代码zip和版本tag。外部运行时全覆盖、全自动云生成、自动评定观众喜欢程度不属于本次已验证能力。

## 14. 案例

[《贵妃醉酒》PRD与制作复盘](PRD-guifei-mv.md)提供实际五镜头、参考关系、音乐变更、字幕降级和AAC峰值故障；[anime迁移清单](migration-from-anime.md)保留《雨》的配音/本地生成历史证据，不把特定人物预设作为所有项目的默认角色。
