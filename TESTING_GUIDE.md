# Guide de Test du Pipeline Android

## Test Local du Build

### 1. Prérequis
- Python 3.10+ installé
- Java JDK 17+ installé
- Git configuré

### 2. Test de Build Local (Optionnel)

```bash
# Cloner le projet
git clone https://github.com/NunoMars/kivy_app.git
cd kivy_app

# Installer les dépendances
pip install buildozer cython kivy Pillow

# Créer une clé temporaire pour test local
keytool -genkey -v -keystore test.keystore -alias testkey -keyalg RSA -keysize 2048 -validity 1

# Tenter un build (peut échouer sans SDK Android complet)
buildozer android debug
```

## Test du Pipeline GitHub Actions

### 1. Test sans Secrets (Build uniquement)

```bash
# Déclencher manuellement le workflow
# GitHub > Actions > "Build and Publish Android App" > Run workflow
```

**Attendu :** Le build doit réussir jusqu'à l'étape "Build Android AAB" et échouer sur la signature (secrets manquants).

### 2. Test avec Secrets (Pipeline complet)

1. **Configurer les secrets GitHub** (voir `SECRETS_SETUP.md`)
2. **Créer et pousser un tag :**

```bash
git tag v1.2.0
git push origin v1.2.0
```

**Attendu :** Pipeline complet réussi avec AAB signé uploadé sur GitHub et Google Play.

## Vérification des Résultats

### 1. GitHub Actions
- Allez sur : https://github.com/NunoMars/kivy_app/actions
- Vérifiez que toutes les étapes sont vertes ✅
- Téléchargez l'artifact "tarot-app-bundle"

### 2. GitHub Release
- Allez sur : https://github.com/NunoMars/kivy_app/releases
- Vérifiez que la release contient le fichier `.aab`

### 3. Google Play Console
- Allez sur : https://play.google.com/console/
- Vérifiez la nouvelle version en "Internal testing"

## Diagnostic des Erreurs

### Erreur : "SDK not found"
```
# Android SDK found at /usr/local/lib/android/sdk
# sdkmanager path "..." does not exist
```
**Solution :** Problème de configuration SDK dans le workflow. Les liens symboliques devraient corriger cela.

### Erreur : "Invalid keystore"
```
❌ Clé de production invalide
```
**Solution :** 
- Vérifiez que `ANDROID_KEYSTORE` est bien en base64
- Vérifiez le mot de passe `ANDROID_KEYSTORE_PASSWORD`

### Erreur : "Key not found"
```
Key alias not found: XXX
```
**Solution :**
- Vérifiez `ANDROID_KEY_ALIAS` (doit correspondre à la clé)
- Listez les clés : `keytool -list -keystore release.keystore`

### Erreur : Google Play Upload
```
Package not found: org.tarot.macartedetarot
```
**Solution :**
- L'app doit d'abord être créée manuellement sur Google Play Console
- Uploadez la première version manuellement

## Test Rapide des Scripts

### Linux/macOS
```bash
# Test de création de clé
./create_signing_key.sh

# Test de l'icône
python3 create_android_icon.py

# Test des corrections buildozer
python3 fix_buildozer_errors.py
```

### Windows
```powershell
# Test de création de clé
.\create_signing_key.ps1

# Test de l'icône
python create_android_icon.py

# Test des corrections buildozer
python fix_buildozer_errors.py
```

## Nettoyage Après Test

```bash
# Supprimer les fichiers de test
rm -f test.keystore temp.keystore

# Nettoyer buildozer cache (si test local)
rm -rf .buildozer bin

# Supprimer les tags de test (optionnel)
git tag -d v1.2.0
git push origin --delete v1.2.0
```

## Tests de Performance

- **Temps de build attendu :** 15-25 minutes
- **Taille AAB attendue :** 25-35 MB
- **Architectures :** arm64-v8a, armeabi-v7a, x86, x86_64

## Validation Finale

✅ AAB généré et signé  
✅ Compatible Google Play Store  
✅ Version uploadée automatiquement  
✅ Release GitHub créée  
✅ Pas d'erreurs de signature  
✅ Toutes les architectures incluses  

---

🔮 **Ready for Production!**
