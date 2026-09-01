"""Package final deliverables with portable relative paths, excluding rejected images."""
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parent.parent
destination = root.parent / 'M401-5min-storyboard-v1.zip'
files = [p for p in root.iterdir() if p.is_file()]
for folder in ('characters', 'scenes', 'frames', 'production/skill-after'):
    files.extend(p for p in (root / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
for name in ('asset-audit.json', 'image-generation-log.json', 'skill-update.diff'):
    files.append(root / 'production' / name)
assert len(list((root / 'frames').glob('S*.png'))) == 36
with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(set(files)):
        assert path.stat().st_size > 0, path
        archive.write(path, 'storyboard_book/' + path.relative_to(root).as_posix())
with zipfile.ZipFile(destination) as archive:
    assert archive.testzip() is None
    frame_entries = [name for name in archive.namelist() if name.startswith('storyboard_book/frames/') and name.endswith('.png')]
    assert len(frame_entries) == 36
print('VERIFIED ZIP:', destination)
print('BYTES:', destination.stat().st_size)
print('FILES:', len(set(files)))
