#!/bin/bash
# Script pour générer une clé de signature Android et la configurer

echo "🔑 GÉNÉRATION DE CLÉ DE SIGNATURE ANDROID POUR GOOGLE PLAY"
echo "============================================================"

# Variables
KEYSTORE_NAME="release.keystore"
ALIAS_NAME="tarot_release"
VALIDITY_DAYS=10000  # ~27 ans

echo ""
echo "📋 Informations requises :"
echo "   - Nom de l'organisation"
echo "   - Ville" 
echo "   - Pays (FR)"
echo "   - Mot de passe du keystore"
echo "   - Mot de passe de la clé"
echo ""

# Vérifier que keytool est disponible
if ! command -v keytool &> /dev/null; then
    echo "❌ keytool non trouvé. Assurez-vous que Java JDK est installé."
    exit 1
fi

# Générer la clé
echo "🔨 Génération de la clé de signature..."
keytool -genkey -v -keystore $KEYSTORE_NAME -keyalg RSA -keysize 2048 -validity $VALIDITY_DAYS -alias $ALIAS_NAME

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Clé générée avec succès : $KEYSTORE_NAME"
    echo ""
    echo "📋 PROCHAINES ÉTAPES :"
    echo ""
    echo "1. ENCODER LA CLÉ EN BASE64 :"
    echo "   base64 -w 0 $KEYSTORE_NAME"
    echo ""
    echo "2. AJOUTER LES SECRETS GITHUB :"
    echo "   - ANDROID_KEYSTORE_BASE64 : (résultat du base64)"
    echo "   - KEYSTORE_PASSWORD : (mot de passe du keystore)"
    echo "   - KEY_ALIAS : $ALIAS_NAME"
    echo "   - KEY_PASSWORD : (mot de passe de la clé)"
    echo ""
    echo "3. CONFIGURER BUILDOZER.SPEC :"
    echo "   [app:android.gradle_dependencies]"
    echo "   android.gradle_dependencies = "
    echo ""
    echo "⚠️  IMPORTANT :"
    echo "   - Sauvegardez ce fichier keystore en lieu sûr"
    echo "   - Si vous le perdez, vous ne pourrez plus mettre à jour l'app"
    echo "   - Ne le partagez JAMAIS publiquement"
    echo ""
    echo "🔐 Clé prête pour la signature automatique !"
else
    echo "❌ Erreur lors de la génération de la clé"
    exit 1
fi
