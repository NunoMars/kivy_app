# 🔐 Guide Complet - Génération Clé de Signature Android

## 📋 Prérequis Windows

### 1. Installer Java JDK
```powershell
# Option A: Télécharger depuis Microsoft
# https://docs.microsoft.com/java/openjdk/download#openjdk-17
# Télécharger "Microsoft Build of OpenJDK 17" pour Windows x64

# Option B: Via Chocolatey (si installé)
choco install openjdk17

# Option C: Via Winget
winget install Microsoft.OpenJDK.17
```

### 2. Vérifier l'installation
```powershell
java -version
# Doit afficher: openjdk version "17.x.x"

keytool -help
# Doit afficher l'aide de keytool
```

## 🔑 Génération Manuelle de la Clé

Si le script Python ne fonctionne pas, voici la méthode manuelle :

### 1. Générer la clé
```bash
keytool -genkey -v -keystore macartedetarot-release.keystore -alias macartedetarot -keyalg RSA -keysize 2048 -validity 10000
```

**Répondre aux questions :**
- **Mot de passe keystore** : Choisir un mot de passe fort (min 6 caractères)
- **Nom et prénom** : Ma Carte de Tarot
- **Unité organisationnelle** : Mobile Apps  
- **Organisation** : Tarot Software
- **Ville** : Paris
- **État/Province** : Ile-de-France
- **Code pays** : FR
- **Mot de passe clé** : Même que keystore ou différent

### 2. Vérifier la clé
```bash
keytool -list -keystore macartedetarot-release.keystore
```

### 3. Encoder en base64
```powershell
# Windows PowerShell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("macartedetarot-release.keystore")) > keystore.base64

# Afficher le contenu
Get-Content keystore.base64
```

## 🔧 Configuration Secrets GitHub

Aller dans **GitHub Repository > Settings > Secrets and variables > Actions**

Cliquer **"New repository secret"** pour chaque :

1. **ANDROID_KEYSTORE_BASE64**
   - Copier tout le contenu du fichier `keystore.base64`

2. **KEYSTORE_PASSWORD** 
   - Le mot de passe du keystore

3. **KEY_ALIAS**
   - `macartedetarot`

4. **KEY_PASSWORD**
   - Le mot de passe de la clé (souvent identique au keystore)

## 🚀 Test de la Configuration

### 1. Créer un tag test
```bash
git add .
git commit -m "feat: clé de signature production configurée"
git push origin main
git tag v1.0.1-test
git push origin v1.0.1-test
```

### 2. Surveiller le build
- Aller dans **Actions** tab de GitHub
- Vérifier que l'étape "Sign Release AAB" réussit
- Chercher "✅ AAB correctement signé avec clé production"

### 3. Télécharger et tester l'AAB
- Télécharger depuis **Artifacts** ou **Releases**
- Vérifier : `jarsigner -verify macartedetarot-production.aab`
- Uploader sur Google Play Console

## 🔍 Dépannage

### Erreur "Keystore tampered" 
- La clé base64 est incorrecte
- Re-générer le base64 et re-configurer le secret

### Erreur "Wrong password"
- Vérifier KEYSTORE_PASSWORD et KEY_PASSWORD
- Tester localement avec la clé

### Erreur "Alias not found"  
- Vérifier KEY_ALIAS = "macartedetarot"
- Lister les alias : `keytool -list -keystore xxx.keystore`

## 📁 Structure Finale

```
kivy_app/
├── macartedetarot-release.keystore  # ⚠️ NE PAS COMMITTER
├── keystore.base64                  # ⚠️ NE PAS COMMITTER  
├── generate_signing_key.py         # Script automatique
├── SIGNING_KEY_SOLUTION.md         # Ce guide
└── .gitignore                      # Mis à jour pour ignorer .keystore
```

## 🎯 Résultat Final

Avec la clé configurée correctement :
- ✅ AAB signé avec certificat valide
- ✅ Upload Google Play Console réussi
- ✅ Plus d'erreur "doit être signé"
- ✅ Publication automatique fonctionnelle

**La clé de signature résout définitivement le problème !** 🔐🎮
