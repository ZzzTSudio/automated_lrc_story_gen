# M401 前期分镜包验收记录

## 已完成

- 详细扩写故事、人物动机、六段剧情、对白定稿、声音与剪辑设计。
- 36 个连续镜号 S01—S36，单镜 6—10 秒，总和 **300 秒 / 05:00**；最后4秒片名计入最后一镜。
- **40 张 PNG**：角色设定2张、场景锚点2张、逐镜首帧36张。全部可解码、非空。原始宽度为1670/1671/1672像素，高度均为941像素。14张图片尚需1—2像素的尺寸统一，严格尺寸校验未通过，等待本地尺寸处理授权；没有将尺寸差异掩盖为PASS。
- 36 条最终视频提示词按镜号集中于 `video-prompts.txt`；每个非空行对应一镜，一对方括号内合并场景、角色、镜头、动作，四字段各出现一次。对白已合入动作。
- 已在生成结果中逐张查看首帧；修正实验室误入台灯、背景复制主角、窗缝构图、完整便笺、纸船、记录本外形、清晨碎纸及窗帘提前打开等问题。
- 角色位置以实际首帧回填；部分原定手部特写生成了躯干/背景同学，分镜书和最终提示词已相应标注，没有虚称画面无人。
- 技能基础校验通过；实际导出保持提示词原文；缺失提示词、意外换行、时长不符、重复镜号的异常用例均被拒绝。
- Markdown图片引用可解析；最终图片均保存在工程内，不依赖默认生成目录。PNG逐文件尺寸、字节数和SHA256记录见 `production/asset-audit.json`。

## 定点修订与保留边界

所有图片通过内置 imagegen 生成。正式交付使用最终版本；本次9次定点视觉修订分别覆盖S08、S19、S05、S15、S26、S27、S29、S35、S36。未出现需更换生成服务的网络失败。

本包是一次完整视觉前期试作，未生成图生视频、口型、对白音轨或最终剪辑；300秒是设计片长，不是成片时长实测。现有四个WAV没有被试听、选择、剪辑或覆盖。

生成首帧仍可能存在细小的文具材质、书本厚度、背景同学姿态和杯子位置变化；不能把这些独立首帧视为已验证的连续实拍素材。正式生成视频时应逐镜沿用本包首帧并检查人物漂移、手指、便笺物理、灯开关、箱轮和口型，必要时做相邻镜头衔接修订。文字合成和片名仍属于明确的后期任务。

原M401故事、歌词和WAV文件保持不变；新增内容全部在 `storyboard_book`，全局技能改动有before/after副本与diff。

## 脚本输出

```text
ERROR: frame dimensions are inconsistent: [(1670, 941), (1671, 941), (1672, 941)]
FAIL: 1 error(s), 36 shot(s), duration=300.0

WROTE E:\Project\zzzt-aimm-project\aimusic\outputs\M401-窗帘后面的灯\storyboard_book\video-prompts.txt (36 prompts)
WROTE E:\Project\zzzt-aimm-project\aimusic\outputs\M401-窗帘后面的灯\storyboard_book\storyboard-book.md (36 shots)
WROTE offline gallery: 36 shots, 300 seconds
PASS rejection: missing_prompt
PASS rejection: multiline_prompt
PASS rejection: timing_mismatch
PASS rejection: duplicate_id
PASS: valid manifest, exact prompt export, book inclusion, 4 invalid-input cases
PASS: 40 readable PNG assets, 36 exported prompts, valid Markdown image links
```

## 图文页检查

浏览器安全策略拒绝file URL，未绕过此限制，也未声称完成浏览器交互验收。HTML图片与下载链接使用工程内相对路径，已做静态文件存在性检查。筛选与复制按钮保留实现，实际交互须由用户打开页面后确认。
