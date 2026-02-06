#!/bin/bash
# Script de rebuild complet pour support pages 16 Ko

echo "🧹 Nettoyage complet des builds précédents..."
buildozer android clean

echo "🗑️ Suppression du cache p4a..."
rm -rf ~/.buildozer/android/platform/build-*
rm -rf .buildozer/android/platform/build-*

echo "🔨 Rebuild complet avec flags 16KB..."
buildozer android release

echo "✅ Build terminé ! Vérifiez le fichier .aab généré"
