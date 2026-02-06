#!/bin/bash
# Script de correction et rebuild complet avec alignement 16KB
# Supprime les recettes non conformes et rebuild proprement

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🔧 CORRECTION & REBUILD COMPLET 16KB${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Vérifier que les recettes patchées existent
echo -e "${BLUE}📋 Vérification des recettes patchées...${NC}"
RECIPES_OK=true

if [ ! -f "p4a_recipes/python3/__init__.py" ]; then
    echo -e "${RED}❌ Recette python3 non trouvée${NC}"
    RECIPES_OK=false
fi

if [ ! -f "p4a_recipes/openssl/__init__.py" ]; then
    echo -e "${RED}❌ Recette openssl non trouvée${NC}"
    RECIPES_OK=false
fi

if [ ! -f "p4a_recipes/sqlite3/__init__.py" ]; then
    echo -e "${RED}❌ Recette sqlite3 non trouvée${NC}"
    RECIPES_OK=false
fi

if [ "$RECIPES_OK" = false ]; then
    echo ""
    echo -e "${RED}❌ Erreur: Recettes patchées manquantes${NC}"
    echo "Exécutez d'abord les commandes de création des recettes."
    exit 1
fi

echo -e "${GREEN}✅ Toutes les recettes patchées sont présentes${NC}"
echo ""

# Clean des recettes problématiques
echo -e "${BLUE}🧹 Nettoyage des recettes non conformes...${NC}"

BUILDOZER_ANDROID=".buildozer/android/platform/build-arm64-v8a/build/other_builds"

if [ -d "$BUILDOZER_ANDROID" ]; then
    echo -e "${YELLOW}Suppression de: python3, openssl, sqlite3, libffi${NC}"
    rm -rf "$BUILDOZER_ANDROID"/python3* 2>/dev/null || true
    rm -rf "$BUILDOZER_ANDROID"/openssl* 2>/dev/null || true
    rm -rf "$BUILDOZER_ANDROID"/sqlite3* 2>/dev/null || true
    rm -rf "$BUILDOZER_ANDROID"/libffi* 2>/dev/null || true
    echo -e "${GREEN}✅ Recettes supprimées${NC}"
else
    echo -e "${YELLOW}⚠️  Répertoire buildozer non trouvé (premier build ?)${NC}"
fi

echo ""
echo -e "${BLUE}🔨 Lancement du rebuild complet avec flags 16KB...${NC}"
echo ""

# Export des flags 16KB dans l'environnement
export LDFLAGS="-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384 ${LDFLAGS}"
export CFLAGS="-Wl,-z,max-page-size=16384 ${CFLAGS}"
export CXXFLAGS="-Wl,-z,max-page-size=16384 ${CXXFLAGS}"

echo -e "${GREEN}✅ Variables d'environnement:${NC}"
echo "   LDFLAGS=$LDFLAGS"
echo "   CFLAGS=$CFLAGS"
echo "   CXXFLAGS=$CXXFLAGS"
echo ""

# Lancer buildozer en mode release
echo -e "${BLUE}🚀 Buildozer android release...${NC}"
echo -e "${YELLOW}⏱️  Cela peut prendre 15-30 minutes (recompilation Python + OpenSSL)${NC}"
echo ""

buildozer android release

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ BUILD TERMINÉ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Trouver le AAB généré
AAB_FILE=$(find bin/ -name "*.aab" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)

if [ -z "$AAB_FILE" ]; then
    echo -e "${RED}❌ Aucun AAB trouvé dans bin/${NC}"
    exit 1
fi

echo -e "${BLUE}📦 AAB généré: ${AAB_FILE}${NC}"
echo ""

# Lancer la vérification automatique
echo -e "${BLUE}🔍 Lancement de la vérification 16KB...${NC}"
echo ""

if [ -f "./verify_16kb_compliance.sh" ]; then
    bash ./verify_16kb_compliance.sh "$AAB_FILE"
else
    echo -e "${YELLOW}⚠️  Script de vérification non trouvé${NC}"
    echo "Vérifiez manuellement avec:"
    echo "  ./verify_16kb_compliance.sh $AAB_FILE"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 PROCESSUS TERMINÉ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
