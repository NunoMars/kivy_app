#!/bin/bash

# Script de correction rapide pour le problème sdkmanager buildozer
# Ce script crée les liens symboliques nécessaires pour que buildozer trouve sdkmanager

echo "🔧 Correction du problème sdkmanager buildozer"
echo "=============================================="

# Variables
ANDROID_HOME="${ANDROID_HOME:-/usr/local/lib/android/sdk}"
BUILDOZER_SDK="$HOME/.buildozer/android/platform/android-sdk"
TOOLS_DIR="$BUILDOZER_SDK/tools/bin"

echo "📍 Chemins utilisés:"
echo "  ANDROID_HOME: $ANDROID_HOME"
echo "  BUILDOZER_SDK: $BUILDOZER_SDK"
echo "  TOOLS_DIR: $TOOLS_DIR"

# Vérifier que ANDROID_HOME existe
if [ ! -d "$ANDROID_HOME" ]; then
    echo "❌ ANDROID_HOME non trouvé: $ANDROID_HOME"
    exit 1
fi

# Vérifier que le SDK buildozer existe
if [ ! -d "$BUILDOZER_SDK" ]; then
    echo "❌ SDK buildozer non trouvé: $BUILDOZER_SDK"
    echo "💡 Suggestion: Copier le SDK avec: cp -r $ANDROID_HOME $BUILDOZER_SDK"
    exit 1
fi

echo ""
echo "🔧 Création de la structure des outils..."

# Créer le répertoire tools/bin
mkdir -p "$TOOLS_DIR"

# Fonction pour créer un lien symbolique
create_symlink() {
    local tool_name="$1"
    local source_path="$ANDROID_HOME/cmdline-tools/latest/bin/$tool_name"
    local target_path="$TOOLS_DIR/$tool_name"
    
    if [ -f "$source_path" ]; then
        if [ -L "$target_path" ]; then
            echo "  🔄 Mise à jour du lien: $tool_name"
            rm "$target_path"
        elif [ -f "$target_path" ]; then
            echo "  ⚠️ Fichier existant remplacé: $tool_name"
            rm "$target_path"
        else
            echo "  ✅ Création du lien: $tool_name"
        fi
        
        ln -sf "$source_path" "$target_path"
        
        if [ -x "$target_path" ]; then
            echo "    ✅ Lien créé et exécutable"
        else
            echo "    ❌ Problème avec le lien"
        fi
    else
        echo "  ❌ Source non trouvée: $source_path"
    fi
}

# Créer les liens pour les outils essentiels
echo "🔗 Création des liens symboliques..."
create_symlink "sdkmanager"
create_symlink "avdmanager"

# Vérification finale
echo ""
echo "🔍 Vérification finale..."

if [ -x "$TOOLS_DIR/sdkmanager" ]; then
    echo "✅ sdkmanager est accessible"
    echo "  Chemin: $TOOLS_DIR/sdkmanager"
    echo "  Version: $($TOOLS_DIR/sdkmanager --version 2>/dev/null || echo 'Erreur lors de la vérification')"
else
    echo "❌ sdkmanager n'est pas accessible"
    echo "💡 Buildozer va probablement échouer"
fi

if [ -x "$TOOLS_DIR/avdmanager" ]; then
    echo "✅ avdmanager est accessible"
else
    echo "⚠️ avdmanager n'est pas accessible"
fi

echo ""
echo "📋 Contenu du répertoire tools/bin:"
ls -la "$TOOLS_DIR" 2>/dev/null || echo "Répertoire vide"

echo ""
echo "✅ Correction terminée"
echo ""
echo "💡 Pour tester:"
echo "  $TOOLS_DIR/sdkmanager --version"
echo "  buildozer android debug"
