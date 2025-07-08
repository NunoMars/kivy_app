#!/bin/bash

# Script de diagnostic et correction des problèmes buildozer/p4a

echo "🔍 Diagnostic des problèmes buildozer/p4a"
echo "=============================================="

# 1. Vérifier les chemins des outils
echo "📍 Vérification des chemins des outils"
echo "ANDROID_HOME: ${ANDROID_HOME:-'Non défini'}"
echo "ANDROID_SDK_ROOT: ${ANDROID_SDK_ROOT:-'Non défini'}"
echo "ANDROID_NDK_HOME: ${ANDROID_NDK_HOME:-'Non défini'}"

# 2. Vérifier la présence des outils
echo ""
echo "🔧 Vérification de la présence des outils"
TOOLS_TO_CHECK=("sdkmanager" "adb" "javac" "keytool" "git" "cython" "buildozer")

for tool in "${TOOLS_TO_CHECK[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
        echo "✅ $tool: $(which $tool)"
    else
        echo "❌ $tool: Non trouvé"
    fi
done

# 3. Vérifier les versions NDK
echo ""
echo "📦 Versions NDK disponibles"
if [ -n "$ANDROID_HOME" ] && [ -d "$ANDROID_HOME/ndk" ]; then
    echo "NDK disponibles dans $ANDROID_HOME/ndk:"
    ls -la "$ANDROID_HOME/ndk" 2>/dev/null || echo "Aucun NDK trouvé"
else
    echo "Répertoire NDK non trouvé"
fi

# 4. Vérifier les copies buildozer
echo ""
echo "🏗️ Vérification des copies buildozer"
BUILDOZER_PATH="$HOME/.buildozer/android/platform"
if [ -d "$BUILDOZER_PATH" ]; then
    echo "SDK buildozer: $(ls -la $BUILDOZER_PATH/android-sdk 2>/dev/null || echo 'Non trouvé')"
    echo "NDK buildozer: $(ls -la $BUILDOZER_PATH/android-ndk* 2>/dev/null || echo 'Non trouvé')"
else
    echo "Répertoire buildozer non trouvé"
fi

# 5. Vérifier les outils SDK
echo ""
echo "🛠️ Vérification des outils SDK"
SDK_TOOLS_PATHS=(
    "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager"
    "$ANDROID_HOME/platform-tools/adb"
    "$BUILDOZER_PATH/android-sdk/cmdline-tools/latest/bin/sdkmanager"
    "$BUILDOZER_PATH/android-sdk/tools/bin/sdkmanager"
)

for tool_path in "${SDK_TOOLS_PATHS[@]}"; do
    if [ -f "$tool_path" ]; then
        echo "✅ $tool_path"
    else
        echo "❌ $tool_path"
    fi
done

# 6. Recommandations
echo ""
echo "💡 Recommandations"
echo "=================="

# Vérifier si sdkmanager est accessible
if [ -f "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" ]; then
    echo "✅ sdkmanager disponible dans le chemin principal"
else
    echo "⚠️ sdkmanager non trouvé - créer des liens symboliques"
fi

# Vérifier la version NDK recommandée
if [ -d "$ANDROID_HOME/ndk" ]; then
    NDK_COUNT=$(ls -1 "$ANDROID_HOME/ndk" 2>/dev/null | wc -l)
    echo "📊 Nombre de NDK installés: $NDK_COUNT"
    if [ "$NDK_COUNT" -gt 1 ]; then
        echo "⚠️ Plusieurs NDK installés - utiliser android.ndk_path dans buildozer.spec"
    fi
fi

# 7. Suggestions de correction
echo ""
echo "🔧 Suggestions de correction"
echo "============================="

cat << 'EOF'
1. Pour corriger les chemins sdkmanager:
   mkdir -p ~/.buildozer/android/platform/android-sdk/tools/bin
   ln -sf ../../../cmdline-tools/latest/bin/* ~/.buildozer/android/platform/android-sdk/tools/bin/

2. Pour forcer l'utilisation d'un NDK spécifique:
   Ajouter dans buildozer.spec:
   android.ndk_path = ~/.buildozer/android/platform/android-ndk-r26.3.11579264

3. Pour éviter les téléchargements:
   android.sdk_path = ~/.buildozer/android/platform/android-sdk
   android.ndk_path = ~/.buildozer/android/platform/android-ndk-r26c

4. Pour activer les logs détaillés:
   BUILDOZER_LOG_LEVEL=2 buildozer android debug -v
EOF

echo ""
echo "✅ Diagnostic terminé"
