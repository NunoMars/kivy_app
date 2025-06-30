#!/bin/bash

# Script de préparation pour publication sur les stores
# Usage: ./prepare_store_release.sh

echo "🚀 Préparation de l'app Tarot pour publication..."

# 1. Vérifier que nous sommes dans le bon répertoire
if [ ! -f "main.py" ]; then
    echo "❌ Erreur: main.py non trouvé. Êtes-vous dans le bon répertoire ?"
    exit 1
fi

# 2. Vérifier buildozer.spec
if [ ! -f "buildozer.spec" ]; then
    echo "❌ Erreur: buildozer.spec non trouvé"
    exit 1
fi

echo "✅ Fichiers de base trouvés"

# 3. Mettre à jour les métadonnées dans buildozer.spec
echo "📝 Mise à jour des métadonnées..."

# Demander la version
read -p "Version de l'app (ex: 1.0.0): " VERSION
if [ -z "$VERSION" ]; then
    VERSION="1.0.0"
fi

# Mettre à jour buildozer.spec
sed -i "s/version = .*/version = $VERSION/" buildozer.spec
sed -i "s/version.regex = .*/version.regex = __version__ = ['\"]([^'\"]*)['\"]/" buildozer.spec
sed -i "s/version.filename = .*/version.filename = %(source.dir)s\/main.py/" buildozer.spec

echo "✅ Version mise à jour: $VERSION"

# 4. Vérifier les requirements
echo "🔍 Vérification des requirements..."
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt trouvé"
else
    echo "⚠️  requirements.txt manquant, création..."
    cat > requirements.txt << EOF
kivy==2.2.0
pillow==10.0.0
EOF
fi

# 5. Vérifier les images nécessaires
echo "🖼️  Vérification des assets..."

REQUIRED_IMAGES=(
    "tarot_img/bg.jpg"
    "tarot_img/Back.jpg"
    "tarot_img/tapis.ico"
)

for img in "${REQUIRED_IMAGES[@]}"; do
    if [ -f "$img" ]; then
        echo "✅ $img trouvé"
    else
        echo "❌ $img manquant"
    fi
done

# 6. Créer le fichier de version dans main.py
echo "📄 Mise à jour de la version dans main.py..."
sed -i "1s/.*/__version__ = \"$VERSION\"/" main.py

# 7. Test de compilation locale (optionnel)
read -p "Voulez-vous tester la compilation locale ? (y/N): " TEST_BUILD
if [ "$TEST_BUILD" = "y" ] || [ "$TEST_BUILD" = "Y" ]; then
    echo "🔨 Test de compilation..."
    if command -v buildozer &> /dev/null; then
        buildozer android debug
        if [ $? -eq 0 ]; then
            echo "✅ Compilation réussie"
        else
            echo "❌ Erreur de compilation"
            exit 1
        fi
    else
        echo "⚠️  Buildozer non installé, ignoré"
    fi
fi

# 8. Créer le commit et tag Git
echo "📦 Préparation Git..."

# Vérifier si git est initialisé
if [ ! -d ".git" ]; then
    echo "🔧 Initialisation Git..."
    git init
fi

# Ajouter tous les fichiers
git add .

# Créer le commit
git commit -m "Préparation version $VERSION pour publication"

# Créer le tag
git tag "v$VERSION"

echo "✅ Tag v$VERSION créé"

# 9. Instructions finales
echo ""
echo "🎯 PRÊT POUR PUBLICATION !"
echo ""
echo "Prochaines étapes :"
echo "1. Pousser vers GitHub:"
echo "   git remote add origin https://github.com/VOTRE_USERNAME/tarot-app.git"
echo "   git push -u origin main"
echo "   git push origin v$VERSION"
echo ""
echo "2. GitHub Actions va automatiquement:"
echo "   - Compiler l'APK"
echo "   - Uploader sur Google Play Console"
echo ""
echo "3. Aller sur Google Play Console pour finaliser la publication"
echo ""
echo "📱 Fichiers générés:"
echo "   - Version: $VERSION"
echo "   - Tag Git: v$VERSION"
echo "   - buildozer.spec mis à jour"
echo ""
echo "🚀 Bonne chance pour votre publication !"
