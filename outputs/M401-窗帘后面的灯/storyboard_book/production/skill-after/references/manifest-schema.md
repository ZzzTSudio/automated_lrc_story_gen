# 分镜清单与交付格式

仅在需要生成JSON清单、Markdown分镜书或使用脚本验收时读取本文件。

## 推荐JSON结构

```json
{
  "project": {
    "title": "片名",
    "final_prompt_format": "scene-character-camera-action-v1",
    "total_duration_seconds": 360,
    "preferred_min_shot_seconds": 5,
    "max_shot_seconds": 10,
    "aspect_ratio": "16:9",
    "frame_size": "1672x941",
    "style": "高清写实都市悬疑剧"
  },
  "global_constraints": ["人物身份稳定", "禁止可读生成文字", "禁止水印"],
  "characters": [
    {
      "name": "林晚",
      "description": "28岁，低盘发，象牙白婚纱",
      "image": "characters/lin-wan-character-sheet.png"
    }
  ],
  "shots": [
    {
      "id": "S01",
      "duration": 8,
      "scene": "婚礼厅",
      "characters": ["林晚", "顾沉舟"],
      "shot": "特写，85mm微距",
      "visual": "男主将婚戒推入女主指尖",
      "motion": "缓慢推近婚戒",
      "dialogue": "司仪：你是否愿意——",
      "post_notes": "无文字合成",
      "image": "frames/S01.png",
      "generation_prompt": "可选：仅描述动作发生前静态画面的内部首帧提示",
      "video_prompt": "[场景：婚礼厅，暖光照亮两人。角色：林晚（图中左侧的人）、顾沉舟（图中右侧的人）。镜头：双人中景，40mm镜头，大景深，固定机位。动作：顾沉舟将婚戒缓慢推入林晚指尖，对她说‘嫁给我吧’，林晚眼中含泪。]"
    }
  ]
}
```

## 字段要求

- `project.total_duration_seconds`：必填，必须等于所有镜头时长之和。
- `project.preferred_min_shot_seconds`：可选；常规镜头偏好下限，默认5。低于该值由验证脚本警告，但允许有明确理由的闪切或插入。
- `project.max_shot_seconds`：可选；默认硬上限10。超过该值由验证脚本报错。
- `project.aspect_ratio`：必填，格式如 `16:9`。
- `shots[].id`：唯一且数字连续，推荐 `S01`、`S02`。
- `shots[].duration`：正数。常规镜头根据剧情在5—10秒内选择；低于偏好下限需有节奏理由，不得超过硬上限。
- `shots[].visual`：只写第一帧可见事实。
- `shots[].motion`：只写接下来数秒的主要动作或运镜。
- `shots[].image`：相对于分镜目录的路径；推荐PNG。
- `generation_prompt`：可选；需要完整复现提示词时保留。
- `project.final_prompt_format`：新交付使用 `scene-character-camera-action-v1`。
- `shots[].video_prompt`：使用上述格式时必填。一条中文单段提示，只有一对外层 `[]`，内部依次为 `场景：`、`角色：`、`镜头：`、`动作：`，无换行。人物位置与实际首帧一致，包含该镜完整对白。内部结构字段不能替代这个最终交付字段。

## 生成Markdown

```powershell
py -3 scripts/build_storyboard_book.py storyboard-manifest.json --output storyboard-book.md --prompts-output video-prompts.txt
```

脚本会输出项目规格、统一约束、角色设定图，以及每镜准确时间码、景别、画面、运动、对白、后期备注和首帧图。每镜最终视频提示词以单段单独展示；内部首帧提示可折叠保留。`video-prompts.txt` 按镜号顺序集中输出全部提示词，每个非空行对应一镜，不加编号和说明。

Markdown图片路径沿用清单中的相对路径。把Markdown放在清单所在的分镜目录中，移动或压缩整个目录后仍可显示。

## 验证清单

```powershell
py -3 scripts/validate_storyboard.py storyboard-manifest.json --root .
```

验证JSON结构、镜号、时长、图片存在性、PNG尺寸一致性和画幅比例。只有结果为 `PASS` 后才能报告技术交付完成。视觉连续性仍需人工抽查，脚本不能替代导演验收。
