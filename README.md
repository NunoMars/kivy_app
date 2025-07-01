# 🔮 Ma Carte de Tarot - Application Android

**Application de tirage de cartes de tarot développée avec Kivy et optimisée pour Google Play Store**

## 🎯 Fonctionnalités

- 🃏 **Tirage de cartes authentique** avec le Tarot de Marseille
- 🎨 **Interface moderne** et intuitive
- 📱 **Compatible Android** avec App Bundle (AAB) optimisé
- 🔮 **Guidance spirituelle** avec significations détaillées

## 🚀 Déploiement Automatisé

### ⚡ Déploiement Rapide

```bash
# Linux/macOS
./deploy.sh v1.0.0

# Windows PowerShell  
.\deploy.ps1 v1.0.0
```

### 📋 Processus Manuel

```bash
# 1. Validation
python validate_aab_workflow.py

# 2. Push code
git add .
git commit -m "feat: ready for production"
git push origin main

# 3. Créer release
git tag v1.0.0
git push origin v1.0.0
```

## 🏗️ Architecture Build

### 📱 Modes de Build
- **Debug** : APK pour tests (`buildozer android debug`)
- **Release** : AAB pour Google Play (`buildozer android release`)

### 🔧 Configuration
- **Platform** : Ubuntu 22.04 (GitHub Actions)
- **Java** : OpenJDK 17 LTS
- **Android** : NDK 25c, API Level 33
- **Framework** : Kivy 2.2.0

### 📦 Artefacts
- **APK Debug** : Tests et développement
- **AAB Release** : Publication Google Play Store
- **GitHub Release** : Distribution directe

## 🔑 Configuration Secrets

Pour la **signature de production** et **publication automatique**, configurer dans GitHub Settings > Secrets :

```bash
ANDROID_KEYSTORE_BASE64     # Clé de signature Android (base64)
KEYSTORE_PASSWORD          # Mot de passe keystore
KEY_ALIAS                 # Alias de la clé
KEY_PASSWORD              # Mot de passe de la clé
GOOGLE_PLAY_SERVICE_ACCOUNT # JSON API Google Play Console
```

## 🛠️ Développement Local

### Installation
```bash
# Cloner le repository
git clone <repository-url>
cd kivy_app

# Installer les dépendances
pip install -r requirements.txt

# Installer buildozer (Linux/macOS)
pip install buildozer
```

### Tests et Validation
```bash
# Validation complète
python validate_aab_workflow.py

# Test configuration AAB
python .github/scripts/test_aab_config.py

# Test génération AAB (si environnement complet)
python test_aab_generation.py
```

### Build Local (si SDK Android installé)
```bash
# Debug APK
buildozer android debug

# Release AAB (nécessite clé de signature)
buildozer android release
```

## 📊 Workflow GitHub Actions

### 🔄 Déclencheurs
- **Push main** : Build APK debug automatique
- **Create tag** : Build AAB release + publication

### 📁 Artefacts Générés
- `tarot-app-bundle` : AAB et APK (30 jours)
- GitHub Release : AAB signé attaché
- Google Play : Publication automatique (si configuré)

### 🔍 Monitoring
- Logs détaillés activés
- Diagnostics automatiques SDK/NDK
- Fallback gracieux en cas d'erreur

## 📱 Structure Application

```
kivy_app/
├── main.py                      # Point d'entrée Kivy
├── macartedetarotapp.kv         # Interface utilisateur
├── signification.py             # Module significations
├── buildozer.spec              # Configuration build Android
├── requirements.txt            # Dépendances Python
├── tarot_img/                  # Ressources images
│   ├── tapis.ico              # Icône application
│   └── MajorArcanaCards/      # Images cartes tarot
├── .github/
│   ├── workflows/             # GitHub Actions
│   └── scripts/               # Scripts utilitaires
└── docs/                      # Documentation
```

## 🔧 Scripts Utilitaires

- `validate_aab_workflow.py` : Validation complète pipeline
- `final_test_pipeline.py` : Tests finaux avant déploiement
- `deploy.sh` / `deploy.ps1` : Déploiement automatisé
- `.github/scripts/` : Configuration SDK/NDK, diagnostics

## 🎮 Utilisation Application

1. **Installation** : Télécharger AAB depuis Google Play Store
2. **Lancement** : Ouvrir "Ma Carte de Tarot"
3. **Tirage** : Sélectionner type de tirage souhaité
4. **Interprétation** : Consulter significations détaillées

## 🆘 Support et Dépannage

### Erreurs Communes
- **Build failed** : Vérifier logs GitHub Actions détaillés
- **SDK/NDK errors** : Scripts de diagnostic disponibles
- **Signature errors** : Vérifier configuration secrets

### Ressources
- [Documentation Kivy](https://kivy.org/doc/stable/)
- [Buildozer Guide](https://github.com/kivy/buildozer)
- [Google Play Console](https://play.google.com/console)

## 📄 Documentation

- [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) : Guide déploiement détaillé
- [`MISSION_COMPLETE.md`](MISSION_COMPLETE.md) : Résumé configuration finale
- [`.github/workflows/`](.github/workflows/) : Workflows GitHub Actions

## 🎉 État du Projet

**✅ READY FOR PRODUCTION**

Le pipeline AAB est finalisé, testé et validé pour la publication Google Play Store.

---

**🔮 Guidance spirituelle authentique avec le Tarot de Marseille ! 🃏**