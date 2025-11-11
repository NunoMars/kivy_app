#!/usr/bin/env bash
# Diagnostic rapide Achats In-App (Google Play Billing)
# Usage: ./scripts/iap_diag.sh [PACKAGE]
# Exemple: ./scripts/iap_diag.sh org.tarot.macartedetarot

set -euo pipefail
PKG="${1:-org.tarot.macartedetarot}"

echo "== App et Play Store versions =="
adb shell dumpsys package "$PKG" | grep -E "versionCode|versionName" -A 1 || true
adb shell dumpsys package com.android.vending | grep versionName || true

echo "\n== Logs Billing / ProductDetails / Achats =="
adb logcat -d | grep -E "Billing|ProductDetails|Achat|premium_features|Purchases|Acknowledge" | tail -n 200 || true

echo "\n== Fichier de log IAP local (si présent) =="
adb shell run-as "$PKG" cat /data/data/$PKG/files/iap_debug.log 2>/dev/null || echo "(absent)"

cat <<EOF

Conseils:
- Code ProductDetails 4 = ITEM_UNAVAILABLE: vérifier ID 'premium_features' actif dans Play Console.
- Code 5 = DEVELOPER_ERROR: vérifier package, build Play Store, licences test.
- Assure-toi que le test se fait depuis une version Play (pas sideload).
EOF
