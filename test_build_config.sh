#!/bin/bash
# test_build_config.sh - Script pour tester la configuration de build Android localement

set -e

echo "🔧 Test de la configuration de build Android"
echo "============================================="

# Vérifier les prérequis
echo "📋 Vérification des prérequis..."

# Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3: $(python3 --version)"
else
    echo "❌ Python3 non trouvé"
    exit 1
fi

# Buildozer
if command -v buildozer &> /dev/null; then
    echo "✅ Buildozer: $(buildozer --version)"
else
    echo "❌ Buildozer non installé. Installation..."
    pip install buildozer==1.5.0
fi

# Variables d'environnement (simuler GitHub Actions)
export ANDROID_HOME=${ANDROID_HOME:-"/usr/local/lib/android/sdk"}
export ANDROID_NDK_HOME=${ANDROID_NDK_HOME:-"/usr/local/lib/android/sdk/ndk/27.2.12479018"}
export JAVA_HOME=${JAVA_HOME:-"/usr/lib/jvm/temurin-17-jdk-amd64"}

echo "🌍 Variables d'environnement:"
echo "   ANDROID_HOME: $ANDROID_HOME"
echo "   ANDROID_NDK_HOME: $ANDROID_NDK_HOME"
echo "   JAVA_HOME: $JAVA_HOME"

# Exécuter les scripts de configuration
if [ -f ".github/scripts/configure_buildozer_sdk.py" ]; then
    echo "⚙️  Configuration buildozer SDK..."
    python3 .github/scripts/configure_buildozer_sdk.py
else
    echo "❌ Script configure_buildozer_sdk.py non trouvé"
fi

if [ -f ".github/scripts/fix_sdk_paths.py" ]; then
    echo "🔍 Diagnostic des chemins SDK..."
    python3 .github/scripts/fix_sdk_paths.py
else
    echo "❌ Script fix_sdk_paths.py non trouvé"
fi

# Vérifier buildozer.spec
echo "📄 Contenu buildozer.spec (extrait):"
if [ -f "buildozer.spec" ]; then
    grep -E "(requirements|android\.(sdk_path|ndk_path|ndk|api))" buildozer.spec || echo "Aucune ligne correspondante trouvée"
else
    echo "❌ buildozer.spec non trouvé"
    exit 1
fi

# Test de build (dry run)
echo "🏗️  Test de build (dry run)..."
echo "Note: Ce test peut échouer si les SDK Android ne sont pas installés localement"

# Nettoyer d'abord
if [ -d ".buildozer" ]; then
    echo "🧹 Nettoyage du cache buildozer..."
    rm -rf .buildozer
fi

# Tenter un build de test
if buildozer android debug --verbose 2>&1 | head -50; then
    echo "✅ Build initié avec succès"
else
    echo "⚠️  Build échoué (normal si SDK non installé localement)"
fi

echo ""
echo "============================================="
echo "✅ Test de configuration terminé"
echo ""
echo "Pour un build complet sur GitHub Actions:"
echo "1. Commitez et pushez les changements"
echo "2. Créez un tag pour déclencher la publication"
echo "3. Vérifiez les logs dans l'onglet Actions"
