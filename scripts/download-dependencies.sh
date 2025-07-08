#!/bin/bash

# Script de téléchargement alternatif pour les dépendances buildozer
# Utilise plusieurs méthodes et sources pour télécharger les packages

set -e

echo "📦 === TELECHARGEMENT ALTERNATIF DES DEPENDANCES ==="
echo "Timestamp: $(date)"
echo ""

# Configuration
CACHE_DIR="$HOME/.buildozer/android/packages"
TEMP_DIR="/tmp/buildozer_downloads"
mkdir -p "$CACHE_DIR" "$TEMP_DIR"

# Fonction de téléchargement robuste
download_package() {
    local name="$1"
    local primary_url="$2"
    local fallback_url="$3"
    local filename="$(basename "$primary_url")"
    local target="$CACHE_DIR/$filename"
    
    echo "📥 Téléchargement de $name..."
    
    # Vérifier si déjà en cache
    if [ -f "$target" ] && [ -s "$target" ]; then
        echo "  ✅ $name déjà en cache"
        return 0
    fi
    
    # Tentative 1: curl avec URL primaire
    echo "  🔄 Tentative 1: curl avec URL primaire"
    if curl -L --connect-timeout 30 --max-time 300 --retry 3 --retry-delay 5 -o "$target" "$primary_url" 2>/dev/null && [ -s "$target" ]; then
        echo "  ✅ $name téléchargé avec succès (curl primaire)"
        return 0
    fi
    
    rm -f "$target"
    
    # Tentative 2: wget avec URL primaire
    echo "  🔄 Tentative 2: wget avec URL primaire"
    if wget -q --timeout=30 --tries=3 --retry-connrefused --waitretry=5 -O "$target" "$primary_url" 2>/dev/null && [ -s "$target" ]; then
        echo "  ✅ $name téléchargé avec succès (wget primaire)"
        return 0
    fi
    
    rm -f "$target"
    
    # Tentative 3: curl avec URL de fallback
    if [ -n "$fallback_url" ]; then
        echo "  🔄 Tentative 3: curl avec URL de fallback"
        if curl -L --connect-timeout 30 --max-time 300 --retry 3 --retry-delay 5 -o "$target" "$fallback_url" 2>/dev/null && [ -s "$target" ]; then
            echo "  ✅ $name téléchargé avec succès (curl fallback)"
            return 0
        fi
        
        rm -f "$target"
        
        # Tentative 4: wget avec URL de fallback
        echo "  🔄 Tentative 4: wget avec URL de fallback"
        if wget -q --timeout=30 --tries=3 --retry-connrefused --waitretry=5 -O "$target" "$fallback_url" 2>/dev/null && [ -s "$target" ]; then
            echo "  ✅ $name téléchargé avec succès (wget fallback)"
            return 0
        fi
        
        rm -f "$target"
    fi
    
    # Tentative 5: python avec urllib
    echo "  🔄 Tentative 5: python avec urllib"
    if python3 -c "
import urllib.request
import ssl
import socket

# Ignorer les certificats SSL pour contourner les problèmes de connectivité
ssl._create_default_https_context = ssl._create_unverified_context

try:
    socket.setdefaulttimeout(30)
    urllib.request.urlretrieve('$primary_url', '$target')
    print('  ✅ $name téléchargé avec succès (python urllib)')
    exit(0)
except Exception as e:
    print(f'  ❌ Erreur python urllib: {e}')
    exit(1)
" 2>/dev/null && [ -s "$target" ]; then
        return 0
    fi
    
    rm -f "$target"
    
    echo "  ❌ Échec du téléchargement de $name"
    return 1
}

# Dépendances à télécharger
echo "📋 Liste des dépendances à télécharger:"
echo "  - freetype"
echo "  - libffi"
echo "  - openssl"
echo "  - libpng"
echo ""

# Télécharger freetype
download_package "freetype" \
    "https://download.savannah.gnu.org/releases/freetype/freetype-2.10.1.tar.gz" \
    "https://github.com/freetype/freetype/archive/VER-2-10-1.tar.gz"

# Télécharger libffi
download_package "libffi" \
    "https://github.com/libffi/libffi/archive/v3.4.2.tar.gz" \
    "https://sourceforge.net/projects/libffi/files/libffi-3.4.2.tar.gz"

# Télécharger openssl
download_package "openssl" \
    "https://www.openssl.org/source/openssl-1.1.1w.tar.gz" \
    "https://github.com/openssl/openssl/archive/OpenSSL_1_1_1w.tar.gz"

# Télécharger libpng
download_package "libpng" \
    "https://sourceforge.net/projects/libpng/files/libpng16/1.6.37/libpng-1.6.37.tar.xz" \
    "https://github.com/glennrp/libpng/archive/v1.6.37.tar.gz"

echo ""
echo "📊 Résumé du téléchargement:"
echo "=========================================="

total_size=0
success_count=0
total_count=4

for file in "$CACHE_DIR"/*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo "0")
        size_mb=$((size / 1024 / 1024))
        
        if [ "$size" -gt 0 ]; then
            echo "  ✅ $filename (${size_mb}MB)"
            total_size=$((total_size + size))
            success_count=$((success_count + 1))
        else
            echo "  ❌ $filename (0MB - échec)"
        fi
    fi
done

total_size_mb=$((total_size / 1024 / 1024))
echo ""
echo "Taille totale du cache: ${total_size_mb}MB"
echo "Succès: $success_count/$total_count packages"

if [ "$success_count" -eq "$total_count" ]; then
    echo "🎉 Tous les packages ont été téléchargés avec succès!"
else
    echo "⚠️  Certains packages n'ont pas pu être téléchargés"
fi

echo ""
echo "🏁 === FIN DU TELECHARGEMENT ==="
echo "Timestamp: $(date)"
