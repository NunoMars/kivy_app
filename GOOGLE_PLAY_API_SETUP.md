# 🚀 GUIDE COMPLET : Configuration API Google Play Console

## ✅ ÉTAPE 1 TERMINÉE : Clé de Signature Android
Votre clé de signature Android est créée ! Maintenant configurons l'API Google Play pour l'automatisation complète.

## 🎯 ÉTAPE 2 : Configuration API Google Play Console

### A. Prérequis
- ✅ Application déjà créée sur Google Play Console
- ✅ Compte développeur Google Play (25€ unique)
- ✅ Clé de signature Android configurée (fait !)

### B. Création du Service Account Google Cloud Platform

#### 1. Aller sur Google Cloud Console
🌐 **URL** : https://console.cloud.google.com/

#### 2. Créer/Sélectionner un Projet
```
- Cliquer "Sélectionner un projet" en haut
- "Nouveau projet" 
- Nom : "ma-carte-tarot-publish" (ou similaire)
- Créer
```

#### 3. Activer l'API Google Play Developer
```
- Menu ☰ → APIs & Services → Library
- Rechercher : "Google Play Developer API"
- Cliquer sur "Google Play Developer API"
- Cliquer "ENABLE" (Activer)
```

#### 4. Créer un Service Account
```
- Menu ☰ → IAM & Admin → Service Accounts
- "CREATE SERVICE ACCOUNT" (Créer un compte de service)
- Nom : google-play-publisher
- Description : Service account for publishing Ma Carte de Tarot to Google Play
- Créer et continuer
- Role : Laisser vide pour l'instant
- Terminer
```

#### 5. Générer la Clé JSON
```
- Cliquer sur le service account créé (google-play-publisher@...)
- Onglet "KEYS" 
- "ADD KEY" → "Create new key"
- Type : JSON
- CREATE
- 📥 Télécharger le fichier JSON (ex: ma-carte-tarot-publish-abc123.json)
```

⚠️ **IMPORTANT** : Gardez ce fichier JSON secret ! Il donne accès à votre compte Google Play.

### C. Configurer les Permissions Google Play Console

#### 1. Aller sur Google Play Console
🌐 **URL** : https://play.google.com/console/

#### 2. Lier le Projet Google Cloud
```
- Settings (Paramètres) → API access
- "Link Google Cloud Project" 
- Sélectionner votre projet : "ma-carte-tarot-publish"
- Link project
```

#### 3. Configurer le Service Account
```
- Dans API access, section "Service accounts"
- Trouver votre service account : google-play-publisher@...
- Cliquer "Grant access" (Accorder l'accès)
```

#### 4. Définir les Permissions
```
📱 App permissions :
   ✅ Ma Carte de Tarot (sélectionner votre app)

🔐 Account permissions :
   ✅ View app information and download bulk reports
   ✅ Manage store presence  
   ✅ Manage production releases
   ✅ Manage testing track releases
   
💰 Financial permissions :
   ❌ Aucune (pas nécessaire pour publication)
```

#### 5. Sauvegarder
```
- "Invite user" ou "Save"
- Le service account est maintenant configuré
```

### D. Configurer le Secret GitHub

#### 1. Préparer le JSON
```powershell
# Copier le contenu COMPLET du fichier JSON téléchargé
Get-Content "ma-carte-tarot-publish-abc123.json" | Set-Clipboard
```

#### 2. Ajouter le Secret GitHub
```
🌐 URL : https://github.com/VOTRE_USERNAME/kivy_app/settings/secrets/actions

Nouveau secret :
- Name : GOOGLE_PLAY_SERVICE_ACCOUNT
- Secret : [Coller le contenu JSON complet]
```

Le JSON doit ressembler à :
```json
{
  "type": "service_account",
  "project_id": "ma-carte-tarot-publish",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "google-play-publisher@ma-carte-tarot-publish.iam.gserviceaccount.com",
  "client_id": "123456789...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
}
```

## 📊 RÉCAPITULATIF DES SECRETS GITHUB

Après configuration complète, vous devriez avoir **5 secrets** :

### 🔐 Signature Android (OBLIGATOIRE - Fait !)
1. **ANDROID_KEYSTORE_BASE64** → `MIILBAIBAzCCCq4GCSqGSIb3DQEH...`
2. **KEYSTORE_PASSWORD** → `BkRbqu&DK6KIYg@r`
3. **KEY_ALIAS** → `macartedetarot`
4. **KEY_PASSWORD** → `WdQ#CV^frVQfa#Zd`

### 🚀 Publication Automatique (OPTIONNEL)
5. **GOOGLE_PLAY_SERVICE_ACCOUNT** → `{"type":"service_account",...}`

## 🎯 TEST DE LA CONFIGURATION COMPLÈTE

Une fois les 5 secrets configurés :

```powershell
# Tester le build complet avec publication automatique
.\deploy.ps1 v1.0.1

# Vérifier que :
# ✅ AAB est généré et signé
# ✅ Upload automatique sur Google Play Console (track internal)
# ✅ Disponible dans Play Console → Testing → Internal testing
```

## 🔄 WORKFLOW COMPLET APRÈS CONFIGURATION

### Avec les 5 secrets configurés :

1. **Push d'un tag** (`v1.0.1`) déclenche automatiquement :
   - 🔧 Build AAB avec buildozer
   - 🔑 Signature avec votre clé de production
   - 📤 Upload automatique sur Google Play Console
   - 🚀 Publication sur track "internal"
   - 📋 Création d'une release GitHub

2. **Publication manuelle** depuis Play Console :
   - Play Console → Testing → Internal testing
   - Promouvoir vers "Production" quand prêt

## 💡 CONSEILS DE SÉCURITÉ

### Fichiers à JAMAIS commiter :
```
✅ Déjà dans .gitignore :
- *.keystore
- *.keystore.base64
- *.keystore.config
- *service-account*.json
- *google-play*.json
```

### Stockage local sécurisé :
```
📁 Recommandé :
- Dossier chiffré ou coffre-fort numérique
- Backup de la clé .keystore sur support externe
- Documentation des mots de passe dans gestionnaire
```

## 🎉 RÉSULTAT FINAL

Avec cette configuration, vous avez :

- ✅ **Problème "doit être signé"** → RÉSOLU
- ✅ **Build AAB automatique** → Fonctionnel  
- ✅ **Signature de production** → Automatique
- ✅ **Upload Google Play** → Automatique
- ✅ **Publication track internal** → Automatique
- 🎯 **Publication production** → Manuelle (sécurisé)

---

## 🚀 PROCHAINES ÉTAPES

1. **MAINTENANT** : Configurer les secrets GitHub (4 ou 5)
2. **ENSUITE** : Tester avec `.\deploy.ps1 v1.0.1`
3. **FINALISER** : Publier sur Google Play Store !

Voulez-vous que je vous aide à configurer les secrets GitHub ou tester le déploiement ?
