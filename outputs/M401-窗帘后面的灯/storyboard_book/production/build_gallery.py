# -*- coding: utf-8 -*-
"""Build an offline storyboard gallery without modifying source frame images."""
import html
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
data = json.loads((root / 'storyboard-manifest.json').read_text(encoding='utf-8'))
escape = html.escape
beat_names = ['比他晚熄', '最后一页', '把话夹进去', '她在那边', '只交还记录', '灯照见自己']

def tc(seconds):
    return '%02d:%02d' % divmod(seconds, 60)

cards = []
elapsed = 0
for shot in data['shots']:
    end = elapsed + shot['duration']
    cards.append('''<article class="shot" data-beat="{beat}" id="{id}">
      <a class="frame" href="{image}" target="_blank" aria-label="打开{id}原图"><img loading="lazy" src="{image}" alt="{visual}" width="1672" height="941"></a>
      <div class="body"><div class="meta"><b>{id}</b><span>{start} — {end}</span><span>{duration}s</span></div>
      <h3>{camera}</h3><p class="action">{motion}</p>
      <details><summary>声音 / 制作备注</summary><p>{audio}</p><p>{notes}</p></details>
      <div class="copybar"><span>最终提示词 · 整段复制</span><button type="button" data-copy="p{id}">复制</button></div>
      <textarea id="p{id}" readonly aria-label="{id}完整视频提示词">{prompt}</textarea></div></article>'''.format(
        beat=shot['beat'], id=shot['id'], image=escape(shot['image'], quote=True), visual=escape(shot['visual'], quote=True),
        start=tc(elapsed), end=tc(end), duration=shot['duration'], camera=escape(shot['shot']), motion=escape(shot['motion']),
        audio=escape(shot['audio']), notes=escape(shot['post_notes']), prompt=escape(shot['video_prompt'])))
    elapsed = end
