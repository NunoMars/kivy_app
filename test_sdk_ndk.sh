#!/bin/bash

# Script de test pour valider la disponibilité du SDK/NDK pour buildozer

echo "=== Test de disponibilité SDK/NDK pour Buildozer ==="

# Simuler les variables d'environnement
export ANDROID_HOME="/usr/local/lib/android/sdk"
export NDK_VERSION="25.2.9519653"

echo "1. Variables d'environnement:"
echo "   ANDROID_HOME: $ANDROID_HOME"
echo "   NDK_VERSION: $NDK_VERSION"

echo ""
echo "2. Vérification des répertoires source:"
echo "   SDK: $(ls -d $ANDROID_HOME 2>/dev/null && echo '✅ Exists' || echo '❌ Missing')"
echo "   NDK: $(ls -d $ANDROID_HOME/ndk/$NDK_VERSION 2>/dev/null && echo '✅ Exists' || echo '❌ Missing')"

echo ""
echo "3. Simulation de copie vers buildozer:"
mkdir -p ~/.test_buildozer/android/platform

# Test de copie SDK
if [ -d "$ANDROID_HOME" ]; then
    echo "   📁 Copying SDK... (simulated)"
    echo "   ✅ SDK copy would succeed"
else
    echo "   ❌ SDK copy would fail - source not found"
fi

# Test de copie NDK
if [ -d "$ANDROID_HOME/ndk/$NDK_VERSION" ]; then
    echo "   📁 Copying NDK... (simulated)"
    echo "   ✅ NDK copy would succeed"
else
    echo "   ❌ NDK copy would fail - source not found"
fi

echo ""
echo "4. Emplacements attendus par buildozer:"
echo "   SDK target: ~/.buildozer/android/platform/android-sdk"
echo "   NDK target: ~/.buildozer/android/platform/android-ndk-r$NDK_VERSION"
echo "   NDK alt target: ~/.buildozer/android/platform/android-ndk-r25b"

# Nettoyer
rm -rf ~/.test_buildozer

echo ""
echo "=== Test terminé ==="
