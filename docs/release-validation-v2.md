# v2.0.0 发布验证

日期：2026-10-11。完整结果见 [JSON](release-validation-v2.json)。

## 本次实际执行

- 新的隔离安装环境成功 `pip install -e .[mcp,render]`，console CLI可启动。
- **50项自动测试PASS**：保留44项1.0 Prompt/示例/引用回归；增加voice/video输入边界、真实FFmpeg拼接、24→30fps、定长帧数、双语片头字幕、源不足拒绝、强峰值PCM→AAC修复和stdio MCP回归。
- FFmpeg真实短片结果2.000秒、160×288、30fps、60帧；全片解码成功。高于预算的源音轨触发增益回退，最终解码峰值在配置-3dBFS内。样本规模小，不能据此声称所有格式/素材已经验证。
- 专门MCP客户端完成initialize、list_tools、voice health调用；五个工具名称核对，PaidVideoAPI节点被拒绝，未提交生成。
- 使用现有VOICEVOX0.17本地运行时，迁移后的男声接口真实生成0.683125秒、48kHz stereo WAV；未变速，试听验收false。WAV及完整query不发布。
- 六个固定上游checkout成功，196条指定公开SKILL入口全部存在：HyperFrames21、video-use1、Remotion12、Generative Media153、VideoCut8、Seedance2.5 1。相对目录结构保留；没有执行上游安装器或开通provider。
- skill-creator frontmatter验证通过；本地Markdown引用检查通过；发布源码检查剔除媒体、模型、缓存、测试运行时与个人路径。

## 本次发现并修复

隔离安装首次解析到MCP2.3，FastMCP模块已被删除。可选SDK依赖因此固定为 `mcp>=1.0,<2`，重新安装MCP1.30并通过stdio测试。没有声称兼容未经迁移的2.x接口。

## 未验证与历史证据

没有重新运行昂贵人物模型、Seedance云生成、Remotion/HyperFrames/VideoCut的全部运行时，也没有逐个调用Generative Media的provider。196入口可读不等于196种服务可运行。

贵妃60秒技术证据来自既有制作，见 [历史QA](../examples/guifei/recorded-qa.json)；唱词专名和感知混音没有人工逐字试听通过。Wan5B人物动作门槛未过、14B/LTX2.5未测，保留原结论。2.0没有另做独立Agent自然语言前向评测；1.0的历史forward记录不冒充2.0新结果。
