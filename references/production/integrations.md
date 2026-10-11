# 六套视频技能的统一接入

入口按需调用外部skill正文和它引用的文件。完整固定提交清单 config/upstream-skills.lock.json 覆盖196个公开模块，下载源码不代表运行时安装，更不代表生成验收。

| family参数 | 上游 | 用途与常用入口 |
|---|---|---|
| hyperframes | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | hyperframes入口、core/CLI/animation/audio、general-video、media-use、music-to-video、标题/字幕/导演时间轴 |
| video-use | [browser-use/video-use](https://github.com/browser-use/video-use) | 视频转录、剪辑、调色、overlay、项目记忆；用户既有剪辑授权无需再确认策略 |
| remotion | [remotion-dev/skills](https://github.com/remotion-dev/skills) | best-practices、create/markup/render/captions/multimedia、studio/interactivity；React帧驱动包装与剪辑 |
| generative-media | [calesthio/generative-media-skills](https://github.com/calesthio/generative-media-skills) | performance/character/cinematic/storyboard、MV/anime、配音音乐拟音、后期/VFX/FFmpeg、QA与可选provider |
| videocut | [Agentchengfeng/chengfeng-videocut-skills](https://github.com/Agentchengfeng/chengfeng-videocut-skills) | chengfeng-cut/subtitle/visual/export/workbench；口播账本和Studio复核，非MV默认流程 |
| seedance-2-5 | [Standed/Seedance2.5](https://github.com/Standed/Seedance2.5) | 真实2.5 brief/镜头包/参考职责/连续性/修复方法，活跃界面决定参数 |

## 使用

```bash
python3 scripts/integrations.py list --family generative-media
python3 scripts/integrations.py sync --family hyperframes
python3 scripts/integrations.py sync --family seedance-2-5
python3 scripts/integrations.py resolve --module seedance-2-5
# 用户明确需要全部参考资料时：
python3 scripts/integrations.py sync --family all
```

sync只将固定SHA源码缓存到本skill的 .integrations/sources；不运行package脚本、不装权重、不改变全局已装skills、不配置账号。返回available后读取真实entrypoint及相对引用。如果用户已有模块可直接读已安装入口，并记录其版本与本清单的差别。现有不匹配缓存不会被覆盖。

## 运行时与适用边界

- HyperFrames需要其CLI、Node、浏览器与FFmpeg；采用seekable deterministic时间轴，不以实时setInterval生成渲染状态。接入方法不表示每个扩展模块都试跑过。默认选择本地可用路径，尊重用户不允许付费fallback的设置。
- Remotion是独立React运行时，核实当前使用条款与依赖。源技能许可未由仓库API识别，不将其正文当作本库MIT文件重新发行。
- video-use中的云Scribe或TTS是示例依赖；无云授权时用已有本地转录，保留词级和置信信息。已确定的歌曲MV不要求进行口播筛词。
- VideoCut的四段业务边界是账本、字幕、画面、导出；工作台/CLI需要单独doctor，历史版本有Runtime兼容失败记录。
- Generative Media的provider文档是可选能力导航。平台未连接、模型未下载、额度不明时记录状态；不要因为资料存在就调用付费服务。
- Seedance2.5技能写计划与提示词；通过实际UI/API操作才算生成。中文2.0多参考写法可借方法，数值/功能需要替换为当前2.5事实。

外部正文保留自己的许可与调用条件；用户要求和系统工具权限优先。相关来源与迁移见 THIRD_PARTY_NOTICES.md。
