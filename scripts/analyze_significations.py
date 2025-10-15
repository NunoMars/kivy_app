#!/usr/bin/env python3
"""Analyze i18n/lang/*.json and report signification entries that are short
compared to reference languages (fr and pt). Writes i18n/significations_short_report.json
"""
import os, json, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG_DIR = os.path.join(ROOT, 'i18n', 'lang')
OUT = os.path.join(ROOT, 'i18n', 'significations_short_report.json')
REF_LANGS = ['fr', 'pt']
THRESH_PERC = 0.6
ABS_MIN = 120

def load_json(p):
    try:
        with open(p, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception as e:
        print('ERR', p, e)
        return None

# build reference lengths per card using FR then PT if available
ref_lengths = {}
for rl in REF_LANGS:
    p = os.path.join(LANG_DIR, f'{rl}.json')
    data = load_json(p)
    if not data:
        continue
    signs = data.get('significations', {})
    for card, bundle in signs.items():
        # choose the longest 'signification' field present
        max_len = 0
        for k, v in bundle.items():
            if isinstance(k, str) and 'signification' in k.lower():
                if isinstance(v, str):
                    max_len = max(max_len, len(v.strip()))
        if max_len:
            ref_lengths[card] = max(ref_lengths.get(card, 0), max_len)

# list all lang files
files = [f for f in os.listdir(LANG_DIR) if f.endswith('.json')]
report = {}
summary_count = 0
for fn in files:
    lang = os.path.splitext(fn)[0]
    p = os.path.join(LANG_DIR, fn)
    data = load_json(p)
    if not data:
        continue
    signs = data.get('significations', {})
    short_items = []
    for card, bundle in signs.items():
        # find the most descriptive signification string available
        best_len = 0
        best_key = None
        best_text = None
        for k, v in bundle.items():
            if isinstance(k, str) and 'signification' in k.lower():
                if isinstance(v, str):
                    l = len(v.strip())
                    if l > best_len:
                        best_len = l
                        best_key = k
                        best_text = v
        # compare to ref
        ref = ref_lengths.get(card)
        if ref:
            if best_len < max(int(ref * THRESH_PERC), ABS_MIN):
                short_items.append({
                    'card': card,
                    'field': best_key,
                    'length': best_len,
                    'ref_length': ref,
                })
        else:
            # if no ref, consider anything below ABS_MIN as short
            if best_len < ABS_MIN:
                short_items.append({
                    'card': card,
                    'field': best_key,
                    'length': best_len,
                    'ref_length': None,
                })
    if short_items:
        report[fn] = short_items
        summary_count += 1

out = {'summary_count': summary_count, 'report': report}
with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
print('WROTE', OUT)
print('SUMMARY_COUNT', summary_count)
