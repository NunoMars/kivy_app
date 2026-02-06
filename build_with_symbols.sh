#!/bin/bash
# Script pour générer l'AAB avec symboles de débogage et mapping ProGuard

set -e  # Arrêter en cas d'erreur

echo "🔨 Build avec symboles de débogage natifs et ProGuard mapping..."
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
PROJECT_DIR="/home/loupy/kivy_app"
BUILD_DIR="$PROJECT_DIR/.buildozer/android/platform/build-arm64-v8a/dists/macartedetarot"
BIN_DIR="$PROJECT_DIR/bin"
DESKTOP_DIR="/mnt/c/Users/loupy/Desktop"

cd "$PROJECT_DIR"

echo -e "${BLUE}📦 Étape 1: Clean et rebuild AAB...${NC}"
./rebuild_16kb.sh

echo ""
echo -e "${BLUE}📁 Étape 2: Recherche des symboles de débogage natifs...${NC}"

# Chercher les symboles natifs (.so avec debug info)
SYMBOLS_DIR="$BUILD_DIR/build/intermediates/merged_native_libs/release/out/lib"
if [ -d "$SYMBOLS_DIR" ]; then
    echo -e "${GREEN}✅ Symboles natifs trouvés dans: $SYMBOLS_DIR${NC}"
    
    # Créer un zip avec les symboles
    SYMBOLS_ZIP="$BIN_DIR/native-debug-symbols-2.41.zip"
    cd "$SYMBOLS_DIR"
    zip -r "$SYMBOLS_ZIP" arm64-v8a/
    echo -e "${GREEN}✅ Symboles natifs zippés: $SYMBOLS_ZIP${NC}"
    cd "$PROJECT_DIR"
else
    echo -e "${YELLOW}⚠️  Symboles natifs non trouvés (peut nécessiter configuration Gradle)${NC}"
fi

echo ""
echo -e "${BLUE}📁 Étape 3: Recherche du mapping ProGuard...${NC}"

# Chercher le mapping.txt de ProGuard/R8
MAPPING_FILE=$(find "$BUILD_DIR/build/outputs/mapping" -name "mapping.txt" 2>/dev/null | head -1)
if [ -n "$MAPPING_FILE" ]; then
    echo -e "${GREEN}✅ Mapping ProGuard trouvé: $MAPPING_FILE${NC}"
    cp "$MAPPING_FILE" "$BIN_DIR/mapping-2.41.txt"
    echo -e "${GREEN}✅ Mapping copié: $BIN_DIR/mapping-2.41.txt${NC}"
else
    echo -e "${YELLOW}⚠️  Mapping ProGuard non trouvé${NC}"
    echo "   Vérifier que minifyEnabled est true dans build.gradle"
fi

echo ""
echo -e "${BLUE}📦 Étape 4: Signature de l'AAB...${NC}"

# Copier et signer l'AAB
AAB_SOURCE="$BIN_DIR/macartedetarot-2.41-arm64-v8a-release.aab"
AAB_FINAL="$BIN_DIR/macartedetarot-2.41-arm64-v8a-release-16KB-signed.aab"

cp "$AAB_SOURCE" "$AAB_FINAL"

jarsigner -sigalg SHA256withRSA -digestalg SHA-256 \
    -keystore "$PROJECT_DIR/googleplay.keystore" \
    -storepass nunotheboss \
    "$AAB_FINAL" upload

echo -e "${GREEN}✅ AAB signé: $AAB_FINAL${NC}"

echo ""
echo -e "${BLUE}📋 Étape 5: Copie sur le bureau Windows...${NC}"

# Copier l'AAB sur le bureau
cp "$AAB_FINAL" "$DESKTOP_DIR/"
echo -e "${GREEN}✅ AAB copié sur le bureau${NC}"

# Copier les symboles natifs si disponibles
if [ -f "$SYMBOLS_ZIP" ]; then
    cp "$SYMBOLS_ZIP" "$DESKTOP_DIR/"
    echo -e "${GREEN}✅ Symboles natifs copiés sur le bureau${NC}"
fi

# Copier le mapping ProGuard si disponible
if [ -f "$BIN_DIR/mapping-2.41.txt" ]; then
    cp "$BIN_DIR/mapping-2.41.txt" "$DESKTOP_DIR/"
    echo -e "${GREEN}✅ Mapping ProGuard copié sur le bureau${NC}"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ BUILD TERMINÉ AVEC SUCCÈS !${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📂 Fichiers disponibles:"
echo ""
echo "   1️⃣  AAB signé:"
echo "      $AAB_FINAL"
echo ""
if [ -f "$SYMBOLS_ZIP" ]; then
    echo "   2️⃣  Symboles de débogage natifs:"
    echo "      $SYMBOLS_ZIP"
    echo ""
fi
if [ -f "$BIN_DIR/mapping-2.41.txt" ]; then
    echo "   3️⃣  Mapping ProGuard/R8:"
    echo "      $BIN_DIR/mapping-2.41.txt"
    echo ""
fi
echo ""
echo "🖥️  Tous les fichiers ont été copiés sur le bureau Windows !"
echo ""
echo "📤 Étapes suivantes dans Google Play Console:"
echo ""
echo "   1. Uploader l'AAB"
if [ -f "$SYMBOLS_ZIP" ]; then
    echo "   2. Dans la même version, uploader native-debug-symbols-2.41.zip"
fi
if [ -f "$BIN_DIR/mapping-2.41.txt" ]; then
    echo "   3. Dans la même version, uploader mapping-2.41.txt"
fi
echo ""
echo "✨ Bon déploiement !"
echo ""
