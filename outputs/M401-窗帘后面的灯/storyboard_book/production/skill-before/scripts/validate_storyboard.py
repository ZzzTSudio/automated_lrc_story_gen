#!/usr/bin/env python3
"""Validate storyboard timing, IDs, PNG frames, dimensions, and aspect ratio."""

import argparse
import json
import re
import struct
import sys
from pathlib import Path


def png_dimensions(path):
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("not a readable PNG")
    return struct.unpack(">II", header[16:24])


def parse_ratio(value):
    match = re.match(r"^\s*(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)\s*$", str(value))
    if not match:
        raise ValueError("aspect_ratio must look like 16:9")
    return float(match.group(1)) / float(match.group(2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, help="Storyboard root; defaults to manifest directory")
    parser.add_argument("--skip-images", action="store_true")
    args = parser.parse_args()
    root = (args.root or args.manifest.parent).resolve()
    errors, warnings = [], []
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except Exception as exc:
        print("FAIL: cannot read manifest: %s" % exc)
        return 1
    if not isinstance(data, dict):
        print("FAIL: manifest must be an object")
        return 1
    project, shots = data.get("project"), data.get("shots")
    if not isinstance(project, dict):
        errors.append("project must be an object")
        project = {}
    if not isinstance(shots, list) or not shots:
        errors.append("shots must be a non-empty array")
        shots = []
    seen, numbers, dimensions = set(), [], set()
    total = 0.0
    preferred_min = float(project.get("preferred_min_shot_seconds", 5))
    max_shot = float(project.get("max_shot_seconds", 10))
    if preferred_min <= 0:
        errors.append("project.preferred_min_shot_seconds must be positive")
    if max_shot < preferred_min:
        errors.append("project.max_shot_seconds must be greater than or equal to preferred_min_shot_seconds")
    try:
        expected_ratio = parse_ratio(project.get("aspect_ratio", "16:9"))
    except ValueError as exc:
        errors.append(str(exc))
        expected_ratio = None
    for index, shot in enumerate(shots, 1):
        if not isinstance(shot, dict):
            errors.append("shot %d must be an object" % index)
            continue
        shot_id = shot.get("id")
        if not isinstance(shot_id, str) or not shot_id:
            errors.append("shot %d has no valid id" % index)
            continue
        if shot_id in seen:
            errors.append("duplicate shot id %s" % shot_id)
        seen.add(shot_id)
        match = re.search(r"(\d+)$", shot_id)
        if not match:
            errors.append("shot id %s has no numeric suffix" % shot_id)
        else:
            numbers.append(int(match.group(1)))
        duration = shot.get("duration")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration <= 0:
            errors.append("%s has invalid duration" % shot_id)
        else:
            total += duration
            if duration < preferred_min:
                warnings.append("%s duration %s is below preferred minimum %s; keep only with a deliberate pacing reason" % (shot_id, duration, preferred_min))
            if duration > max_shot:
                errors.append("%s duration %s exceeds max %s" % (shot_id, duration, max_shot))
        if args.skip_images:
            continue
        image_rel = shot.get("image", "frames/%s.png" % shot_id)
        image_path = root / str(image_rel).lstrip("./\\")
        if not image_path.is_file() or image_path.stat().st_size == 0:
            errors.append("%s image missing or empty: %s" % (shot_id, image_path))
            continue
        if image_path.suffix.lower() != ".png":
            warnings.append("%s image is not PNG; dimension validation skipped" % shot_id)
            continue
        try:
            width, height = png_dimensions(image_path)
            dimensions.add((width, height))
            if expected_ratio and abs((float(width) / height) - expected_ratio) / expected_ratio > 0.02:
                errors.append("%s image ratio %sx%s does not match %s" % (shot_id, width, height, project.get("aspect_ratio")))
        except Exception as exc:
            errors.append("%s image error: %s" % (shot_id, exc))
    if numbers and numbers != list(range(1, len(shots) + 1)):
        errors.append("shot numeric IDs are not contiguous in manifest order: %s" % numbers)
    target_total = project.get("total_duration_seconds")
    if not isinstance(target_total, (int, float)) or isinstance(target_total, bool):
        errors.append("project.total_duration_seconds must be numeric")
    elif abs(total - target_total) > 1e-6:
        errors.append("shot duration sum %s does not equal project total %s" % (total, target_total))
    if len(dimensions) > 1:
        errors.append("frame dimensions are inconsistent: %s" % sorted(dimensions))
    for warning in warnings:
        print("WARN: %s" % warning)
    if errors:
        for error in errors:
            print("ERROR: %s" % error)
        print("FAIL: %d error(s), %d shot(s), duration=%s" % (len(errors), len(shots), total))
        return 1
    size_text = "%sx%s" % next(iter(dimensions)) if dimensions else "not checked"
    print("PASS: %d shots, duration=%ss, preferred=%s-%ss, frame=%s" % (len(shots), total, preferred_min, max_shot, size_text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
