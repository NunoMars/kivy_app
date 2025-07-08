#!/bin/bash

# Script de test pour vérifier la configuration buildozer locale
# Simule les étapes du workflow GitHub Actions

echo "🧪 Test de Configuration Buildozer Local"
echo "========================================"

# Vérifier les variables d'environnement
echo "📋 Variables d'environnement:"
echo "  ANDROID_HOME: ${ANDROID_HOME:-'Non défini'}"
echo "  ANDROID_SDK_ROOT: ${ANDROID_SDK_ROOT:-'Non défini'}"
echo "  ANDROID_NDK_HOME: ${ANDROID_NDK_HOME:-'Non défini'}"

# Vérifier les outils de base
echo ""
echo "🔧 Vérification des outils de base:"
TOOLS=("python" "java" "git" "buildozer" "cython")
for tool in "${TOOLS[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
        echo "  ✅ $tool: $(which $tool)"
    else
        echo "  ❌ $tool: Non trouvé"
    fi
done

# Vérifier la structure buildozer
echo ""
echo "📁 Structure buildozer:"
BUILDOZER_DIR="$HOME/.buildozer/android/platform"
if [ -d "$BUILDOZER_DIR" ]; then
    echo "  ✅ Répertoire buildozer: $BUILDOZER_DIR"
    echo "  📦 Contenu:"
    ls -la "$BUILDOZER_DIR" 2>/dev/null || echo "    Vide"
else
    echo "  ❌ Répertoire buildozer: Non trouvé"
fi

# Vérifier les SDK/NDK
echo ""
echo "🔍 Vérification SDK/NDK:"
SDK_PATH="$BUILDOZER_DIR/android-sdk"
if [ -d "$SDK_PATH" ]; then
    echo "  ✅ SDK buildozer: $SDK_PATH"
    
    # Vérifier sdkmanager
    SDKMANAGER_PATH="$SDK_PATH/tools/bin/sdkmanager"
    if [ -x "$SDKMANAGER_PATH" ]; then
        echo "  ✅ sdkmanager: $SDKMANAGER_PATH"
        echo "    Version: $($SDKMANAGER_PATH --version 2>/dev/null || echo 'Erreur')"
    else
        echo "  ❌ sdkmanager: Non trouvé ou non exécutable"
    fi
else
    echo "  ❌ SDK buildozer: Non trouvé"
fi

# Vérifier NDK
NDK_PATHS=(
    "$BUILDOZER_DIR/android-ndk-r26.3.11579264"
    "$BUILDOZER_DIR/android-ndk-r26c"
)

echo ""
echo "🔧 Vérification NDK:"
for ndk_path in "${NDK_PATHS[@]}"; do
    if [ -d "$ndk_path" ]; then
        echo "  ✅ NDK: $ndk_path"
        echo "    Taille: $(du -sh "$ndk_path" 2>/dev/null | cut -f1)"
    else
        echo "  ❌ NDK: $ndk_path - Non trouvé"
    fi
done

# Test de buildozer
echo ""
echo "🏗️ Test buildozer:"
if command -v buildozer >/dev/null 2>&1; then
    echo "  Version buildozer: $(buildozer --version 2>/dev/null || echo 'Erreur')"
    
    # Test de configuration
    if [ -f "buildozer.spec" ]; then
        echo "  ✅ buildozer.spec trouvé"
        echo "  📋 Test de configuration..."
        
        # Dry run pour vérifier la configuration
        timeout 30 buildozer android debug --dry-run 2>/dev/null && echo "  ✅ Configuration valide" || echo "  ⚠️ Problème de configuration"
    else
        echo "  ❌ buildozer.spec non trouvé"
    fi
else
    echo "  ❌ buildozer non installé"
fi

# Recommandations
echo ""
echo "💡 Recommandations:"
echo "=================="

if [ -z "$ANDROID_HOME" ]; then
    echo "⚠️ Définir ANDROID_HOME"
    echo "   export ANDROID_HOME=/path/to/android/sdk"
fi

if [ ! -d "$BUILDOZER_DIR" ]; then
    echo "⚠️ Créer la structure buildozer"
    echo "   mkdir -p $BUILDOZER_DIR"
fi

if [ ! -x "$BUILDOZER_DIR/android-sdk/tools/bin/sdkmanager" ]; then
    echo "⚠️ Corriger les liens sdkmanager"
    echo "   bash scripts/fix-sdkmanager.sh"
fi

echo ""
echo "🎯 Résumé:"
echo "========="

# Calculer le score
score=0
total=5

command -v buildozer >/dev/null 2>&1 && ((score++))
[ -n "$ANDROID_HOME" ] && ((score++))
[ -d "$BUILDOZER_DIR" ] && ((score++))
[ -d "$SDK_PATH" ] && ((score++))
[ -x "$BUILDOZER_DIR/android-sdk/tools/bin/sdkmanager" ] && ((score++))

echo "Score: $score/$total"

if [ $score -eq $total ]; then
    echo "✅ Configuration parfaite ! Prêt pour le build."
elif [ $score -ge 3 ]; then
    echo "⚠️ Configuration correcte avec quelques problèmes mineurs."
else
    echo "❌ Configuration incomplète. Corrections nécessaires."
fi

echo ""
echo "🔗 Commandes utiles:"
echo "  - Corriger sdkmanager: bash scripts/fix-sdkmanager.sh"
echo "  - Diagnostic complet: bash scripts/diagnose-buildozer.sh"
echo "  - Build test: buildozer android debug"
