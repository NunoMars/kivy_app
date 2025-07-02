# Configuration des Secrets GitHub

Ce guide explique comment configurer les secrets GitHub nécessaires pour le pipeline Android.

## Secrets Requis

### 1. ANDROID_KEYSTORE
**Description :** Clé de signature Android encodée en base64  
**Format :** Base64 string  
**Génération :**
```bash
# Créer une clé de signature (si pas déjà fait)
keytool -genkey -v -keystore release.keystore -alias release -keyalg RSA -keysize 2048 -validity 10000

# Encoder en base64 pour GitHub
base64 -w 0 release.keystore
```

### 2. ANDROID_KEYSTORE_PASSWORD
**Description :** Mot de passe du keystore  
**Format :** String  
**Exemple :** `MonMotDePasseSecurise123`

### 3. ANDROID_KEY_ALIAS
**Description :** Alias de la clé dans le keystore  
**Format :** String  
**Exemple :** `release`

### 4. ANDROID_KEY_PASSWORD
**Description :** Mot de passe de la clé  
**Format :** String  
**Exemple :** `MonMotDePasseClé123`

### 5. GOOGLE_PLAY_SERVICE_ACCOUNT
**Description :** JSON du compte de service Google Play  
**Format :** JSON string (pas d'encodage base64)  
**Génération :** Voir guide ci-dessous

## Configuration des Secrets dans GitHub

1. Allez sur votre repository GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Cliquez sur **New repository secret**
4. Ajoutez chaque secret avec son nom exact et sa valeur

## Configuration Google Play Service Account

### Étape 1 : Créer un Service Account
1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez ou sélectionnez un projet
3. **IAM & Admin** → **Service Accounts**
4. **Create Service Account**
5. Nom : `google-play-publisher`
6. **Create and Continue**

### Étape 2 : Générer la clé JSON
1. Cliquez sur le service account créé
2. **Keys** → **Add Key** → **Create new key**
3. Type : **JSON**
4. Téléchargez le fichier JSON

### Étape 3 : Configurer Google Play Console
1. Allez sur [Google Play Console](https://play.google.com/console/)
2. **Setup** → **API access**
3. **Create new service account** (si premier)
4. **Grant access** au service account créé
5. Permissions :
   - **Release apps to testing tracks**
   - **Release apps to production**
   - **View app information and download bulk reports**

### Étape 4 : Ajouter le JSON dans GitHub
Copiez tout le contenu du fichier JSON téléchargé dans le secret `GOOGLE_PLAY_SERVICE_ACCOUNT`.

## Test de Configuration

Pour tester si tous les secrets sont bien configurés :

1. Poussez un tag de version :
```bash
git tag v1.2.0
git push --tags
```

2. Vérifiez le workflow GitHub Actions
3. Si échec, consultez les logs pour identifier le secret manquant

## Sécurité

⚠️ **Important :**
- Ne jamais committer les clés dans le repository
- Utiliser des mots de passe forts
- Restreindre les permissions du service account Google Play
- Régénérer les clés si compromises

## Dépannage

### Erreur "Invalid keystore"
- Vérifiez que le fichier keystore est bien encodé en base64
- Vérifiez le mot de passe du keystore

### Erreur "Key not found"
- Vérifiez l'alias de la clé
- Listez les clés : `keytool -list -keystore release.keystore`

### Erreur Google Play Upload
- Vérifiez que le service account a les bonnes permissions
- Vérifiez que l'app existe déjà sur Google Play Console
- Pour la première publication, faites-la manuellement via la console

## Contact

Pour toute question, consultez la documentation officielle :
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Google Play Publishing API](https://developers.google.com/android-publisher)
