"""Exercise the changed skill's real export and rejection paths on temporary files."""
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parent.parent
skill = Path(r'C:\Users\Administrator\.codex\skills\ai-director-storyboard')
data = json.loads((root / 'storyboard-manifest.json').read_text(encoding='utf-8'))
data['shots'] = data['shots'][:1]
data['project']['total_duration_seconds'] = data['shots'][0]['duration']

with tempfile.TemporaryDirectory(prefix='m401-skill-check-') as folder:
    target = Path(folder)
    manifest = target / 'manifest.json'

    def run_check(case, expected):
        manifest.write_text(json.dumps(case, ensure_ascii=False), encoding='utf-8')
        result = subprocess.run([sys.executable, '-X', 'utf8', str(skill / 'scripts/validate_storyboard.py'), str(manifest), '--skip-images'], capture_output=True, text=True, encoding='utf-8')
        assert result.returncode == expected, result.stdout + result.stderr

    run_check(data, 0)
    exported = target / 'prompts.txt'
    book = target / 'book.md'
    subprocess.run([sys.executable, '-X', 'utf8', str(skill / 'scripts/build_storyboard_book.py'), str(manifest), '--output', str(book), '--prompts-output', str(exported)], check=True, capture_output=True)
    assert exported.read_text(encoding='utf-8').strip() == data['shots'][0]['video_prompt']
    assert data['shots'][0]['video_prompt'] in book.read_text(encoding='utf-8')
    for name in ('missing_prompt', 'multiline_prompt', 'timing_mismatch', 'duplicate_id'):
        case = copy.deepcopy(data)
        if name == 'missing_prompt':
            del case['shots'][0]['video_prompt']
        elif name == 'multiline_prompt':
            case['shots'][0]['video_prompt'] = case['shots'][0]['video_prompt'].replace('。角色：', '。\n角色：')
        elif name == 'timing_mismatch':
            case['project']['total_duration_seconds'] += 1
        else:
            case['shots'].append(copy.deepcopy(case['shots'][0]))
            case['project']['total_duration_seconds'] *= 2
        run_check(case, 1)
        print('PASS rejection:', name)
    print('PASS: valid manifest, exact prompt export, book inclusion, 4 invalid-input cases')
