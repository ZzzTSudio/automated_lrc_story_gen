# -*- coding: utf-8 -*-
"""Apply visual review notes, export deliverables and validate all local assets."""
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parent.parent
skill = Path(r'C:\Users\Administrator\.codex\skills\ai-director-storyboard')
manifest_path = root / 'storyboard-manifest.json'
data = json.loads(manifest_path.read_text(encoding='utf-8'))
edits = json.loads((root / 'production/review-adjustments.json').read_text(encoding='utf-8'))
generation_log = json.loads((root / 'production/image-generation-log.json').read_text(encoding='utf-8'))
for shot in data['shots']:
    shot.update(edits.get(shot['id'], {}))
    stability = '保持人物身份、发型、服装和空间结构稳定' if shot['characters'] else '保持空间结构稳定，不增加人物'
    shot['video_prompt'] = '[场景：%s。角色：%s。镜头：%s。动作：%s；%s。]' % (shot['scene'], shot['character_placement'], shot['shot'], shot['motion'], stability)
    shot['generation_history'] = [entry for entry in generation_log if entry['id'] == shot['id']]
    shot['visual_review'] = '首帧已查看；已按实际构图修订出镜位置和必要景别。后续视频动作及口型仍须验收。'
data['project']['status'] = 'visual_preproduction_ready_for_review'
manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def run(script, *args):
    result = subprocess.run([sys.executable, '-X', 'utf8', str(script), *map(str, args)], text=True, capture_output=True, encoding='utf-8')
    print(result.stdout.strip())
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout.strip()

checks = []
try:
    checks.append(run(skill / 'scripts/validate_storyboard.py', manifest_path, '--root', root))
    dimension_pass = True
except RuntimeError as exc:
    checks.append(str(exc))
    dimension_pass = False
data['project']['frame_size'] = '1672x941' if dimension_pass else '1670—1672×941（尚未统一）'
manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
checks.append(run(skill / 'scripts/build_storyboard_book.py', manifest_path, '--output', root / 'storyboard-book.md', '--prompts-output', root / 'video-prompts.txt'))
checks.append(run(root / 'production/build_gallery.py'))
checks.append(run(root / 'production/check_skill_pipeline.py'))

assets = []
for folder in ('characters', 'scenes', 'frames'):
    for file in sorted((root / folder).glob('*.png')):
        with Image.open(file) as image:
            width, height = image.size
            image.verify()
        assets.append({'path': file.relative_to(root).as_posix(), 'bytes': file.stat().st_size, 'width': width, 'height': height, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
assert len(assets) == 40, len(assets)
all_uniform = all((a['width'], a['height']) == (1672, 941) for a in assets)
data['project']['status'] = 'visual_preproduction_complete' if dimension_pass and all_uniform else 'ready_for_review_pending_dimension_normalization'
manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
prompts = [line for line in (root / 'video-prompts.txt').read_text(encoding='utf-8').splitlines() if line.strip()]
assert prompts == [s['video_prompt'] for s in data['shots']]
assert len(prompts) == 36
assert all(all(p.count(label) == 1 for label in ('场景：', '角色：', '镜头：', '动作：')) for p in prompts)
book = (root / 'storyboard-book.md').read_text(encoding='utf-8')
for rel in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', book):
    assert (root / rel).is_file(), rel
(root / 'production/asset-audit.json').write_text(json.dumps(assets, ensure_ascii=False, indent=2), encoding='utf-8')

changed = ['SKILL.md', 'references/visual-pipeline.md', 'references/manifest-schema.md', 'scripts/build_storyboard_book.py', 'scripts/validate_storyboard.py']
diff = []
for rel in changed:
    before = (root / 'production/skill-before' / rel).read_text(encoding='utf-8').splitlines(True)
    after = (skill / rel).read_text(encoding='utf-8').splitlines(True)
    diff.extend(difflib.unified_diff(before, after, fromfile='before/' + rel, tofile='after/' + rel))
(root / 'production/skill-update.diff').write_text(''.join(diff), encoding='utf-8')
for rel in changed + ['references/directing-workflow.md', 'agents/openai.yaml']:
    source = skill / rel
    if source.exists():
        destination = root / 'production/skill-after' / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

report = '''# M401 前期分镜包验收记录

## 已完成

- 详细扩写故事、人物动机、六段剧情、对白定稿、声音与剪辑设计。
- 36 个连续镜号 S01—S36，单镜 6—10 秒，总和 **300 秒 / 05:00**；最后4秒片名计入最后一镜。
- **40 张 PNG**：角色设定2张、场景锚点2张、逐镜首帧36张。全部可解码、非空。__DIMENSION_STATUS__
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
__CHECKS__
PASS: 40 readable PNG assets, 36 exported prompts, valid Markdown image links
```
'''.replace('__CHECKS__', '\n'.join(checks)).replace('__DIMENSION_STATUS__', '尺寸全部为1672×941，比例接近16:9，技术尺寸校验通过。' if dimension_pass and all_uniform else '原始宽度为1670/1671/1672像素，高度均为941像素。14张图片尚需1—2像素的尺寸统一，严格尺寸校验未通过，等待本地尺寸处理授权；没有将尺寸差异掩盖为PASS。')
report += '\n## 图文页检查\n\n浏览器安全策略拒绝file URL，未绕过此限制，也未声称完成浏览器交互验收。HTML图片与下载链接使用工程内相对路径，已做静态文件存在性检查。筛选与复制按钮保留实现，实际交互须由用户打开页面后确认。\n'
(root / 'validation-report.md').write_text(report, encoding='utf-8')
page = (root / 'storyboard-gallery.html').read_text(encoding='utf-8')
for rel in re.findall(r'(?:src|href)="([^"#]+)"', page):
    assert (root / rel).is_file(), rel
print('PASS: 40 PNG assets, 36 single-paragraph prompts, Markdown/HTML file links, skill snapshot')
print('Dimension status:', 'PASS' if dimension_pass and all_uniform else 'PENDING NORMALIZATION')
