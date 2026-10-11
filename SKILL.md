---
name: aigc-character-skill
description: 编写中文人物表演提示词，制作或修订以角色为核心的AI视频、短剧和MV。按需求调用角色连续性、Seedance 2.5、多镜头生产、本地配音与ComfyUI、HyperFrames、Remotion和确定性剪辑字幕质检；已有素材可直接完成MP4后期。
license: MIT
metadata:
  version: "2.0.0"
  language: "zh-CN"
---

# AIGC character skill

把人物的目标、克制与选择写成可以看见、可以演出的动作。只要提示词时，直接交付可复制正文；明确要求制作、改片或合成时，继续到可检查的媒体交付。实际执行取决于可用工具与用户授权。

## 工作模式

| 请求 | 执行入口 |
|---|---|
| 写或局部改提示词 | 下文原有导演流程；不顺带生成视频 |
| AI人物短片、短剧、MV | [生产流程](references/production/workflow.md)，建立角色母版与逐镜头状态 |
| 用小云雀/Seedance 2.5生成或准备画布 | [Seedance 2.5](references/production/seedance-2-5.md)，核实当前界面、参考关系与提交权限 |
| 拼接已有镜头、配音、修声、加字幕 | [声音与后期](references/production/audio-finishing.md)，优先保留已认可的媒体 |
| HTML/GSAP动画或React视频 | [六套集成](references/production/integrations.md)，选择HyperFrames或Remotion运行时 |
| 本地人物连续运动试验 | [本地生成](references/production/local-video.md)，先通过一个短镜头，再按用户要求批量 |
| 需要通用产品/项目规格 | [人物视频PRD](docs/PRD-character-video-production.md)；实作参考[贵妃醉酒案例](docs/PRD-guifei-mv.md) |

六套能力的固定提交和全部公开模块在 `config/upstream-skills.lock.json`。运行 `python3 scripts/integrations.py resolve --module NAME` 找到已缓存入口；缺失时按需要 `sync --family FAMILY`。安装器只获取方法资料，不启用外部付费服务或安装生成模型。按当前需求读相应模块和引用；不一次加载196份正文。用户既有策略与授权优先，不因上游示例重新要求确认已确定的剪辑方案。

## 输入与范围

接受口语剧情，不要求 JSON。提取人物与关系、目标和潜台词、情绪起转终、性格与控制习惯、年龄/时代/画风/服装、台词原文及语言、动作强度、参考与连续性、时长/画幅/目标平台、禁止项。

缺少非关键项时作节制的默认选择：短小情绪需求通常 10 秒、standard、无对白；不主动加哭泣、亲吻、告白、暴力或换装。若用户只要短词，采用 concise。只有无法合理推断的关键事实才问一项；未提供的参考图不可声称已经分析。引用参考时锁定已知身份、服装、发型、初始姿态和空间关系，再让动作正常发展。

若要求修改旧词，先确定改动范围，保留其他段落与台词原文，尽量逐字保留无关内容。若局部修改导致时间矛盾，仅修正必要关联并简述原因（prompt_only 除外）。请求真实视频时使用生产模式，区分准备完成、生成已提交、文件已返回和验收通过；没有实际文件不能声称已渲染。

## 按需读取

| 情况 | 资源 |
|---|---|
| 推断人格、场景、复合情绪 | [character-taxonomy](references/character-taxonomy.md) |
| 情绪分段、克制与反转 | [emotional-arcs](references/emotional-arcs.md) |
| 眼眉唇颌、呼吸与可见尺度 | [facial-acting](references/facial-acting.md) |
| 道具交换、身体发力、歌舞或战斗 | [body-acting](references/body-acting.md) |
| 机位、轴线、焦点与光 | [cinematography](references/cinematography.md) |
| 台词、口型、语言、字幕和声音 | [dialogue-and-sound](references/dialogue-and-sound.md) |
| 指定平台或原视频局部编辑 | [platform-profiles](references/platform-profiles.md) |
| 长短档与七种交付形式 | [prompt-patterns](references/prompt-patterns.md) |
| 审稿或明显生成风险 | [quality-rubric](references/quality-rubric.md) |

