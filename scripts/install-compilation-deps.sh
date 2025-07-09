#!/bin/bash
# Script pour installer automatiquement les dépendances manquantes pour la compilation hostpython3

set -e

echo "=== Installation des dépendances pour la compilation hostpython3 ==="

# Mettre à jour la liste des packages
echo "📦 Mise à jour de la liste des packages..."
sudo apt-get update -qq

# Packages essentiels pour la compilation C/C++
echo "🔧 Installation des outils de compilation de base..."
sudo apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    autotools-dev \
    automake \
    autoconf \
    libtool \
    pkg-config \
    ccache

# Packages pour Python et ses dépendances natives
echo "🐍 Installation des dépendances Python natives..."
sudo apt-get install -y --no-install-recommends \
    python3-dev \
    python3-setuptools \
    python3-pip \
    python3-wheel

# Bibliothèques système essentielles (headers de développement)
echo "📚 Installation des bibliothèques système..."
sudo apt-get install -y --no-install-recommends \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    libbz2-dev \
    libsqlite3-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libgdbm-dev \
    libgdbm-compat-dev \
    liblzma-dev \
    tk-dev \
    uuid-dev \
    libmpdec-dev

# Bibliothèques additionnelles pour Python complet
echo "📋 Installation des bibliothèques additionnelles..."
sudo apt-get install -y --no-install-recommends \
    libreadline-dev \
    libexpat1-dev \
    libxml2-dev \
    libxslt1-dev \
    libc6-dev \
    linux-libc-dev

# Outils de build avancés
echo "🛠️  Installation des outils de build avancés..."
sudo apt-get install -y --no-install-recommends \
    cmake \
    ninja-build \
    gfortran \
    libgfortran5

# Nettoyer le cache apt
echo "🧹 Nettoyage du cache apt..."
sudo apt-get autoremove -y
sudo apt-get autoclean

echo "✅ Installation des dépendances terminée"

# Vérifier l'installation
echo ""
echo "🔍 Vérification de l'installation..."

# Test de compilation simple
cat > /tmp/hostpython_test.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <zlib.h>
#include <openssl/ssl.h>
#include <ffi.h>
#include <sqlite3.h>
#include <bzlib.h>
#include <lzma.h>

int main() {
    printf("✅ Toutes les bibliothèques essentielles sont disponibles\n");
    printf("zlib: %s\n", zlibVersion());
    printf("SQLite: %s\n", sqlite3_libversion());
    printf("OpenSSL: %s\n", OpenSSL_version(OPENSSL_VERSION));
    return 0;
}
EOF

if gcc -o /tmp/hostpython_test /tmp/hostpython_test.c -lz -lssl -lcrypto -lffi -lsqlite3 -lbz2 -llzma 2>/dev/null; then
    echo "✅ Test de compilation réussi"
    /tmp/hostpython_test
else
    echo "❌ Test de compilation échoué"
    echo "Détails de l'erreur:"
    gcc -o /tmp/hostpython_test /tmp/hostpython_test.c -lz -lssl -lcrypto -lffi -lsqlite3 -lbz2 -llzma 2>&1
fi

# Nettoyer
rm -f /tmp/hostpython_test /tmp/hostpython_test.c

echo ""
echo "=== Récapitulatif ==="
echo "Les dépendances suivantes ont été installées pour assurer la compilation de hostpython3:"
echo "- Compilateurs C/C++ et outils de build"
echo "- Headers de développement Python"
echo "- Bibliothèques système essentielles (zlib, openssl, ffi, sqlite, etc.)"
echo "- Outils de build avancés (cmake, ninja, etc.)"
echo ""
echo "L'environnement est maintenant prêt pour la compilation de hostpython3."
