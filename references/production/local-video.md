# LOCAL_VIDEO_PROVIDER 与诊断

复用anime-video-skill的本地ComfyUI适配器。仅接受loopback HTTP，关闭proxy/redirect，API graph须用已审阅本地节点allowlist；拒绝PaidVideoAPI之类外部节点。不随意增加节点以绕过本地限制。

```bash
LOCAL_COMFYUI_URL=http://127.0.0.1:8188 aigc-character-local-video health
aigc-character-local-video submit --workflow workflow_api.json --save outputs/local-job.json
aigc-character-local-video status --prompt-id ACTUAL_ID
```

ComfyUI必须独立安装/启动，输入位于其input目录，输出位于output；job元数据不等于实际MP4质量。allowlist支持已迁移的Wan节点/GGUF及基础加载/采样/保存；LTX节点未完成此适配器支持与实测，不能声称LTX2.5已可用。

先运行一个4–6秒人物测试，沿用实际母版和初态。双人递物：甲已持物 → 伸手递出 → 乙接触承重 → 甲松手。验收连续人物运动、身份、动作方向、脸和手、MP4编码；细节zoom、光流处理静帧或雨叠层不能让该动作测试通过。

M1Pro16GB的历史Wan5B小样没通过；14B/LTX2.5未实测。CPU/MPS对照须保存同一conditioning/noise，固定seed和参数，然后各自sample、交叉decode和VAE roundtrip。定位失败阶段后再改变一个变量。不要用CUDA显存需求推断统一内存可运行，也不强关OS内存保护。

[迁移历史](../../docs/migration-from-anime.md)记录实测边界。官方参考：[ComfyUI Wan2.2](https://docs.comfy.org/tutorials/video/wan/wan2_2)、[LTX-2](https://github.com/Lightricks/LTX-2)。昂贵权重和采样不为文档发布重复运行，资料安装不代表模型验收。
