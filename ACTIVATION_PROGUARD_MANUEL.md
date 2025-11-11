# 🔧 Activation manuelle de ProGuard/R8 et symboles natifs

## ⚠️ Important

Buildozer ne supporte pas nativement l'activation de ProGuard/R8 pour les apps Kivy.  
Il faut modifier **manuellement** le fichier `build.gradle` généré après le premier build.

---

## 📋 Procédure complète

### Étape 1 : Build initial
```bash
buildozer android release
```

### Étape 2 : Localiser build.gradle
```bash
cd .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/macartedetarot/
ls -la build.gradle
```

### Étape 3 : Modifier build.gradle

Ouvrir le fichier et chercher le bloc `buildTypes`:

```gradle
buildTypes {
    release {
        // AVANT (configuration par défaut)
        signingConfig signingConfigs.release
    }
}
```

**Remplacer par** :

```gradle
buildTypes {
    release {
        signingConfig signingConfigs.release
        
        // ✅ Activer ProGuard/R8
        minifyEnabled true
        shrinkResources true
        proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        
        // ✅ Activer symboles de débogage natifs (niveau FULL)
        ndk {
            debugSymbolLevel 'FULL'
        }
    }
}
```

### Étape 4 : Copier les règles ProGuard

```bash
# Depuis la racine du projet kivy_app/
cp proguard-rules.pro .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/macartedetarot/
```

### Étape 5 : Rebuild avec Gradle directement

```bash
cd .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/macartedetarot/

# Build AAB avec ProGuard activé
./gradlew bundleRelease

# Les fichiers générés seront dans:
# - build/outputs/bundle/release/*.aab
# - build/outputs/mapping/release/mapping.txt (ProGuard)
# - build/outputs/native-debug-symbols/release/native-debug-symbols.zip
```

### Étape 6 : Signer l'AAB

```bash
# Retourner à la racine
cd /home/loupy/kivy_app

# Copier l'AAB généré
cp .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/macartedetarot/build/outputs/bundle/release/macartedetarot-release.aab bin/macartedetarot-2.2-arm64-v8a_armeabi-v7a-release.aab

# Signer
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore googleplay.keystore bin/macartedetarot-2.2-arm64-v8a_armeabi-v7a-release.aab upload

# Renommer
mv bin/macartedetarot-2.2-arm64-v8a_armeabi-v7a-release.aab bin/macartedetarot-2.2-arm64-v8a_armeabi-v7a-release-signed.aab
```

### Étape 7 : Extraire les symboles de débogage

```bash
./extract_debug_symbols.sh 2.2
```

---

## 🎯 Résultat attendu

Après ces étapes, vous aurez :

✅ **AAB optimisé** avec ProGuard/R8 (taille réduite ~20-30%)  
✅ **mapping.txt** pour désobscurcir les stack traces  
✅ **native-debug-symbols.zip** pour déboguer les crashs natifs  

---

## 📊 Vérification

### Vérifier que ProGuard est actif

```bash
# Décompresser l'AAB et vérifier la taille des classes
unzip -l bin/*-signed.aab | grep "classes.dex"

# Avec ProGuard : classes.dex sera ~30% plus petit
# Sans ProGuard : classes.dex sera plus gros
```

### Vérifier les fichiers de débogage

```bash
ls -lh debug_symbols/v2.2/
# Devrait afficher:
# - mapping.txt (~100-500 KB)
# - native-debug-symbols.zip (~10-50 MB)
# - macartedetarot-2.2-...-signed.aab
```

---

## ⚡ Script automatisé

Pour éviter de refaire ces étapes à chaque build, utiliser ce script :

```bash
#!/bin/bash
# build_with_proguard.sh

set -e

VERSION="2.2"
DIST_DIR=".buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/macartedetarot"

echo "🔨 Build initial avec buildozer..."
buildozer android release

echo "🔧 Modification de build.gradle..."
# Backup
cp "${DIST_DIR}/build.gradle" "${DIST_DIR}/build.gradle.bak"

# Ajouter minifyEnabled (script sed complexe ou éditeur manuel)
# TODO: automatiser avec sed/awk

echo "📋 Copie des règles ProGuard..."
cp proguard-rules.pro "${DIST_DIR}/"

echo "🏗️  Rebuild avec Gradle..."
cd "${DIST_DIR}"
./gradlew bundleRelease

echo "🔏 Signature de l'AAB..."
cd -
cp "${DIST_DIR}/build/outputs/bundle/release/macartedetarot-release.aab" "bin/macartedetarot-${VERSION}-arm64-v8a_armeabi-v7a-release.aab"
jarsigner -keystore googleplay.keystore "bin/macartedetarot-${VERSION}-arm64-v8a_armeabi-v7a-release.aab" upload
mv "bin/macartedetarot-${VERSION}-arm64-v8a_armeabi-v7a-release.aab" "bin/macartedetarot-${VERSION}-arm64-v8a_armeabi-v7a-release-signed.aab"

echo "📦 Extraction des symboles..."
./extract_debug_symbols.sh "${VERSION}"

echo "✅ Build terminé !"
```

---

## 🚨 Limitation buildozer

**Problème** : Buildozer régénère `build.gradle` à chaque `buildozer android release`  
**Conséquence** : Les modifications manuelles sont perdues  

**Solutions** :
1. Utiliser directement `./gradlew` après le premier build buildozer
2. Créer un hook p4a pour modifier automatiquement build.gradle (complexe)
3. Ne pas utiliser ProGuard (accepter l'avertissement Play Console)

---

## 🎓 Recommandation

Pour v2.1 actuelle :
- ✅ **Uploader l'AAB sans ProGuard** (déjà signé et prêt)
- ⚠️  **Accepter temporairement l'avertissement** Play Console
- 📅 **Planifier ProGuard pour v2.2+** (quand temps disponible)

Les avertissements Play Console sur ProGuard et symboles natifs sont **informatifs**, pas bloquants.  
L'app peut être publiée sans eux.

---

## 📚 Références

- [ProGuard avec Python for Android](https://github.com/kivy/python-for-android/issues/2089)
- [Buildozer ProGuard support](https://github.com/kivy/buildozer/issues/1234)
- [R8/ProGuard Android](https://developer.android.com/studio/build/shrink-code)
