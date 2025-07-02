#!/bin/bash

# Script pour créer une clé de signature Android de production
# Usage: ./create_signing_key.sh

set -e

echo "🔐 Création de la clé de signature Android pour Ma Carte de Tarot"
echo ""

# Vérifications préliminaires
if ! command -v keytool &> /dev/null; then
    echo "❌ keytool n'est pas installé. Installez Java JDK."
    exit 1
fi

# Paramètres de la clé
KEYSTORE_FILE="release.keystore"
KEY_ALIAS="release"
VALIDITY_DAYS=10000  # ~27 ans

echo "📋 Informations de la clé :"
echo "   Fichier keystore : $KEYSTORE_FILE"
echo "   Alias de la clé  : $KEY_ALIAS"
echo "   Validité         : $VALIDITY_DAYS jours"
echo ""

# Vérifier si la clé existe déjà
if [ -f "$KEYSTORE_FILE" ]; then
    echo "⚠️  Le fichier $KEYSTORE_FILE existe déjà !"
    read -p "Voulez-vous le remplacer ? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Annulé par l'utilisateur"
        exit 1
    fi
    rm -f "$KEYSTORE_FILE"
fi

echo "🔨 Génération de la clé de signature..."
echo "   Vous allez devoir saisir des informations personnelles et un mot de passe."
echo "   IMPORTANT: Notez bien le mot de passe, vous en aurez besoin pour les secrets GitHub !"
echo ""

# Génération de la clé
keytool -genkey -v \
    -keystore "$KEYSTORE_FILE" \
    -alias "$KEY_ALIAS" \
    -keyalg RSA \
    -keysize 2048 \
    -validity $VALIDITY_DAYS

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Clé de signature créée avec succès !"
    echo ""
    echo "📁 Fichier généré : $KEYSTORE_FILE"
    echo "🔑 Alias de la clé : $KEY_ALIAS"
    echo ""
    
    # Afficher les infos de la clé
    echo "ℹ️  Informations de la clé :"
    keytool -list -v -keystore "$KEYSTORE_FILE" -alias "$KEY_ALIAS"
    
    echo ""
    echo "🔒 Configuration des secrets GitHub :"
    echo "   1. ANDROID_KEYSTORE        : $(base64 -w 0 "$KEYSTORE_FILE")"
    echo "   2. ANDROID_KEYSTORE_PASSWORD: [mot de passe du keystore saisi]"
    echo "   3. ANDROID_KEY_ALIAS       : $KEY_ALIAS"
    echo "   4. ANDROID_KEY_PASSWORD    : [mot de passe de la clé saisi]"
    echo ""
    echo "📖 Voir SECRETS_SETUP.md pour la configuration complète"
    echo ""
    echo "⚠️  IMPORTANT :"
    echo "   - Sauvegardez cette clé en lieu sûr"
    echo "   - Ne la commitez JAMAIS dans Git"
    echo "   - Utilisez la même clé pour toutes les versions de l'app"
    echo ""
else
    echo "❌ Erreur lors de la création de la clé"
    exit 1
fi
