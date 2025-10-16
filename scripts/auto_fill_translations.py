#!/usr/bin/env python3
"""
Auto-fill TODO_TRANSLATE placeholders by copying existing translations from other language files.
Strategy:
 - Use `i18n/lang/fr.json` as canonical reference for keys.
 - For each language file, determine the localized key for each french key using cards_mapping.get_card_name_for_lang.
 - If the target entry contains "TODO_TRANSLATE: <fr_text>", look for an existing translation for the same french key in other languages and copy it.
 - Prefer regional variants (e.g. es_latam before es) by simple ordering.
 - Make a backup <file>.autofill.bak before writing.

This operates offline and does not call external translation APIs.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parents[1]
LANG_DIR = ROOT / 'i18n' / 'lang'


def _load(fp: Path) -> Dict[str, Any]:
    try:
        return json.loads(fp.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _write(fp: Path, obj: Dict[str, Any]):
    fp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')


def is_todo(value: Any) -> bool:
    if isinstance(value, str):
        return isinstance(value, str) and value.strip().startswith('TODO_TRANSLATE:')
    if isinstance(value, dict):
        for v in value.values():
            if isinstance(v, str) and v.strip().startswith('TODO_TRANSLATE:'):
                return True
    return False


def extract_todo_fr_text(value: Any) -> Dict[str, str]:
    """Return mapping subkey->fr_text extracted from TODO placeholders in value.
    If value is a string, returns {'__self__': fr_text}.
    """
    res = {}
    if isinstance(value, str):
        txt = value.strip()
        if txt.startswith('TODO_TRANSLATE:'):
            res['__self__'] = txt[len('TODO_TRANSLATE:'):].strip()
    elif isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, str) and v.strip().startswith('TODO_TRANSLATE:'):
                res[k] = v.strip()[len('TODO_TRANSLATE:'):].strip()
    return res


def main():
    # load fr reference
    fr_fp = LANG_DIR / 'fr.json'
    if not fr_fp.exists():
        print('fr.json not found; abort')
        return 1
    fr = _load(fr_fp)
    fr_sig = fr.get('significations', {})
    french_keys = list(fr_sig.keys())

    # discover language files
    lang_files = sorted([p for p in LANG_DIR.glob('*.json') if p.name != 'fr.json'])

    # try import cards_mapping
    try:
        import cards_mapping
    except Exception as e:
        print('could not import cards_mapping:', e)
        return 1

    # Build source translations map: for each fr_key, map lang->entry (prefer non-TODO)
    source_map: Dict[str, Dict[str, Any]] = {fk: {} for fk in french_keys}

    for fp in lang_files:
        lang_code = fp.stem
        j = _load(fp)
        sig = j.get('significations', {}) or {}
        for fk in french_keys:
            localized = cards_mapping.get_card_name_for_lang(fk, lang_code)
            entry = None
            if localized in sig:
                entry = sig[localized]
            elif fk in sig:
                entry = sig[fk]
            if entry is not None and not is_todo(entry):
                source_map[fk][lang_code] = entry

    # now fill TODOs by copying from source_map
    changed_files = {}
    for fp in lang_files:
        lang_code = fp.stem
        j = _load(fp)
        sig = j.get('significations', {}) or {}
        modified = False
        for fk in french_keys:
            localized = cards_mapping.get_card_name_for_lang(fk, lang_code)
            # prefer localized key, else fallback to french key
            target_key = localized if localized in sig else (fk if fk in sig else None)
            if not target_key:
                # create new localized entry if translation source exists
                # but we only want to fill if there's a source
                if source_map.get(fk):
                    # pick best source: prefer same base language (eg es_latam->es)
                    picked = None
                    for cand_lang in [lang_code] + list(source_map[fk].keys()):
                        if cand_lang in source_map[fk]:
                            picked = source_map[fk][cand_lang]
                            break
                    if picked is not None:
                        sig[localized] = picked
                        modified = True
                continue

            cur = sig.get(target_key)
            if cur is None:
                continue
            if not is_todo(cur):
                continue
            # target has TODOs; try to find a source translation
            candidate = None
            # prefer same base language variants (e.g., es_latam -> es, es -> es_latam)
            base = lang_code.split('_')[0].split('-')[0]
            # order: prefer exact lang_code source, then base variants, then any other
            order = []
            if lang_code in source_map[fk]:
                order.append(lang_code)
            # include other variants with same base
            for s in list(source_map[fk].keys()):
                if s != lang_code and s.split('_')[0].split('-')[0] == base:
                    order.append(s)
            # finally any available
            for s in source_map[fk].keys():
                if s not in order:
                    order.append(s)
            for s in order:
                candidate = source_map[fk].get(s)
                if candidate is not None:
                    break
            if candidate is None:
                continue
            # replace cur TODOs with candidate translations (structure preserved)
            if isinstance(cur, str) and isinstance(candidate, str):
                sig[target_key] = candidate
                modified = True
            elif isinstance(cur, dict) and isinstance(candidate, dict):
                newdict = dict(cur)
                for subk, subv in cur.items():
                    if isinstance(subv, str) and subv.strip().startswith('TODO_TRANSLATE:'):
                        # try to copy same subkey from candidate
                        if subk in candidate and isinstance(candidate[subk], str):
                            newdict[subk] = candidate[subk]
                            modified = True
                        else:
                            # fallback: if candidate has a single string, use it
                            pass
                # if we replaced any, assign
                sig[target_key] = newdict
        if modified:
            # backup
            bak = fp.with_suffix('.autofill.bak')
            if not bak.exists():
                fp.rename(fp.with_suffix('.origbak'))
                # restore original name after writing? To be safe, write to original path and save .origbak
                # but simpler: write backup file with .autofill.bak using the original content from .origbak
                Path(str(bak)).write_text(json.dumps(_load(fp.with_suffix('.origbak')), ensure_ascii=False, indent=2), encoding='utf-8')
            # assign back
            j['significations'] = sig
            _write(fp, j)
            changed_files[fp.name] = True

    # report
    print('Auto-fill complete. Files modified:')
    for f in changed_files:
        print('-', f)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
