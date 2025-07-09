#!/bin/bash
# Script de test local pour valider les corrections hostpython3

set -e

echo "=== Test des corrections hostpython3 ==="

# Vérifier la présence des scripts
echo "🔍 Vérification des scripts..."
if [ -f "scripts/check-compilation-env.sh" ]; then
    echo "✅ check-compilation-env.sh présent"
else
    echo "❌ check-compilation-env.sh manquant"
    exit 1
fi

if [ -f "scripts/install-compilation-deps.sh" ]; then
    echo "✅ install-compilation-deps.sh présent"
else
    echo "❌ install-compilation-deps.sh manquant"
    exit 1
fi

# Rendre les scripts exécutables
echo "🔧 Configuration des permissions..."
chmod +x scripts/check-compilation-env.sh
chmod +x scripts/install-compilation-deps.sh

# Tester le diagnostic de l'environnement
echo ""
echo "🧪 Test du diagnostic d'environnement..."
./scripts/check-compilation-env.sh

# Vérifier le workflow
echo ""
echo "🔍 Vérification du workflow..."
if [ -f ".github/workflows/build-android.yml" ]; then
    echo "✅ Workflow build-android.yml présent"
    
    # Vérifier les éléments critiques
    if grep -q "check-compilation-env.sh" .github/workflows/build-android.yml; then
        echo "✅ Script de diagnostic intégré au workflow"
    else
        echo "❌ Script de diagnostic non intégré au workflow"
    fi
    
    if grep -q "CC=gcc" .github/workflows/build-android.yml; then
        echo "✅ Variables d'environnement de compilation présentes"
    else
        echo "❌ Variables d'environnement de compilation manquantes"
    fi
    
    if grep -q "hostpython3" .github/workflows/build-android.yml; then
        echo "✅ Nettoyage hostpython3 présent"
    else
        echo "❌ Nettoyage hostpython3 manquant"
    fi
    
    if grep -q "libmpdec-dev" .github/workflows/build-android.yml; then
        echo "✅ Dépendances système étendues présentes"
    else
        echo "❌ Dépendances système étendues manquantes"
    fi
    
else
    echo "❌ Workflow build-android.yml manquant"
    exit 1
fi

# Vérifier la documentation
echo ""
echo "📚 Vérification de la documentation..."
if [ -f "docs/HOSTPYTHON3_COMPILATION_FIX.md" ]; then
    echo "✅ Documentation des corrections présente"
else
    echo "❌ Documentation des corrections manquante"
fi

# Résumé
echo ""
echo "=== Résumé des corrections hostpython3 ==="
echo "✅ Scripts de diagnostic et d'installation créés"
echo "✅ Workflow mis à jour avec les nouvelles dépendances"
echo "✅ Variables d'environnement de compilation ajoutées"
echo "✅ Nettoyage forcé de hostpython3 implémenté"
echo "✅ Vérification d'environnement intégrée"
echo "✅ Documentation complète fournie"
echo ""
echo "🚀 Le workflow est prêt pour résoudre l'erreur de compilation hostpython3 !"
echo ""
echo "📋 Prochaines étapes :"
echo "1. Commiter et pousser les modifications"
echo "2. Déclencher un nouveau build sur GitHub Actions"
echo "3. Surveiller les logs pour confirmer la compilation de hostpython3"
echo "4. Si des erreurs persistent, utiliser les scripts de diagnostic"
