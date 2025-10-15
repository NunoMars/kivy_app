#!/usr/bin/env python3
"""Script helper: migrer les modules signification_*.py vers un fichier JSON central.

Usage:
    python3 scripts/migrate_significations.py --out ../data/significations.json

Il inspecte les modules présents dans le dossier courant (workspace racine) nommés
signification_*.py et extrait la variable `cards_signification` ou la valeur
retournée par `get_cards_signification()`.
"""
import os
import json
import importlib.util
import argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def load_module(path):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"Erreur chargement {path}: {e}")
        return None
    return mod


def extract_from_module(mod):
    if mod is None:
        return None
    if hasattr(mod, 'get_cards_signification'):
        try:
            return mod.get_cards_signification()
        except Exception:
            pass
    if hasattr(mod, 'cards_signification'):
        return mod.cards_signification
    if hasattr(mod, 'significations'):
        return mod.significations
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default=os.path.join(ROOT, 'data', 'significations.json'))
    args = parser.parse_args()

    # Prefer JSON-based sources via i18n.lang files
    try:
        import i18n
        lang_dir = os.path.join(os.path.dirname(i18n.__file__), 'lang')
        files = [f for f in os.listdir(lang_dir) if f.endswith('.json')]
        data = {}
        for f in files:
            lang = os.path.splitext(f)[0]
            try:
                content = i18n.load_lang_significations(lang)
                if content:
                    data[lang] = content
                    print(f"Imported {lang} -> {len(content)} entries from JSON")
            except Exception as e:
                print(f"Skipping {f}: {e}")
    except Exception:
        # Fallback: try legacy signification_*.py modules (rare)
        files = [f for f in os.listdir(ROOT) if f.startswith('signification_') and f.endswith('.py')]
        data = {}
        for f in files:
            full = os.path.join(ROOT, f)
            mod = load_module(full)
            content = extract_from_module(mod)
            if content:
                lang = f.replace('signification_', '').replace('.py', '')
                data[lang] = content
                print(f"Imported {lang} -> {len(content)} entries from module")

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    print(f"Wrote {out} with languages: {list(data.keys())}")


if __name__ == '__main__':
    main()