assert elapsed == 300
story = (root / 'story-expanded.md').read_text(encoding='utf-8').split('## 完整故事\n\n', 1)[1].split('\n## 六段场景', 1)[0]
story_html = ''.join('<p>' + escape(p.strip()) + '</p>' for p in story.split('\n\n') if p.strip())
filters = '<button type="button" data-filter="all" aria-pressed="true">全部 36 镜</button>' + ''.join('<button type="button" data-filter="%d" aria-pressed="false">%02d %s</button>' % (i+1, i+1, name) for i, name in enumerate(beat_names))
page = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>窗帘后面的灯 · M401 分镜书</title>
<style>
:root{color-scheme:dark;--bg:#111819;--panel:#1a2425;--ink:#ece9df;--muted:#a5b1ae;--accent:#d7bb82;--line:#354243}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font-family:'Microsoft YaHei',sans-serif;line-height:1.8}a{color:var(--accent)}button,a,input,summary{touch-action:manipulation}button{cursor:pointer;border:1px solid var(--line);background:#243132;color:var(--ink);padding:9px 16px;border-radius:7px;font:inherit}button[aria-pressed=true]{background:var(--accent);color:#182021;border-color:var(--accent)}button:focus-visible,a:focus-visible,textarea:focus-visible,summary:focus-visible{outline:3px solid #e7c87d;outline-offset:3px}header{max-width:1320px;margin:auto;padding:56px 28px 34px;display:grid;grid-template-columns:1fr 1.1fr;gap:40px;align-items:center}.eyebrow{letter-spacing:3px;color:var(--accent);font-size:12px}h1{font-family:'Microsoft YaHei',sans-serif;font-weight:500;font-size:clamp(30px,3.6vw,52px);line-height:1.3;margin:18px 0}header p{color:var(--muted);max-width:480px}header img{width:100%;display:block;border-radius:10px}.stats{display:flex;gap:24px;color:var(--accent);font-size:14px}.links{display:flex;gap:16px;flex-wrap:wrap;font-size:14px;margin-top:20px}.intro{max-width:1264px;margin:0 auto 30px;padding:0 28px}.intro>details{border-block:1px solid var(--line);padding:18px 0}.story{max-width:820px;margin:28px auto;color:#d3d9d5}.refs{display:grid;grid-template-columns:1fr 1fr;gap:18px}.refs img{width:100%;height:auto}.filters{position:sticky;top:0;z-index:2;background:#111819f5;border-block:1px solid var(--line);padding:12px max(24px,calc((100vw - 1264px)/2));display:flex;gap:8px;overflow-x:auto;white-space:nowrap}.filters button{font-size:13px;padding:8px 13px}main{max-width:1320px;margin:auto;padding:28px;display:grid;grid-template-columns:1fr 1fr;gap:28px}.shot{background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;scroll-margin-top:100px}.shot[hidden]{display:none}.frame{display:block;line-height:0}.frame img{width:100%;height:auto;aspect-ratio:1672/941;object-fit:contain}.body{padding:22px}.meta{display:flex;gap:18px;align-items:center;color:var(--muted);font-size:13px}.meta b{font-size:20px;color:var(--accent);margin-right:auto}h3{font-size:15px;font-weight:500;margin:16px 0 10px}.action{font-size:14px;min-height:76px}.body details{font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:10px}.body details p{margin:10px 0}.copybar{margin-top:18px;display:flex;justify-content:space-between;align-items:center;font-size:12px;color:var(--accent)}.copybar button{font-size:12px;padding:4px 12px}textarea{margin-top:8px;width:100%;min-height:164px;resize:vertical;border:1px solid var(--line);border-radius:6px;padding:12px;background:#121b1c;color:#ccd5d1;font:13px/1.8 'Microsoft YaHei',sans-serif}footer{text-align:center;padding:26px;color:var(--muted);font-size:12px}@media(max-width:800px){header{grid-template-columns:1fr;padding-top:28px;gap:20px}main{grid-template-columns:1fr;padding:16px}.intro{padding:0 20px}.refs{grid-template-columns:1fr}.action{min-height:0}}@media print{.filters,button,.links{display:none}header{padding:0}main{display:block}.shot{break-inside:avoid;margin-bottom:24px}textarea{border:0;min-height:180px}body{background:white;color:black}}
</style></head><body><header><div><div class="eyebrow">M401 / DIRECTOR'S STORYBOARD / V1</div><h1>窗帘后面的灯</h1><p>他以为是一盏忘关的灯。<br>她等了三年，终于在清晨亲手把它关掉。</p><div class="stats"><span>05:00 设计时长</span><span>36 个镜头</span><span>16:9</span></div><div class="links"><a href="video-prompts.txt" download>下载提示词合集</a><a href="storyboard-book.md">Markdown分镜书</a><a href="story-expanded.md">详细剧本</a><a href="continuity-bible.md">连续性设定</a><a href="validation-report.md">验收记录</a></div><p style="font-size:12px">本页是视频生成前期分镜包；图片为首帧，不是已生成影片。单镜6—10秒，片名包含在最后一镜内。</p></div><img src="frames/S34.png" alt="林澄独自坐在亮灯的书桌前，桌上留着撕碎的告白" width="1672" height="941"></header>
<section class="intro"><details><summary>阅读完整故事</summary><div class="story">__STORY__</div></details><details><summary>人物与空间参考 · 4张</summary><div class="refs"><figure><img src="characters/lin-cheng-sheet.png" alt="林澄角色设定"><figcaption>林澄</figcaption></figure><figure><img src="characters/zhou-yu-sheet.png" alt="周屿角色设定"><figcaption>周屿</figcaption></figure><figure><img src="scenes/lab-anchor.png" alt="实验记录室空间锚点"><figcaption>实验记录室</figcaption></figure><figure><img src="scenes/dorm-anchor.png" alt="宿舍空间锚点"><figcaption>宿舍书桌</figcaption></figure></div></details></section>
<nav class="filters" aria-label="按剧情段落筛选">__FILTERS__</nav><main>__CARDS__</main><footer>原故事、歌词与WAV保留不变 · 精确纸面文字与片名交后期 · 2026-08-31</footer>
<script>document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('[data-filter]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));document.querySelectorAll('.shot').forEach(x=>{x.hidden=b.dataset.filter!=='all'&&x.dataset.beat!==b.dataset.filter});}));document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',async()=>{const t=document.getElementById(b.dataset.copy);try{if(navigator.clipboard){await navigator.clipboard.writeText(t.value)}else{t.focus();t.select();if(!document.execCommand('copy'))throw Error('copy unavailable')}b.textContent='已复制';setTimeout(()=>b.textContent='复制',1500)}catch(e){t.focus();t.select();b.textContent='已选中，请手动复制'}}));</script></body></html>'''
page = page.replace('__STORY__', story_html).replace('__FILTERS__', filters).replace('__CARDS__', '\n'.join(cards))
(root / 'storyboard-gallery.html').write_text(page, encoding='utf-8')
print('WROTE offline gallery: 36 shots, 300 seconds')
