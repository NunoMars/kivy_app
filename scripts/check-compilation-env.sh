#!/bin/bash
# Script pour vérifier et configurer l'environnement de compilation C pour hostpython3

set -e

echo "=== Diagnostic de l'environnement de compilation C ==="

# Vérifier les compilateurs de base
echo "🔍 Vérification des compilateurs:"
for compiler in gcc g++ cpp ar ranlib strip; do
    if command -v $compiler >/dev/null 2>&1; then
        echo "✅ $compiler: $(which $compiler)"
        $compiler --version | head -1
    else
        echo "❌ $compiler: NON TROUVÉ"
    fi
done

# Vérifier les bibliothèques système essentielles
echo ""
echo "🔍 Vérification des bibliothèques système:"
essential_libs=(
    "libffi"
    "libssl"
    "zlib"
    "libbz2"
    "libsqlite3"
    "libncurses"
    "libgdbm"
    "liblzma"
    "libreadline"
    "libexpat"
    "libxml2"
    "libxslt"
)

for lib in "${essential_libs[@]}"; do
    if ldconfig -p | grep -q "$lib"; then
        echo "✅ $lib: $(ldconfig -p | grep "$lib" | head -1 | awk '{print $4}')"
    else
        echo "❌ $lib: NON TROUVÉ"
    fi
done

# Vérifier les headers de développement
echo ""
echo "🔍 Vérification des headers de développement:"
dev_headers=(
    "/usr/include/ffi.h"
    "/usr/include/openssl/ssl.h"
    "/usr/include/zlib.h"
    "/usr/include/bzlib.h"
    "/usr/include/sqlite3.h"
    "/usr/include/ncurses.h"
    "/usr/include/gdbm.h"
    "/usr/include/lzma.h"
    "/usr/include/readline/readline.h"
    "/usr/include/expat.h"
    "/usr/include/libxml2/libxml/parser.h"
    "/usr/include/libxslt/xslt.h"
    "/usr/include/Python.h"
)

for header in "${dev_headers[@]}"; do
    if [ -f "$header" ]; then
        echo "✅ $header"
    else
        echo "❌ $header: NON TROUVÉ"
    fi
done

# Test de compilation simple
echo ""
echo "🧪 Test de compilation C:"
cat > /tmp/test_compile.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <zlib.h>
#include <openssl/ssl.h>
#include <ffi.h>

int main() {
    printf("Test compilation successful!\n");
    printf("zlib version: %s\n", zlibVersion());
    printf("OpenSSL version: %s\n", OpenSSL_version(OPENSSL_VERSION));
    return 0;
}
EOF

if gcc -o /tmp/test_compile /tmp/test_compile.c -lz -lssl -lcrypto -lffi 2>/dev/null; then
    echo "✅ Compilation de test réussie"
    if /tmp/test_compile 2>/dev/null; then
        echo "✅ Exécution de test réussie"
    else
        echo "❌ Échec de l'exécution de test"
    fi
else
    echo "❌ Échec de la compilation de test"
    echo "Détails de l'erreur:"
    gcc -o /tmp/test_compile /tmp/test_compile.c -lz -lssl -lcrypto -lffi 2>&1 | head -10
fi

# Nettoyer
rm -f /tmp/test_compile /tmp/test_compile.c

# Vérifier les variables d'environnement critiques
echo ""
echo "🔍 Variables d'environnement:"
env_vars=(
    "CC"
    "CXX"
    "CPP"
    "AR"
    "RANLIB"
    "STRIP"
    "CFLAGS"
    "CXXFLAGS"
    "LDFLAGS"
    "CPPFLAGS"
    "PKG_CONFIG_PATH"
    "LD_LIBRARY_PATH"
)

for var in "${env_vars[@]}"; do
    if [ -n "${!var}" ]; then
        echo "✅ $var=${!var}"
    else
        echo "⚠️  $var: non défini"
    fi
done

# Vérifier pkg-config
echo ""
echo "🔍 Configuration pkg-config:"
if command -v pkg-config >/dev/null 2>&1; then
    echo "✅ pkg-config: $(which pkg-config)"
    echo "Version: $(pkg-config --version)"
    
    # Tester quelques packages essentiels
    for pkg in zlib openssl libffi; do
        if pkg-config --exists "$pkg" 2>/dev/null; then
            echo "✅ $pkg: $(pkg-config --modversion "$pkg")"
        else
            echo "❌ $pkg: package non trouvé"
        fi
    done
else
    echo "❌ pkg-config: NON TROUVÉ"
fi

# Rapport final
echo ""
echo "=== Rapport final ==="
echo "Si des éléments sont manquants, installez-les avec:"
echo "sudo apt-get install -y build-essential python3-dev"
echo "sudo apt-get install -y libffi-dev libssl-dev zlib1g-dev"
echo "sudo apt-get install -y libbz2-dev libsqlite3-dev libncurses5-dev"
echo "sudo apt-get install -y libgdbm-dev liblzma-dev libreadline-dev"
echo "sudo apt-get install -y libexpat1-dev libxml2-dev libxslt1-dev"
echo "sudo apt-get install -y autotools-dev automake autoconf libtool pkg-config"
