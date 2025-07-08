#!/bin/bash

# Script de test pour valider la configuration buildozer.spec sans doublons

echo "=== Test de configuration buildozer.spec ==="

# Variables d'environnement simulées
export ANDROID_API_LEVEL=34
export NDK_VERSION="25.2.9519653"
BUILD_TYPE="aab"
KEYSTORE_AVAILABLE="true"

# Sauvegarde
cp buildozer.spec buildozer.spec.backup

echo "🧹 Cleaning existing Android configurations..."
sed -i '/^android\.archs\s*=/d' buildozer.spec
sed -i '/^android\.api\s*=/d' buildozer.spec  
sed -i '/^android\.ndk\s*=/d' buildozer.spec
sed -i '/^android\.sdk\s*=/d' buildozer.spec
sed -i '/^android\.release_artifact\s*=/d' buildozer.spec
sed -i '/^android\.release_keystore\s*=/d' buildozer.spec
sed -i '/^android\.release_keyalias\s*=/d' buildozer.spec
sed -i '/^android\.release_keystore_passwd\s*=/d' buildozer.spec
sed -i '/^android\.release_keyalias_passwd\s*=/d' buildozer.spec

# Supprimer aussi les anciennes lignes de configuration automatique
sed -i '/^# === CONFIGURATION AUTOMATIQUE/d' buildozer.spec
sed -i '/^# === AJOUTS AUTOMATIQUES/d' buildozer.spec

echo "📝 Adding new Android configurations..."

# Insérer avant la section [buildozer]
sed -i '/^\[buildozer\]$/i\\n# === CONFIGURATION AUTOMATIQUE PAR LE WORKFLOW CI/CD ===' buildozer.spec
sed -i '/^# === CONFIGURATION AUTOMATIQUE/a android.archs = arm64-v8a, armeabi-v7a' buildozer.spec
sed -i '/^android.archs = /a android.api = '$ANDROID_API_LEVEL buildozer.spec
sed -i '/^android.api = /a android.ndk = '$NDK_VERSION buildozer.spec
sed -i '/^android.ndk = /a android.sdk = '$ANDROID_API_LEVEL buildozer.spec

# Configuration spécifique au type de build
if [ "$BUILD_TYPE" == "aab" ]; then
  echo "📦 Configuring for AAB build"
  sed -i '/^android.sdk = /a android.release_artifact = aab' buildozer.spec
  
  # Configuration keystore si disponible
  if [ "$KEYSTORE_AVAILABLE" == "true" ]; then
    echo "🔑 Configuring release signing"
    sed -i '/^android.release_artifact = aab/a android.release_keystore = %(source.dir)s/signing.keystore' buildozer.spec
    sed -i '/^android.release_keystore = /a android.release_keyalias = test_alias' buildozer.spec
    sed -i '/^android.release_keyalias = /a android.release_keystore_passwd = test_password' buildozer.spec
    sed -i '/^android.release_keystore_passwd = /a android.release_keyalias_passwd = test_password' buildozer.spec
  fi
else
  echo "📱 Configuring for APK build"
  sed -i '/^android.sdk = /a android.release_artifact = apk' buildozer.spec
fi

echo "=== buildozer.spec configured ==="
echo "📋 Final configuration preview:"
grep -A 15 "CONFIGURATION AUTOMATIQUE" buildozer.spec || echo "Configuration added successfully"

echo ""
echo "🔍 Vérification des doublons..."
# Vérifier s'il y a des doublons
for key in archs api ndk sdk release_artifact; do
  count=$(grep -c "^android\.$key" buildozer.spec)
  if [ $count -gt 1 ]; then
    echo "❌ ERREUR: $count occurrences de android.$key trouvées!"
    grep -n "^android\.$key" buildozer.spec
  else
    echo "✅ android.$key: $count occurrence (OK)"
  fi
done

echo ""
echo "📄 Configuration finale:"
cat buildozer.spec

# Tester la syntaxe avec python
echo ""
echo "🔧 Test de la syntaxe du fichier de configuration..."
python3 -c "
import configparser
try:
    config = configparser.ConfigParser()
    config.read('buildozer.spec')
    print('✅ Syntaxe valide!')
    print(f'Sections trouvées: {list(config.sections())}')
except Exception as e:
    print(f'❌ Erreur de syntaxe: {e}')
"

# Restaurer la sauvegarde
echo ""
echo "🔄 Restauration de la sauvegarde..."
mv buildozer.spec.backup buildozer.spec
echo "Terminé!"
