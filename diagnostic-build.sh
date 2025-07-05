#!/bin/bash

# Script de diagnostic pour builds Android CI/CD
echo "🔍 DIAGNOSTIC BUILD ANDROID CI/CD"
echo "================================="

echo "📅 Date: $(date)"
echo "🏗️ Architecture: $(uname -m)"
echo "🐧 OS: $(cat /etc/os-release | grep PRETTY_NAME)"

echo ""
echo "☕ JAVA ENVIRONMENT"
echo "-------------------"
echo "JAVA_HOME: $JAVA_HOME"
which java && java -version
which javac && javac -version

echo ""
echo "📱 ANDROID ENVIRONMENT"
echo "----------------------"
echo "ANDROID_HOME: $ANDROID_HOME"
echo "ANDROID_NDK_HOME: $ANDROID_NDK_HOME"
echo "ANDROIDNDK: $ANDROIDNDK"

echo ""
echo "📂 Android SDK Structure:"
ls -la $ANDROID_HOME/ 2>/dev/null || echo "❌ ANDROID_HOME not found"

echo ""
echo "🔧 NDK Versions Available:"
ls -la $ANDROID_HOME/ndk/ 2>/dev/null || echo "❌ No NDKs found"

echo ""
echo "🛠️ SDK Tools:"
ls -la $ANDROID_HOME/tools/bin/ 2>/dev/null || echo "❌ tools/bin not found"
ls -la $ANDROID_HOME/cmdline-tools/latest/bin/ 2>/dev/null || echo "❌ cmdline-tools not found"

echo ""
echo "🏗️ BUILD TOOLS:"
ls -la $ANDROID_HOME/build-tools/ 2>/dev/null || echo "❌ build-tools not found"

echo ""
echo "📦 PLATFORMS:"
ls -la $ANDROID_HOME/platforms/ 2>/dev/null || echo "❌ platforms not found"

echo ""
echo "🐍 PYTHON ENVIRONMENT"
echo "---------------------"
echo "Python: $(which python3)"
python3 --version
echo "Pip: $(which pip)"
pip --version

echo ""
echo "🔧 BUILDOZER ENVIRONMENT"
echo "------------------------"
echo "Buildozer: $(which buildozer)"
buildozer --version 2>/dev/null || echo "❌ Buildozer not found"

echo ""
echo "🔍 CYTHON"
echo "---------"
echo "Cython: $(which cython)"
cython --version 2>/dev/null || echo "❌ Cython not found"

echo ""
echo "💾 DISK SPACE"
echo "-------------"
df -h

echo ""
echo "🧠 MEMORY"
echo "---------"
free -h

echo ""
echo "🔍 ENVIRONMENT VARIABLES"
echo "------------------------"
env | grep -E "(ANDROID|JAVA|GRADLE)" | sort

echo ""
echo "⚙️ BUILDOZER CONFIGURATION CHECK"
echo "--------------------------------"
if [ -f "buildozer.spec" ]; then
    echo "✅ buildozer.spec trouvé"
    
    echo ""
    echo "🏗️ Architecture Configuration:"
    grep -n "android.arch" buildozer.spec || echo "❌ Aucune configuration d'architecture trouvée"
    
    echo ""
    echo "📱 Android API Configuration:"
    grep -n "android.api" buildozer.spec || echo "❌ Aucune configuration d'API trouvée"
    
    echo ""
    echo "🔧 NDK Configuration:"
    grep -n "android.ndk" buildozer.spec || echo "❌ Aucune configuration NDK trouvée"
    
    echo ""
    echo "🔍 Conflits potentiels (duplications):"
    duplicates=$(grep -c "android.archs" buildozer.spec)
    if [ "$duplicates" -gt 1 ]; then
        echo "❌ ATTENTION: $duplicates définitions de android.archs trouvées!"
        grep -n "android.archs" buildozer.spec
    else
        echo "✅ Une seule définition d'architecture trouvée"
    fi
else
    echo "❌ buildozer.spec non trouvé!"
fi

echo ""
echo "🗂️ CACHE BUILDOZER CHECK"
echo "------------------------"
if [ -d ".buildozer" ]; then
    echo "📁 Cache buildozer existe"
    echo "Taille du cache: $(du -sh .buildozer 2>/dev/null || echo 'Erreur')"
    
    echo ""
    echo "🏗️ Builds existants:"
    ls -la .buildozer/android/platform/ 2>/dev/null | grep "build-" || echo "Aucun build trouvé"
    
    # Détecter les builds multi-architectures problématiques
    if ls .buildozer/android/platform/build-*_* 2>/dev/null; then
        echo "⚠️ ATTENTION: Builds multi-architectures détectés!"
        ls -la .buildozer/android/platform/build-*_* 2>/dev/null
        echo "💡 Recommandation: Nettoyer avec 'rm -rf .buildozer/android/platform/build-*_*'"
    fi
else
    echo "📁 Aucun cache buildozer trouvé (première compilation)"
fi

echo ""
echo "✅ DIAGNOSTIC COMPLETE"
echo "======================"
