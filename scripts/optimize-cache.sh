#!/bin/bash

# Script d'optimisation et nettoyage du cache buildozer
# Utilisé pour améliorer les performances et éviter les erreurs

set -e

echo "🧹 === NETTOYAGE ET OPTIMISATION DU CACHE BUILDOZER ==="
echo "Timestamp: $(date)"
echo ""

# Configuration
BUILDOZER_DIR="$HOME/.buildozer"
CACHE_DIR="$HOME/.cache/python-for-android"
PACKAGES_DIR="$BUILDOZER_DIR/android/packages"

# Fonction pour calculer la taille d'un répertoire
calculate_size() {
    local dir="$1"
    if [ -d "$dir" ]; then
        du -sh "$dir" 2>/dev/null | cut -f1
    else
        echo "0B"
    fi
}

# Fonction pour compter les fichiers
count_files() {
    local dir="$1"
    if [ -d "$dir" ]; then
        find "$dir" -type f 2>/dev/null | wc -l
    else
        echo "0"
    fi
}

# Afficher l'état initial
echo "📊 État initial du cache:"
echo "========================"
echo "  ~/.buildozer: $(calculate_size "$BUILDOZER_DIR")"
echo "  ~/.cache/python-for-android: $(calculate_size "$CACHE_DIR")"
echo "  ~/.buildozer/android/packages: $(calculate_size "$PACKAGES_DIR")"
echo ""

# Nettoyer les téléchargements partiels
echo "🔄 Nettoyage des téléchargements partiels..."
if [ -d "$BUILDOZER_DIR" ]; then
    find "$BUILDOZER_DIR" -name "*.tmp" -delete 2>/dev/null || true
    find "$BUILDOZER_DIR" -name "*.part" -delete 2>/dev/null || true
    find "$BUILDOZER_DIR" -name "*.download" -delete 2>/dev/null || true
    echo "  ✅ Téléchargements partiels nettoyés"
else
    echo "  ℹ️  Répertoire buildozer n'existe pas encore"
fi

# Nettoyer les fichiers temporaires
echo "🔄 Nettoyage des fichiers temporaires..."
if [ -d "$CACHE_DIR" ]; then
    find "$CACHE_DIR" -name "*.tmp" -delete 2>/dev/null || true
    find "$CACHE_DIR" -name "*.log" -mtime +7 -delete 2>/dev/null || true
    echo "  ✅ Fichiers temporaires nettoyés"
else
    echo "  ℹ️  Cache python-for-android n'existe pas encore"
fi

# Optimiser le cache des packages
echo "🔄 Optimisation du cache des packages..."
if [ -d "$PACKAGES_DIR" ]; then
    # Supprimer les fichiers corrompus (taille 0)
    corrupted_count=0
    for file in "$PACKAGES_DIR"/*; do
        if [ -f "$file" ] && [ ! -s "$file" ]; then
            rm -f "$file"
            corrupted_count=$((corrupted_count + 1))
        fi
    done
    
    if [ $corrupted_count -gt 0 ]; then
        echo "  ✅ $corrupted_count fichiers corrompus supprimés"
    else
        echo "  ✅ Aucun fichier corrompu trouvé"
    fi
    
    # Vérifier l'intégrité des archives
    echo "🔍 Vérification de l'intégrité des archives..."
    for file in "$PACKAGES_DIR"/*.tar.gz; do
        if [ -f "$file" ]; then
            if ! tar -tzf "$file" >/dev/null 2>&1; then
                echo "  ⚠️  Archive corrompue détectée: $(basename "$file")"
                rm -f "$file"
                echo "  ✅ Archive corrompue supprimée"
            fi
        fi
    done
    
    for file in "$PACKAGES_DIR"/*.tar.xz; do
        if [ -f "$file" ]; then
            if ! tar -tJf "$file" >/dev/null 2>&1; then
                echo "  ⚠️  Archive corrompue détectée: $(basename "$file")"
                rm -f "$file"
                echo "  ✅ Archive corrompue supprimée"
            fi
        fi
    done
    
    echo "  ✅ Vérification d'intégrité terminée"
else
    echo "  ℹ️  Répertoire packages n'existe pas encore"
    mkdir -p "$PACKAGES_DIR"
    echo "  ✅ Répertoire packages créé"
fi

# Nettoyer les anciens builds
echo "🔄 Nettoyage des anciens builds..."
if [ -d "$BUILDOZER_DIR/android/platform" ]; then
    # Supprimer les anciens répertoires de build
    find "$BUILDOZER_DIR/android/platform" -name "build-*" -type d -mtime +1 -exec rm -rf {} + 2>/dev/null || true
    
    # Supprimer les anciens dists
    find "$BUILDOZER_DIR/android/platform" -name "dists" -type d -exec find {} -name "*" -type d -mtime +1 -exec rm -rf {} + \; 2>/dev/null || true
    
    echo "  ✅ Anciens builds nettoyés"
else
    echo "  ℹ️  Répertoire platform n'existe pas encore"
fi

# Optimiser les permissions
echo "🔄 Optimisation des permissions..."
if [ -d "$BUILDOZER_DIR" ]; then
    chmod -R u+rw "$BUILDOZER_DIR" 2>/dev/null || true
    echo "  ✅ Permissions optimisées"
fi

# Créer la structure de répertoires nécessaire
echo "🔄 Création de la structure de répertoires..."
mkdir -p "$BUILDOZER_DIR/android/platform"
mkdir -p "$PACKAGES_DIR"
mkdir -p "$CACHE_DIR"
echo "  ✅ Structure créée"

# Afficher l'état final
echo ""
echo "📊 État final du cache:"
echo "======================"
echo "  ~/.buildozer: $(calculate_size "$BUILDOZER_DIR")"
echo "  ~/.cache/python-for-android: $(calculate_size "$CACHE_DIR")"
echo "  ~/.buildozer/android/packages: $(calculate_size "$PACKAGES_DIR")"
echo ""

# Afficher les statistiques détaillées
echo "📈 Statistiques détaillées:"
echo "==========================="
echo "  Fichiers dans ~/.buildozer: $(count_files "$BUILDOZER_DIR")"
echo "  Fichiers dans ~/.cache/python-for-android: $(count_files "$CACHE_DIR")"
echo "  Packages mis en cache: $(count_files "$PACKAGES_DIR")"
echo ""

# Lister les packages en cache
if [ -d "$PACKAGES_DIR" ] && [ "$(ls -A "$PACKAGES_DIR" 2>/dev/null)" ]; then
    echo "📦 Packages en cache:"
    echo "===================="
    for file in "$PACKAGES_DIR"/*; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo "0")
            size_mb=$((size / 1024 / 1024))
            echo "  $filename (${size_mb}MB)"
        fi
    done
else
    echo "📦 Aucun package en cache"
fi

echo ""
echo "🏁 === NETTOYAGE TERMINÉ ==="
echo "Timestamp: $(date)"
