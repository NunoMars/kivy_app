#!/usr/bin/env python3
# apply_image_mapping.py — applique le mapping d'images aux fichiers i18n/lang/*.json

import json, shutil
from pathlib import Path

BASE = Path(__file__).resolve().parents[0]
I18N_DIR = BASE / "i18n" / "lang"
MAPPING_FILE = BASE / "image_mapping_dryrun.json"

def load_mapping():
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def backup_file(path: Path):
    bak = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak)
    return bak

def apply_to_file(path: Path, mapping):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    sig = data.get("significations", {})
    changed = False
    for key, imgs in mapping.items():
        if key in sig and isinstance(sig[key], dict):
            # insert or update image fields
            old_img = sig[key].get("image")
            old_rev = sig[key].get("image_reversed")
            new_img = imgs.get("image")
            new_rev = imgs.get("image_reversed")
            if old_img != new_img:
                sig[key]["image"] = new_img
                changed = True
            if old_rev != new_rev:
                sig[key]["image_reversed"] = new_rev
                changed = True
    if changed:
        # write backup and then overwrite original
        bak = backup_file(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True, bak
    return False, None

def validate_file(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    sig = data.get("significations", {})
    return isinstance(sig, dict) and len(sig) == 38


def main():
    mapping = load_mapping()
    modified = []
    for p in sorted(I18N_DIR.iterdir()):
        if p.is_file() and p.suffix.lower() == ".json":
            ok, bak = apply_to_file(p, mapping)
            valid = validate_file(p)
            modified.append((p.name, ok, bak.name if bak else None, valid))
            print(f"{p.name}: modified={ok}, backup={bak.name if bak else '-'}, valid38={valid}")
    # summary
    print("\n--- Summary ---")
    for m in modified:
        print(f"{m[0]}: modified={m[1]}, backup={m[2]}, valid38={m[3]}")

if __name__ == "__main__":
    main()
