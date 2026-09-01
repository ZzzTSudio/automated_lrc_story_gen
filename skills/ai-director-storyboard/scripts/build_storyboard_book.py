#!/usr/bin/env python3
"""Build a portable Markdown storyboard book from a JSON manifest."""

import argparse
import json
from pathlib import Path


def timecode(seconds):
    seconds = int(seconds)
    return "%02d:%02d" % divmod(seconds, 60)


def load_manifest(path):
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("project"), dict):
        raise ValueError("manifest and project must be objects")
    if not isinstance(data.get("shots"), list) or not data["shots"]:
        raise ValueError("shots must be a non-empty array")
    return data


def render(data):
    project = data["project"]
    title = project.get("title", "未命名项目")
    total = project.get("total_duration_seconds")
    lines = [
        "# 《%s》AI视频分镜书" % title, "",
        "> 总时长：%s  " % timecode(total),
        "> 分镜数量：%d  " % len(data["shots"]),
        "> 常规单镜：%s—%s秒  " % (project.get("preferred_min_shot_seconds", 5), project.get("max_shot_seconds", 10)),
        "> 画幅／首帧：%s／%s" % (project.get("aspect_ratio", "16:9"), project.get("frame_size", "未指定")), ""
    ]
    constraints = data.get("global_constraints", [])
    if constraints:
        lines.extend(["## 全片统一约束", ""] + ["- %s" % item for item in constraints] + [""])
    characters = data.get("characters", [])
    if characters:
        lines.extend(["## 角色设定", ""])
        for char in characters:
            lines.extend(["### %s" % char.get("name", "未命名角色"), "", char.get("description", ""), ""])
            if char.get("image"):
                lines.extend(["![%s角色设定](./%s)" % (char.get("name", "角色"), char["image"].lstrip("./")), ""])
    lines.extend(["# 逐镜头分镜", ""])
    elapsed = 0
    for shot in data["shots"]:
        duration = shot["duration"]
        start, end = elapsed, elapsed + duration
        elapsed = end
        people = shot.get("characters", [])
        image = shot.get("image", "frames/%s.png" % shot["id"])
        lines.extend([
            "## %s｜%s—%s｜%s秒" % (shot["id"], timecode(start), timecode(end), duration), "",
            "- 场景：%s" % shot.get("scene", "未指定"),
            "- 出镜：%s" % shot.get("character_placement", "、".join(people) if people else "无明确主角面部"),
            "- 景别／镜头：%s" % shot.get("shot", "未指定"),
            "- 首帧画面：%s" % shot.get("visual", ""),
            "- 运动提示：%s" % shot.get("motion", ""),
            "- 对白／声音：%s" % shot.get("dialogue", ""),
            "- 声场／剪辑：%s" % shot.get("audio", ""),
            "- 后期备注：%s" % shot.get("post_notes", ""), "",
            "![%s 首帧](./%s)" % (shot["id"], image.lstrip("./")), ""
        ])
        if shot.get("video_prompt"):
            lines.extend(["### 最终视频提示词（整段复制）", "", "```text", shot["video_prompt"], "```", ""])
        if shot.get("generation_prompt"):
            lines.extend(["<details><summary>首帧生成提示词</summary>", "", "```text", shot["generation_prompt"], "```", "", "</details>", ""])
    if elapsed != total:
        raise ValueError("shot duration sum %s does not equal project total %s" % (elapsed, total))
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--prompts-output", type=Path, help="Write one complete video prompt per non-empty line")
    args = parser.parse_args()
    data = load_manifest(args.manifest)
    content = render(data)
    if args.prompts_output:
        prompts = [shot.get("video_prompt") for shot in data["shots"]]
        if any(not isinstance(prompt, str) or not prompt.strip() or "\n" in prompt or "\r" in prompt for prompt in prompts):
            raise ValueError("all shots need a non-empty single-line video_prompt for prompt export")
        args.prompts_output.parent.mkdir(parents=True, exist_ok=True)
        args.prompts_output.write_text("\n\n".join(prompts) + "\n", encoding="utf-8")
        print("WROTE %s (%d prompts)" % (args.prompts_output, len(prompts)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")
    print("WROTE %s (%d shots)" % (args.output, len(data["shots"])))


if __name__ == "__main__":
    main()
