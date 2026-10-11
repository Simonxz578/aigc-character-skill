# 从 anime-video-skill 迁移的人物制作能力

源：[Simonxz578/anime-video-skill](https://github.com/Simonxz578/anime-video-skill)，commit 788d014，0.3.0。原MIT代码与出处保留；结构化记录在 config/migration-provenance.json。

## 实际代码

- local_voice.py：VOICEVOX0.17整句合成、native pitch、停顿上限、48kHz转换、5ms包络、长度槽位检查、原始WAV/query/credit/hash留档。预设是《雨》的历史可用实例，不要求其他角色采用男女二分或日语。
- local_video.py：ComfyUI loopback-only提交、查询，校验API graph与本地节点allowlist，禁止云redirect；作业返回仍标NOT_EVALUATED。
- io.py：原代码所需的稳定JSON/路径辅助。
- 定长片头、确定性字幕、接触表、probe、全解码、PCM/编码音轨检查迁移为新的参数化finishing.py，消除写死《雨》图片/绝对路径的依赖。

## 保留的方法

读取角色/服装/空间/道具状态；对白line_id对应声音和字幕；只修男声时保留女声；自然voice修复用整句、原音高，避免按音节拼接和硬拉伸。HyperFrames导演参考可交给生成平台，但应称animatic而非真实人体动画。

本地Wan5B在M1Pro16GB的已录CPU/MPS短测试都出现损坏画面；同latents交叉解码差异低而参考VAE roundtrip可识别，提示问题位于解码前，但没有定位最终缺陷。14B首尾帧和LTX2.5未实测。该失败不会变成“所有Apple设备不支持”的结论。短镜头真正运动验收尚未通过；不自动批量生产。

保留固定提交的历史技能清单 config/anime-validated-skills.lock.json，同时另有当前完整公开模块清单。旧Remotion未实际运行、VideoCut Runtime不兼容等事实不因文档合并改成通过。

## 不作为通用默认项

夜空知识来源研究、固定《雨》剧情、蓝白配色、夏帆/湊脸、120秒固定时长、日本语言、72BPM音乐motif、模型权重和歌曲都不是通用人物技能的默认项。特定作品的去重不能禁止其他项目有意回忆/重复动作；记录复用意图再判断。
