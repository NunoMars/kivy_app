#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Script : Extraire les symboles de débogage après build
# Usage  : ./extract_debug_symbols.sh [version]
# ═══════════════════════════════════════════════════════════════

set -e  # Exit on error

VERSION=${1:-"2.1"}
BUILD_DIR=".buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/macartedetarot"
OUTPUT_DIR="debug_symbols/v${VERSION}"
DESKTOP_DIR="/mnt/c/Users/loupy/Desktop/debug_v${VERSION}"

echo "🔍 Extraction des symboles de débogage pour version ${VERSION}..."

# Créer les répertoires
mkdir -p "${OUTPUT_DIR}"
mkdir -p "${DESKTOP_DIR}"

# ───────────────────────────────────────────────────────────────
# 1. Fichier de mapping ProGuard/R8
# ───────────────────────────────────────────────────────────────
MAPPING_FILE="${BUILD_DIR}/build/outputs/mapping/release/mapping.txt"

if [ -f "${MAPPING_FILE}" ]; then
    echo "✅ Copie du fichier de mapping ProGuard..."
    cp "${MAPPING_FILE}" "${OUTPUT_DIR}/"
    cp "${MAPPING_FILE}" "${DESKTOP_DIR}/"
    ls -lh "${OUTPUT_DIR}/mapping.txt"
else
    echo "⚠️  Fichier mapping.txt introuvable à : ${MAPPING_FILE}"
    echo "   Recherche alternative..."
    find .buildozer -name "mapping.txt" -type f 2>/dev/null | head -1 | while read -r alt_path; do
        echo "   Trouvé : ${alt_path}"
        cp "${alt_path}" "${OUTPUT_DIR}/"
        cp "${alt_path}" "${DESKTOP_DIR}/"
    done
fi

# ───────────────────────────────────────────────────────────────
# 2. Symboles natifs (.so)
# ───────────────────────────────────────────────────────────────
NATIVE_SYMBOLS="${BUILD_DIR}/build/outputs/native-debug-symbols/release/native-debug-symbols.zip"

if [ -f "${NATIVE_SYMBOLS}" ]; then
    echo "✅ Copie des symboles natifs..."
    cp "${NATIVE_SYMBOLS}" "${OUTPUT_DIR}/"
    cp "${NATIVE_SYMBOLS}" "${DESKTOP_DIR}/"
    ls -lh "${OUTPUT_DIR}/native-debug-symbols.zip"
else
    echo "⚠️  Fichier native-debug-symbols.zip introuvable à : ${NATIVE_SYMBOLS}"
    echo "   Recherche alternative..."
    find .buildozer -name "native-debug-symbols.zip" -type f 2>/dev/null | head -1 | while read -r alt_path; do
        echo "   Trouvé : ${alt_path}"
        cp "${alt_path}" "${OUTPUT_DIR}/"
        cp "${alt_path}" "${DESKTOP_DIR}/"
    done
fi

# ───────────────────────────────────────────────────────────────
# 3. Copier aussi l'AAB signé pour faciliter l'upload
# ───────────────────────────────────────────────────────────────
AAB_FILE="bin/macartedetarot-${VERSION}-arm64-v8a_armeabi-v7a-release-signed.aab"

if [ -f "${AAB_FILE}" ]; then
    echo "✅ Copie de l'AAB signé..."
    cp "${AAB_FILE}" "${OUTPUT_DIR}/"
    cp "${AAB_FILE}" "${DESKTOP_DIR}/"
    ls -lh "${OUTPUT_DIR}/"*.aab
fi

# ───────────────────────────────────────────────────────────────
# 4. Résumé
# ───────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ Extraction terminée - Version ${VERSION}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📁 Fichiers locaux : ${OUTPUT_DIR}/"
ls -lh "${OUTPUT_DIR}/"
echo ""
echo "📁 Fichiers Windows : ${DESKTOP_DIR}/"
ls -lh "${DESKTOP_DIR}/"
echo ""
echo "🚀 Prochaine étape : Upload sur Play Console"
echo "   1. Uploader l'AAB"
echo "   2. Uploader mapping.txt (désobscurcissement)"
echo "   3. Uploader native-debug-symbols.zip (symboles natifs)"
echo ""
