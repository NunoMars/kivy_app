# 🔑 Guide Complet - Clés Google Play Console

## 📋 Deux Types de Clés Nécessaires

### 1. 🔐 Clé de Signature Android (OBLIGATOIRE)
**Problème actuel :** "Tous les app bundles importés doivent être signés"
**Solution :** Clé de signature Android (.keystore)

### 2. 🚀 Clé API Google Play Console (OPTIONNELLE)
**Fonction :** Publication automatique via GitHub Actions
**Solution :** Service Account Google Cloud Platform

## 🔐 ÉTAPE 1 : Clé de Signature Android

### Génération de la Clé
```bash
# Méthode automatique (recommandée)
python generate_signing_key.py

# Méthode manuelle
keytool -genkey -v -keystore macartedetarot-release.keystore -alias macartedetarot -keyalg RSA -keysize 2048 -validity 10000
```

### Configuration GitHub Secrets
Dans **Repository Settings > Secrets and variables > Actions** :
- `ANDROID_KEYSTORE_BASE64` → Clé encodée en base64
- `KEYSTORE_PASSWORD` → Mot de passe keystore
- `KEY_ALIAS` → macartedetarot
- `KEY_PASSWORD` → Mot de passe clé

**Résultat :** AAB correctement signé, upload manuel possible

## 🚀 ÉTAPE 2 : Clé API Google Play Console (Publication Auto)

### A. Créer un Service Account Google Cloud

1. **Aller sur Google Cloud Console**
   - https://console.cloud.google.com/

2. **Créer/Sélectionner un Projet**
   - Projet existant ou nouveau pour votre app

3. **Activer l'API Google Play Developer**
   - APIs & Services > Library
   - Rechercher "Google Play Developer API"
   - Cliquer "Enable"

4. **Créer un Service Account**
   - IAM & Admin > Service Accounts
   - "Create Service Account"
   - Nom : `google-play-publisher`
   - Description : `Service account for publishing to Google Play`

5. **Générer la Clé JSON**
   - Cliquer sur le service account créé
   - Keys > Add Key > Create New Key
   - Type : JSON
   - **Télécharger le fichier JSON** (gardez-le secret !)

### B. Configurer les Permissions Google Play Console

1. **Aller sur Google Play Console**
   - https://play.google.com/console/

2. **Configuration du Compte de Service**
   - Settings > API access
   - "Link a Google Cloud project"
   - Sélectionner votre projet Google Cloud
   - Grant access au service account créé

3. **Définir les Permissions**
   - App permissions : Sélectionner votre app "Ma Carte de Tarot"
   - Account permissions :
     - ✅ View app information and download bulk reports
     - ✅ Manage store presence
     - ✅ Manage production releases
     - ✅ Manage testing track releases

### C. Configurer GitHub Secret

Dans **Repository Settings > Secrets** :
- Nom : `GOOGLE_PLAY_SERVICE_ACCOUNT`
- Valeur : **Contenu COMPLET du fichier JSON** téléchargé

## 🎯 Résultats selon Configuration

### Avec Clé de Signature SEULEMENT
- ✅ AAB correctement signé
- ✅ Upload manuel sur Google Play Console réussi
- ❌ Publication automatique non disponible

### Avec Clé de Signature + API Google Play
- ✅ AAB correctement signé
- ✅ Upload automatique via GitHub Actions
- ✅ Publication automatique sur track "internal"
- ✅ Promotion manuelle vers production possible

## 🔧 Configuration Workflow

Le workflow actuel est configuré pour :

```yaml
- name: Upload to Google Play Console
  if: startsWith(github.ref, 'refs/tags/') && success()
  uses: r0adkll/upload-google-play@v1.1.3
  with:
    serviceAccountJsonPlainText: ${{ secrets.GOOGLE_PLAY_SERVICE_ACCOUNT }}
    packageName: org.tarot.macartedetarot
    releaseFiles: bin/*.aab
    track: internal  # Publication sur track interne
    status: completed
```

## 📋 Ordre de Priorité Recommandé

### 1. URGENT : Clé de Signature Android
**Sans cette clé :** AAB non accepté par Google Play
**Avec cette clé :** Upload manuel possible

### 2. OPTIONNEL : API Google Play Console
**Sans cette clé :** Publication manuelle uniquement
**Avec cette clé :** Publication automatisée complète

## 🚀 Actions Immédiates

```powershell
# 1. Générer la clé de signature (priorité absolue)
python generate_signing_key.py

# 2. Configurer les secrets GitHub de signature
# (ANDROID_KEYSTORE_BASE64, KEYSTORE_PASSWORD, etc.)

# 3. Tester avec un build
.\deploy.ps1 v1.0.1

# 4. OPTIONNEL : Configurer l'API Google Play pour l'auto-publication
```

## 💡 Conseil

**Commencez par la clé de signature Android uniquement !**
- Résout immédiatement l'erreur "doit être signé"
- Permet l'upload manuel sur Google Play
- L'API Google Play peut être ajoutée plus tard

**L'API Google Play Console n'est qu'un bonus pour automatiser la publication.**

---

**🎯 Priorité 1 : Clé de signature Android → Résout le problème immédiatement !**