按需选择 1–3 份，复杂双人战斗再追加，不全量加载。需要长演示时读 [古风释怀](examples/01-ancient-joy-to-regret.md) 或 [隐忍失落](examples/02-silent-crying.md)；三档比较见 [叫名字](examples/04-shy-romance.md)。示例提供结构启发，换剧情时重新建立动机，不套用原句。

## 导演步骤

1. 内部概括“想得到什么、为何不能直说”，分别定义内心压力、外显幅度和自我控制；必要时用 0–5 内部标度，默认不显示数字。
2. 确定起始注视点、姿态与习惯动作，以及实际触发事件。性格决定调节方式，不由性别决定。
3. 安排因果递进：察觉、反应、抑制、泄露、选择、余味；只用剧情需要的节点。每个节点选 2–4 个有效可见动作，不让眼眉鼻唇和双手同时表演。
4. 动作写清方向、起点与终点；目光可先于转头，伸手有肩臂先导，双人递物必须是 A 伸出 → B 接触并握稳 → A 松开。反应由对手上一动作触发。
5. 景别决定细节：远景写重心与路径，近景写目光、唇线与呼吸；二维角色写线条/姿态，避免真人毛孔要求。摄影与环境回应表演，不替代人物动作。
6. 标注连续的秒区间，从 0 到目标时长、无重叠无空缺。≤5 秒一个触发加反应；6–10 秒 2–4 节拍；15 秒通常 4–7 节拍；20–30 秒可加覆盖；≥60 秒先规划再逐镜头写，不承诺单次生成任意长度。
7. 保留台词逐字内容并预算说话、停顿和反应时间。太长就指出超时并给延时/分镜方案，不擅自删词或把朗诵硬塞进去。明确无对白、无声、无字幕是三个不同条件。
8. 自查可演性、情绪因果、微表情精度、连续性、摄影/物理、中文六项；每项内部评分 1–5，低于 4 的明确问题最多修订一次。自评不能证明生成视频一定成功。

只保留少量针对性限制。不用瞳孔随悲伤缩放、睫毛摩擦声或每秒多次情绪反转。含泪不等于泪水必然消失，结束时保留合理余态。

## 输出选择

- **prompt_only（默认）**：一份自然中文可复制正文，不加代码围栏、分析或 QA。
- **cinematic_timeline**：人物/空间锚点、分秒动作与有理由的镜头变化。
- **dialogue_performance**：台词原文、发言时段、注视对象、语气和呼吸，不用微表情妨碍口型。
- **dual_character**：各自所知与目标、屏幕方向、相互触发、道具归属链。
- **character_sheet**：基线、习惯、控制策略、身份与服装锚点；不强加时长。
- **refine_existing**：只修改被点名维度，不附带重做场景、镜头或音轨。
- **qa_report**：短列实质问题与具体修改建议；有需求才给重写稿。

长度按汉字估计：concise 180–350，standard 450–900（默认），cinematic 1100–1700（明确要求细描时）。不是越长越好；对白密集或简单动作不强行凑长度。custom 按用户上限计算 **Unicode 字符，包括空格、标点与换行**；先压缩次要说明，不截断台词或身份锚点。机器 JSON 只在用户或下游确实需要时给。

可选离线自查：将最终正文保存为 UTF-8 文件，运行 `python3 scripts/validate_prompt.py prompt.txt --duration 15 --max-chars 5000`。脚本只做启发式静态检查，不能替代导演判断；语义 warnings 不导致非零退出。Markdown 示例的正文在 `text` 围栏中，须先提取，不能把示例说明一起当 Prompt 校验。

## 微型例子

- “她有些委屈” → 对方略过她的解释后，她把将要抬起的手放回膝上，视线短暂落向空杯，再回到对方脸上；嘴角不再维持礼貌弧度，仍平稳说话。不自动安排泪流满面。
- “两个人递笔记本” → 甲先托住书脊向乙递出，乙目光落到封面，双手接触并承担重量，甲才松开；各自身体始终在原来的画面一侧。
- “只修男生语气，其他别改” → 保留人物、服装、动作、镜头和女孩台词；仅调整男生的发声节奏、停顿、尾音及必要的口型提示。
