#!/bin/bash

echo "🧹 Nettoyage des workflows GitHub Actions"

WORKFLOW_DIR=".github/workflows"

# Vérifier que nous sommes dans le bon répertoire
if [ ! -d "$WORKFLOW_DIR" ]; then
    echo "❌ Répertoire $WORKFLOW_DIR non trouvé"
    exit 1
fi

echo "📁 Workflows actuels:"
ls -la "$WORKFLOW_DIR"/*.yml 2>/dev/null || echo "Aucun fichier .yml trouvé"

# Supprimer les fichiers en doublon ou obsolètes
echo ""
echo "🗑️ Suppression des fichiers obsolètes..."

# Supprimer build-triggers.yml s'il est vide ou inutile
if [ -f ".github/build-triggers.yml" ]; then
    if [ ! -s ".github/build-triggers.yml" ] || [ "$(wc -l < .github/build-triggers.yml)" -lt 3 ]; then
        echo "   Suppression de build-triggers.yml (vide ou minimal)"
        rm -f ".github/build-triggers.yml"
    fi
fi

# Supprimer build-android-optimized.yml si il existe
if [ -f "$WORKFLOW_DIR/build-android-optimized.yml" ]; then
    echo "   Suppression de build-android-optimized.yml (doublon)"
    rm -f "$WORKFLOW_DIR/build-android-optimized.yml"
fi

# Supprimer d'autres fichiers temporaires
rm -f "$WORKFLOW_DIR"/*.backup 2>/dev/null || true
rm -f "$WORKFLOW_DIR"/*.tmp 2>/dev/null || true

echo ""
echo "✅ Nettoyage terminé"
echo "📁 Workflows finaux:"
ls -la "$WORKFLOW_DIR"/*.yml 2>/dev/null || echo "Aucun fichier .yml trouvé"

echo ""
echo "📋 Workflows actifs:"
for workflow in "$WORKFLOW_DIR"/*.yml; do
    if [ -f "$workflow" ]; then
        echo "   - $(basename "$workflow")"
        # Afficher le nom du workflow
        name=$(grep -m1 "^name:" "$workflow" 2>/dev/null | sed 's/name: *//' | tr -d '"')
        if [ -n "$name" ]; then
            echo "     Nom: $name"
        fi
    fi
done
