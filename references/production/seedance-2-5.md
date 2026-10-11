# Seedance 2.5 与画布生产

主要外部技能：[Standed/Seedance2.5](https://github.com/Standed/Seedance2.5)，安装解析名seedance-2-5。它是独立社区制作技能，不是ByteDance官方运行时或自动API。旧dexhunter/seedance2-skill只作为2.0历史参考，不能重命名成2.5。

读取该入口与对应production-contract / route-templates / prompt-patterns。模式包含单镜头、跨镜头剧情、短视频、产品、talking-head B-roll与局部修复。按所用小云雀/即梦/其他UI分别核实模型、时长、720p/其他分辨率、画幅、首尾帧、音轨引用和费用。

官方产品介绍见 [ByteDance Seed 2.5说明](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)。其中的通用能力不能直接当作所有UI或API参数。不要编造2.5 endpoint/model_id；只有实际工具执行/文件返回后才报告生成完成。

参考角色职责先写role_map，再绑定画布关系。若UI使用@引用，保留真正节点/附件token，不自己猜。人物母版锁身份与衣服，动作参考锁动作和运镜；只带动作时排除脸、衣服、界面和文字。每幕起止姿态、主动作、运镜和光线能连续落地即可，不堆多个相互冲突事件。

用户让Agent配置后自己生成：完成所有节点与关系、模型与画幅/时长显示，留就绪截图，停止在生成按钮之前。用户授权提交：保存job/状态与次数。查不到可用入口时仍交付提示词包，不假装已调用Seedance。

已经成功的镜头局部修复：指定唯一master video、目标、允许修改区域/声音及其余保持项；优先编辑或后期合成，不重做全片。所有可选付费API只在用户明确选择并具备可用访问条件时使用，不作为无提示fallback。
