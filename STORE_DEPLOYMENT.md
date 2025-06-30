# Guide de Publication sur les Stores via GitHub

## 🚀 Vue d'ensemble

Ce guide vous explique comment publier automatiquement votre app Tarot sur Google Play Store et Apple App Store en utilisant GitHub Actions.

## 📱 Google Play Store (Android)

### 1. Préparation du compte développeur

1. **Créer un compte Google Play Console** (25$ une fois)
   - Aller sur https://play.google.com/console
   - Créer un compte développeur
   - Payer les frais uniques de 25$

2. **Créer l'application**
   - Créer une nouvelle app dans la Console
   - Choisir le nom : "Ma Carte de Tarot"
   - Package name : `com.votrecompany.tarot`

### 2. Configuration GitHub

#### A. Secrets GitHub requis

Dans votre repo GitHub, allez dans Settings > Secrets and variables > Actions :

```
KEYSTORE_PASSWORD=VotreMotDePasseKeystore
KEY_ALIAS=VotreAliasKey
KEY_PASSWORD=VotreMotDePasseKey
GOOGLE_PLAY_SERVICE_ACCOUNT={"type":"service_account",...}
```

#### B. Générer une clé de signature

```bash
# Générer le keystore
keytool -genkey -v -keystore tarot-release-key.keystore -alias tarot-key -keyalg RSA -keysize 2048 -validity 10000

# Stocker le keystore en base64 dans les secrets GitHub
base64 tarot-release-key.keystore > keystore.txt
```

### 3. Service Account Google Play

1. **Google Cloud Console**
   - Créer un projet
   - Activer Google Play Developer API
   - Créer un Service Account
   - Télécharger le JSON

2. **Play Console**
   - Setup > API access
   - Lier le Service Account
   - Donner les permissions

### 4. Publication automatique

```bash
# Créer un tag pour déclencher la publication
git tag v1.0.0
git push origin v1.0.0
```

## 🍎 Apple App Store (iOS)

### 1. Préparation

1. **Apple Developer Program** (99$/an)
2. **App Store Connect** account
3. **Xcode** (nécessite macOS)

### 2. GitHub Actions pour iOS

```yaml
# .github/workflows/publish-ios.yml
name: Publish iOS App

on:
  push:
    tags: ['v*']

jobs:
  build-ios:
    runs-on: macos-latest
    steps:
    - uses: actions/checkout@v4
    - name: Install kivy-ios
      run: |
        pip install kivy-ios
        toolchain build python3 kivy
    - name: Build iOS app
      run: |
        toolchain create YourApp .
        cd YourApp-ios
        xcodebuild -configuration Release
```

## 🔄 Workflow de publication

### 1. Développement
```bash
git add .
git commit -m "Nouvelle fonctionnalité"
git push
```

### 2. Tests automatiques
- GitHub Actions lance les tests
- Vérifie la compilation
- Génère des builds de test

### 3. Publication
```bash
# Version de test
git tag v1.0.0-beta
git push origin v1.0.0-beta

# Version production
git tag v1.0.0
git push origin v1.0.0
```

## 📊 Stratégie de déploiement

### Phase 1 : Tests internes
1. **Internal Testing** (Google Play)
2. **TestFlight** (iOS)
3. Inviter 20-100 testeurs

### Phase 2 : Tests fermés
1. **Closed Alpha/Beta**
2. Inviter plus d'utilisateurs
3. Récolter feedback

### Phase 3 : Production
1. **Open Beta** (optionnel)
2. **Production Release**
3. Marketing et promotion

## 🛠️ Outils utiles

### GitHub Actions Marketplace
- `actions/checkout@v4`
- `actions/setup-python@v4`
- `r0adkll/upload-google-play@v1`
- `apple-actions/import-codesign-certs@v1`

### Services tiers
- **Fastlane** : Automatisation avancée
- **CodeMagic** : CI/CD pour mobile
- **Bitrise** : Alternative à GitHub Actions

## 💰 Coûts estimés

### Google Play Store
- Compte développeur : 25$ (une fois)
- Maintenance : Gratuit

### Apple App Store
- Apple Developer Program : 99$/an
- App Store Connect : Gratuit

### GitHub
- Actions : 2000 minutes/mois gratuites
- Stockage : 500MB gratuit

## 🎯 Checklist avant publication

### Technique
- [ ] App compilée sans erreur
- [ ] Tests automatisés passent
- [ ] Permissions Android déclarées
- [ ] Icons et splash screen

### Légal
- [ ] Politique de confidentialité
- [ ] Conditions d'utilisation
- [ ] Conformité RGPD
- [ ] Droits d'auteur des images

### Store
- [ ] Description app
- [ ] Screenshots
- [ ] Mots-clés SEO
- [ ] Catégorie appropriée

## 🚀 Commandes rapides

```bash
# Initialiser Git
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/username/tarot-app.git
git push -u origin main

# Publier version
git tag v1.0.0
git push origin v1.0.0

# Vérifier build
# GitHub Actions se charge du reste !
```

---

**Note** : Ce processus peut sembler complexe au début, mais une fois configuré, publier une nouvelle version se résume à créer un tag Git ! 🎯
