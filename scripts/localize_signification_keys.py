#!/usr/bin/env python3
"""
Utility: convert the `significations` keys in a language JSON from French canonical
names to the localized card names for that language.

This script is careful and non-destructive:
- creates a backup of the original file (lang.json.bak)
- preserves existing translations when possible
- when no localized key can be derived, leaves the French key in place

Usage (from project root):
  python3 scripts/localize_signification_keys.py --lang es

This file is meant to be imported or executed. It uses the project's
`cards_mapping.get_card_name_for_lang` function to compute localized keys.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict


def _load_json(fp: str) -> Dict:
    try:
        with open(fp, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return {}


def _write_json(fp: str, obj: Dict) -> None:
    with open(fp, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)


def localize_lang_significations(lang: str, project_root: str = None) -> bool:
    """Convert `i18n/lang/{lang}.json` signification keys to localized names.

    Returns True on success, False otherwise.
    """
    if not project_root:
        project_root = os.path.dirname(os.path.dirname(__file__))
    lang_dir = os.path.join(project_root, 'i18n', 'lang')
    fp = os.path.join(lang_dir, f"{lang}.json")
    if not os.path.exists(fp):
        print(f"Lang file not found: {fp}")
        return False

    # try to import the cards_mapping utilities from the project
    try:
        import cards_mapping
    except Exception:
        cards_mapping = None

    fr_fp = os.path.join(lang_dir, 'fr.json')
    if not os.path.exists(fr_fp):
        print("fr.json (reference) not found; aborting")
        return False

    fr = _load_json(fr_fp) or {}
    fr_sig = fr.get('significations', {}) or {}

    j = _load_json(fp) or {}
    sig = j.get('significations', {}) or {}

    new_sig = {}

    # For each canonical French key, compute localized key and preserve existing translations
    for french_key in fr_sig.keys():
        localized_key = french_key
        try:
            if cards_mapping:
                candidate = cards_mapping.get_card_name_for_lang(french_key, lang)
                if candidate:
                    localized_key = candidate
        except Exception:
            localized_key = french_key

        # Prefer already-localized entries in the file (if present)
        if localized_key in sig:
            new_sig[localized_key] = sig[localized_key]
        elif french_key in sig:
            # move existing French-keyed translation under the localized key
            new_sig[localized_key] = sig[french_key]
        else:
            # fallback: keep French text as placeholder (don't drop information)
            existing = fr_sig.get(french_key)
            if isinstance(existing, dict):
                placeholder = {}
                for subk, subv in existing.items():
                    placeholder[subk] = f"TODO_TRANSLATE: {subv}"
                new_sig[localized_key] = placeholder
            else:
                new_sig[localized_key] = f"TODO_TRANSLATE: {existing}"

    # Keep any extra keys the language file had that are not in fr.json (append them)
    for k, v in sig.items():
        if k in new_sig:
            continue
        # avoid accidental duplicates: add with same key
        new_sig[k] = v

    # Backup original
    bak = fp + '.bak'
    if not os.path.exists(bak):
        try:
            Path(bak).write_text(json.dumps(j, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f"Backup created: {bak}")
        except Exception as e:
            print(f"Warning: could not create backup {bak}: {e}")

    j['significations'] = new_sig
    try:
        _write_json(fp, j)
        print(f"Wrote localized significations to {fp} ({len(new_sig)} keys)")
        return True
    except Exception as e:
        print(f"Failed to write {fp}: {e}")
        return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--lang', required=True, help='language code (filename without .json)')
    args = p.parse_args()
    ok = localize_lang_significations(args.lang)
    if not ok:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
