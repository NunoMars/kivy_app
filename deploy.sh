#!/bin/bash
# Script de déploiement automatique pour Ma Carte de Tarot
# Usage: ./deploy.sh [version]

set -e

# Configuration
PROJECT_NAME="Ma Carte de Tarot"
BRANCH="main"
VERSION=${1:-"v1.0.0"}

echo "🚀 Déploiement $PROJECT_NAME - Version $VERSION"
echo "=================================================="

# Vérifier que nous sommes sur la bonne branche
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo "❌ Vous devez être sur la branche $BRANCH"
    echo "   Branche actuelle: $CURRENT_BRANCH"
    exit 1
fi

# Vérifier que le workspace est propre
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Des changements non committés détectés"
    echo "📋 Fichiers modifiés:"
    git status --short
    echo ""
    read -p "Continuer quand même? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Déploiement annulé"
        exit 1
    fi
fi

# Validation finale
echo "🔍 Validation finale du pipeline..."
if python validate_aab_workflow.py; then
    echo "✅ Validation réussie"
else
    echo "❌ Validation échouée"
    exit 1
fi

# Commit et push
echo "📤 Push du code..."
git add .
git commit -m "feat: ready for production deployment - AAB pipeline finalized" || echo "Nothing to commit"
git push origin $BRANCH

echo "✅ Code pushé vers $BRANCH"

# Attendre un peu pour que les hooks Git se déclenchent
echo "⏳ Attente de synchronisation GitHub..."
sleep 3

# Créer et pousser le tag
echo "🏷️  Création du tag $VERSION..."
if git tag -l | grep -q "^$VERSION$"; then
    echo "⚠️  Le tag $VERSION existe déjà"
    read -p "Forcer la recréation? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d $VERSION
        git push origin :refs/tags/$VERSION
    else
        echo "❌ Déploiement annulé"
        exit 1
    fi
fi

git tag -a $VERSION -m "Release $VERSION - AAB ready for Google Play Store

🎯 Features:
- App Bundle (AAB) generation for Google Play Store
- Automated signing with production keys
- Compatible with Ubuntu 22.04 CI/CD
- Optimized build pipeline without libffi/autotools errors

🔧 Technical:
- Kivy 2.2.0 with optimized dependencies  
- Android NDK 25c for SDL2 compatibility
- API Level 33 for modern Android support
- Automated GitHub Actions workflow

🚀 Ready for Google Play Store publication!"

git push origin $VERSION

echo "✅ Tag $VERSION créé et poussé"

# Afficher les informations de déploiement
echo ""
echo "🎉 DÉPLOIEMENT TERMINÉ !"
echo "========================"
echo "📋 Informations:"
echo "   Version: $VERSION"
echo "   Branche: $BRANCH"
echo "   Tag: $VERSION"
echo ""
echo "🔗 Liens utiles:"
echo "   GitHub Actions: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^.]*\).*/\1/')/actions"
echo "   Releases: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^.]*\).*/\1/')/releases"
echo ""
echo "⏳ Le build GitHub Actions va démarrer automatiquement..."
echo "📱 L'AAB sera disponible dans les artifacts et releases"
echo ""
echo "🔑 N'oubliez pas de configurer les secrets GitHub pour la signature de production:"
echo "   - ANDROID_KEYSTORE_BASE64"
echo "   - KEYSTORE_PASSWORD"  
echo "   - KEY_ALIAS"
echo "   - KEY_PASSWORD"
echo "   - GOOGLE_PLAY_SERVICE_ACCOUNT (pour publication automatique)"
echo ""
echo "🎮 Ma Carte de Tarot est prête pour Google Play Store ! 🔮"
