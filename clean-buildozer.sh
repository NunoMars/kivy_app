#!/bin/bash

echo "=== Nettoyage agressif du cache buildozer ==="

# Supprimer tous les builds existants avec différentes architectures
echo "Suppression des builds multi-architectures..."
rm -rf .buildozer/android/platform/build-arm64-v8a_armeabi-v7a 2>/dev/null || echo "Multi-arch build pas trouvé"
rm -rf .buildozer/android/platform/build-armeabi-v7a 2>/dev/null || echo "Build armeabi-v7a pas trouvé"
rm -rf .buildozer/android/platform/build-x86 2>/dev/null || echo "Build x86 pas trouvé"
rm -rf .buildozer/android/platform/build-x86_64 2>/dev/null || echo "Build x86_64 pas trouvé"

# Supprimer tous les dossiers de build
echo "Suppression de tous les dossiers de build..."
rm -rf .buildozer/android/platform/build-* 2>/dev/null || echo "Aucun dossier de build trouvé"

# Supprimer le dossier bin
echo "Suppression du dossier bin..."
rm -rf bin/ 2>/dev/null || echo "Dossier bin pas trouvé"

# Nettoyer avec buildozer
echo "Nettoyage buildozer..."
buildozer android clean || echo "Nettoyage buildozer échoué, on continue..."

# Vérifier la configuration
echo "=== Vérification de la configuration ==="
echo "Architecture configurée dans buildozer.spec:"
grep "android.archs" buildozer.spec || echo "❌ android.archs non trouvé"

echo "API configurée:"
grep "android.api" buildozer.spec || echo "❌ android.api non trouvé"

echo "NDK configuré:"
grep "android.ndk" buildozer.spec || echo "❌ android.ndk non trouvé"

echo "✅ Nettoyage terminé!"
echo "Vous pouvez maintenant lancer: buildozer android debug"
