"evf#!/usr/bin/env python3
"""
Synchronise les sections 'significations' de tous les fichiers JSON sous i18n/lang
avec la référence `fr.json` :
- sauvegarde chaque fichier original en *.bak
- pour chaque langue, conserve les traductions existantes quand la clé existe
- pour les clés manquantes, crée une valeur placeholder: "TODO_TRANSLATE: <texte_fr>"
- supprime les clés qui ne figurent pas dans la référence
- écrit les fichiers modifiés en UTF-8

Usage: python scripts/sync_significations_to_fr.py
"""
import os, json, glob, shutil
ROOT = os.path.dirname(os.path.dirname(__file__))
lang_dir = os.path.join(ROOT, 'i18n', 'lang')
ref_fp = os.path.join(lang_dir, 'fr.json')
if not os.path.exists(ref_fp):
    raise SystemExit('fr.json introuvable dans i18n/lang. Abandon.')

with open(ref_fp, 'r', encoding='utf-8') as f:
    ref = json.load(f)
ref_sig = ref.get('significations', {})
ref_keys = list(ref_sig.keys())
print(f"Référence: fr.json avec {len(ref_keys)} clés")

files = sorted([p for p in glob.glob(os.path.join(lang_dir, '*.json')) if os.path.basename(p)!='fr.json'])
print(f"Fichiers à synchroniser: {len(files)}")

for fp in files:
    name = os.path.basename(fp)
    print(f"--- Processing {name}")
    bak = fp + '.bak'
    if not os.path.exists(bak):
        shutil.copy2(fp, bak)
        print(f"Sauvegarde créée: {os.path.basename(bak)}")
    else:
        print(f"Backup déjà existant: {os.path.basename(bak)}")

    with open(fp, 'r', encoding='utf-8') as f:
        try:
            j = json.load(f)
        except Exception as e:
            print(f"Erreur lecture {name}: {e}")
            continue
    sig = j.get('significations', {}) or {}

    new_sig = {}
    for k in ref_keys:
        if k in sig:
            new_sig[k] = sig[k]
        else:
            # create placeholder using FR text if available
            fr_text = ref_sig.get(k)
            if isinstance(fr_text, dict):
                # if it's a nested dict, try to copy upright/reversed fields
                placeholder = {}
                for subk, subv in fr_text.items():
                    placeholder[subk] = f"TODO_TRANSLATE: {subv}"
                new_sig[k] = placeholder
            else:
                new_sig[k] = f"TODO_TRANSLATE: {fr_text}"

    # Overwrite significations with new_sig
    j['significations'] = new_sig

    # write back
    with open(fp, 'w', encoding='utf-8') as f:
        json.dump(j, f, ensure_ascii=False, indent=2)
    print(f"Écrit {name} avec {len(new_sig)} clés")

print('Synchronisation terminée.')
