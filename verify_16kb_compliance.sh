#!/bin/bash
# Script de vérification automatique de conformité 16KB pour Google Play
# Usage: ./verify_16kb_compliance.sh [path/to/app.aab]

set -e

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🔍 VERIFICATION CONFORMITÉ 16KB PAGE SIZE - GOOGLE PLAY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Déterminer le AAB à vérifier
if [ -z "$1" ]; then
    # Chercher le dernier AAB buildé
    AAB_PATH=$(find bin/ -name "*.aab" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
    if [ -z "$AAB_PATH" ]; then
        echo -e "${RED}❌ Aucun AAB trouvé dans bin/${NC}"
        echo "Usage: $0 [path/to/app.aab]"
        exit 1
    fi
    echo -e "${BLUE}📦 AAB détecté: ${AAB_PATH}${NC}"
else
    AAB_PATH="$1"
    if [ ! -f "$AAB_PATH" ]; then
        echo -e "${RED}❌ Fichier non trouvé: $AAB_PATH${NC}"
        exit 1
    fi
fi

# Extraction temporaire
TEMP_DIR="/tmp/aab_16kb_check_$$"
echo -e "${BLUE}📂 Extraction AAB vers ${TEMP_DIR}...${NC}"
rm -rf "$TEMP_DIR" && mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR" && unzip -q "$OLDPWD/$AAB_PATH" 2>&1 | head -5

# Rechercher toutes les bibliothèques .so
SO_FILES=$(find . -name "*.so" -type f | sort)
TOTAL_SO=$(echo "$SO_FILES" | wc -l)

echo -e "${BLUE}📊 Bibliothèques natives trouvées: ${TOTAL_SO}${NC}"
echo ""

if [ $TOTAL_SO -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Aucune bibliothèque native détectée (app Java/Kotlin pure)${NC}"
    echo -e "${GREEN}✅ CONFORMITÉ 16KB: OK (pas de code natif)${NC}"
    rm -rf "$TEMP_DIR"
    exit 0
fi

# Analyser chaque .so
echo -e "${BLUE}┌─────────────────────────────────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│ Bibliothèque                    │ Alignements │ Statut              │${NC}"
echo -e "${BLUE}├─────────────────────────────────────────────────────────────────────────┤${NC}"

FAILED_LIBS=""
MIXED_LIBS=""
OK_LIBS=""
NO_LOAD_LIBS=""

for so_path in $SO_FILES; do
    lib_name=$(basename "$so_path")
    
    # Extraire les alignements LOAD
    aligns=$(readelf -lW "$so_path" 2>/dev/null | grep "LOAD" | awk '{print $NF}' | sort -u | tr '\n' ' ' || echo "")
    
    if [ -z "$aligns" ]; then
        # Pas de segment LOAD (bundle/archive)
        status="${YELLOW}⚠️  NO LOAD${NC}"
        NO_LOAD_LIBS="$NO_LOAD_LIBS\n  - $lib_name"
        printf "${BLUE}│${NC} %-31s ${BLUE}│${NC} %-11s ${BLUE}│${NC} %-19s ${BLUE}│${NC}\n" \
            "$lib_name" "N/A" "$(echo -e "$status")"
    elif echo "$aligns" | grep -q "0x4000"; then
        # Contient 0x4000 (16KB)
        if echo "$aligns" | grep -q "0x1000"; then
            # Mixte 4KB + 16KB
            status="${YELLOW}⚠️  MIXTE 4K+16K${NC}"
            MIXED_LIBS="$MIXED_LIBS\n  - $lib_name ($aligns)"
        else
            # Pure 16KB
            status="${GREEN}✅ CONFORME 16KB${NC}"
            OK_LIBS="$OK_LIBS\n  - $lib_name"
        fi
        printf "${BLUE}│${NC} %-31s ${BLUE}│${NC} %-11s ${BLUE}│${NC} %-19s ${BLUE}│${NC}\n" \
            "$lib_name" "$aligns" "$(echo -e "$status")"
    else
        # Contient uniquement 0x1000 (4KB) ou autre
        status="${RED}❌ NON CONFORME${NC}"
        FAILED_LIBS="$FAILED_LIBS\n  - $lib_name ($aligns)"
        printf "${BLUE}│${NC} %-31s ${BLUE}│${NC} %-11s ${BLUE}│${NC} %-19s ${BLUE}│${NC}\n" \
            "$lib_name" "$aligns" "$(echo -e "$status")"
    fi
done

echo -e "${BLUE}└─────────────────────────────────────────────────────────────────────────┘${NC}"
echo ""

# Résumé
OK_COUNT=$(echo -e "$OK_LIBS" | grep -c "^ *-" || echo 0)
FAILED_COUNT=$(echo -e "$FAILED_LIBS" | grep -c "^ *-" || echo 0)
MIXED_COUNT=$(echo -e "$MIXED_LIBS" | grep -c "^ *-" || echo 0)
NO_LOAD_COUNT=$(echo -e "$NO_LOAD_LIBS" | grep -c "^ *-" || echo 0)

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  📊 RÉSUMÉ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "  ${GREEN}✅ Conformes 16KB:${NC}      $OK_COUNT / $TOTAL_SO"
echo -e "  ${RED}❌ Non conformes (4KB):${NC} $FAILED_COUNT / $TOTAL_SO"
echo -e "  ${YELLOW}⚠️  Mixtes (4K+16K):${NC}    $MIXED_COUNT / $TOTAL_SO"
echo -e "  ${YELLOW}⚠️  Sans LOAD:${NC}          $NO_LOAD_COUNT / $TOTAL_SO"
echo ""

# Détails des bibliothèques non conformes
if [ $FAILED_COUNT -gt 0 ]; then
    echo -e "${RED}❌ BIBLIOTHÈQUES NON CONFORMES (BLOQUANTES):${NC}"
    echo -e "$FAILED_LIBS"
    echo ""
    echo -e "${RED}Action requise:${NC}"
    echo "  1. Vérifier les recettes p4a pour ces bibliothèques"
    echo "  2. Forcer rebuild avec: rm -rf .buildozer/android/platform/build-*/build/other_builds/{nom_recette}*"
    echo "  3. Rebuild complet: ./rebuild_16kb.sh"
    echo ""
fi

if [ $MIXED_COUNT -gt 0 ]; then
    echo -e "${YELLOW}⚠️  BIBLIOTHÈQUES MIXTES (À SURVEILLER):${NC}"
    echo -e "$MIXED_LIBS"
    echo ""
    echo -e "${YELLOW}Note:${NC} Alignements mixtes peuvent fonctionner mais ne sont pas garantis."
    echo "      Recommandation: forcer pure 16KB si possible."
    echo ""
fi

# Nettoyage
rm -rf "$TEMP_DIR"

# Verdict final
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
if [ $FAILED_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ ✅ ✅ CONFORMITÉ GOOGLE PLAY: OK ✅ ✅ ✅${NC}"
    echo -e "${GREEN}L'application peut être soumise à Google Play Console${NC}"
    if [ $MIXED_COUNT -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Note: Bibliothèques mixtes détectées, surveillance recommandée${NC}"
    fi
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}❌ ❌ ❌ CONFORMITÉ GOOGLE PLAY: ÉCHEC ❌ ❌ ❌${NC}"
    echo -e "${RED}L'application sera REJETÉE par Google Play Console${NC}"
    echo -e "${RED}$FAILED_COUNT bibliothèque(s) doivent être recompilées avec alignement 16KB${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
    exit 1
fi
