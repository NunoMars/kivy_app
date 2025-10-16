#!/usr/bin/env python3
# dry_run_map_images.py — dry run: map french card keys -> image filenames

import json, os, unicodedata, re
from pathlib import Path

BASE = Path(__file__).resolve().parents[0]
I18N_FR = BASE / "i18n" / "lang" / "fr.json"
IMG_DIR = BASE / "tarot_img" / "MajorArcanaCards"

EXTS = [".jpg", ".jpeg", ".png", ".gif"]
REVERSAL_MARKERS = ["a l'envers", "a l envers", "a-l'envers", "a-l-envers", "invers", "revers"]


def normalize(s):
    s = s.lower()
    s = s.replace("’", "'").replace("`", "'")
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def load_fr_keys():
    with open(I18N_FR, "r", encoding="utf-8") as f:
        data = json.load(f)
    return list(data.get("significations", {}).keys())


def build_file_index():
    files = []
    if not IMG_DIR.exists():
        raise FileNotFoundError(f"Image dir not found: {IMG_DIR}")
    for p in IMG_DIR.iterdir():
        if p.is_file() and p.suffix.lower() in EXTS:
            files.append(p)
    # index by normalized stem -> list(paths)
    idx = {}
    for p in files:
        stem = p.stem
        n = normalize(stem)
        idx.setdefault(n, []).append(p)
    return files, idx


def find_images_for_key(key, files, idx):
    nk = normalize(key)
    # 1) exact normalized stem match
    if nk in idx:
        candidates = idx[nk]
        # prefer exact accent-preserving match if exists
        for c in candidates:
            if c.stem == key:
                rev = find_reversed_for_stem(c.stem, files)
                return str(c.relative_to(BASE)), str(rev.relative_to(BASE)) if rev else None
        # otherwise take first and try find its reversed counterpart
        chosen = candidates[0]
        rev = find_reversed_for_stem(chosen.stem, files)
        return str(chosen.relative_to(BASE)), str(rev.relative_to(BASE)) if rev else None
    # 2) fallback: search filenames containing normalized key
    for p in files:
        if nk in normalize(p.stem):
            rev = find_reversed_for_stem(p.stem, files)
            return str(p.relative_to(BASE)), str(rev.relative_to(BASE)) if rev else None
    # 3) not found
    return None, None


def find_reversed_for_stem(stem, files):
    nstem = normalize(stem)
    for p in files:
        np = normalize(p.stem)
        if any(marker in np for marker in REVERSAL_MARKERS) and nstem in np:
            return p
    for p in files:
        np = normalize(p.stem)
        if nstem in np and any(marker in np for marker in REVERSAL_MARKERS):
            return p
    return None


def main():
    keys = load_fr_keys()
    files, idx = build_file_index()
    mapping = {}
    missing = []
    for k in keys:
        img, img_rev = find_images_for_key(k, files, idx)
        mapping[k] = {"image": img, "image_reversed": img_rev}
        if not img:
            missing.append((k, "normal"))
        if not img_rev:
            missing.append((k, "reversed"))
    # print results
    for k, v in mapping.items():
        print(f"{k}: image={v['image']}, image_reversed={v['image_reversed']}")
    print("\n--- Résumé ---")
    print(f"Total cartes vérifiées: {len(keys)}")
    print("Manquants:")
    for m in missing:
        print(" -", m[0], ":", m[1])
    # write mapping to a JSON file for inspection
    out = BASE / "image_mapping_dryrun.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print("\nMapping écrit en:", out)

if __name__ == "__main__":
    main()
