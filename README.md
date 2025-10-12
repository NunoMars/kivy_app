# 🃏 Ma Carte de Tarot - Applicatio# 🃏 Ma Carte de Tarot - Application Android

Application Kivy de tirage de cartes de tarot avec déploiement automatique sur Google Play Store et **monétisation AdMob**.

## ☁️ Backend Gemini (FastAPI)

Un micro-service FastAPI (`backend/app.py`) expose un endpoint `/chat` pour relayer les demandes vers Google Gemini. Idéal pour l’hébergement sur **Hugging Face Spaces**.

### Déploiement rapide sur Hugging Face

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
```

Variables d’environnement requises :

- `GEMINI_API_KEY` : clé API Google Generative AI.

Dans Hugging Face Spaces (type « FastAPI »), ajoutez le fichier `backend/requirements.txt` et définissez `GEMINI_API_KEY` dans les Secrets Space Settings.

### Contrat API

- `POST /chat` accepte `message` (texte), `language` (optionnel) et `session_id` (recommandé). Chaque `session_id` ne recoit qu’une seule guidance : toute requete ulterieure renvoie un message de politesse invitant a revenir plus tard.
- La langue de reponse suit `language` si fourni, sinon elle est detectee automatiquement.

## 🚀 Déploiement

Pour créer une nouvelle version :

```bash
# Créer un tag et pousser (déclenche automatiquement le build)
git tag v1.0.2
git push origin v1.0.2
```

Le pipeline GitHub Actions se charge automatiquement de :

- Compiler l'application Android (AAB)

## 💰 Monétisation AdMob

L'application intègre un système de publicités AdMob avec **configuration JSON dynamique** (pas besoin de rebuild pour changer les IDs).

### 📚 Documentation AdMob

| Fichier | Description |
|---------|-------------|
| **[ADMOB_QUICK_REFERENCE.md](docs/ADMOB_QUICK_REFERENCE.md)** | � Guide de référence rapide (commandes, config) |
| **[ADMOB_WORKFLOW.md](docs/ADMOB_WORKFLOW.md)** | 🔄 Workflow complet test → production |
| **[ADMOB_INTEGRATION.md](docs/ADMOB_INTEGRATION.md)** | 📖 Documentation technique complète |
| **[ADMOB_INTEGRATION_EXAMPLE.py](docs/ADMOB_INTEGRATION_EXAMPLE.py)** | 💻 Exemples de code |

### ⚡ Démarrage Rapide AdMob

```powershell
# Déployer config en mode TEST (IDs Google de test)
.\deploy_config.ps1 test

# Déployer config en mode PRODUCTION (tes IDs AdMob)
.\deploy_config.ps1 prod
```

**Avantage :** Change les IDs AdMob **sans rebuilder l'APK** !

### 🎯 Fichiers AdMob

- `ads_manager.py` - Gestionnaire AdMob (250+ lignes)
- `config.default.json` - Config embarquée (mode TEST par défaut)
- `deploy_config.ps1` - Script PowerShell de déploiement
- `resources/values/strings.xml` - AdMob App ID Android

**Voir [ADMOB_QUICK_REFERENCE.md](docs/ADMOB_QUICK_REFERENCE.md) pour plus de détails.**iguration des Secrets GitHub

https://play.google.com/apps/internaltest/4699508915394093740

Le projet nécessite les secrets suivants dans GitHub > Settings > Secrets and variables > Actions :

| Secret                          | Description                        |
| ------------------------------- | ---------------------------------- |
| `ANDROID_KEYSTORE`            | Clé de signature Android (base64) |
| `ANDROID_KEYSTORE_PASSWORD`   | Mot de passe du keystore           |
| `ANDROID_KEY_ALIAS`           | Alias de la clé (ex: release)     |
| `ANDROID_KEY_PASSWORD`        | Mot de passe de la clé            |
| `GOOGLE_PLAY_SERVICE_ACCOUNT` | Clé API Google Play (JSON)        |

### 🔑 Génération des Clés de Signature

**Linux/macOS :**

```bash
./create_signing_key.sh
```

**Windows :**

```powershell
.\create_signing_key.ps1
```

**Manuel :**

```bash
keytool -genkey -v -keystore release.keystore -alias release -keyalg RSA -keysize 2048 -validity 10000
base64 -w 0 release.keystore  # Pour Linux/macOS
```

📖 **Guide complet :** Voir `SECRETS_SETUP.md`lication Kivy de tirage de cartes de tarot avec déploiement automatique sur Google Play Store.

## 🚀 Déploiement

Pour créer une nouvelle version :

```bash
# Créer un tag et pousser (déclenche automatiquement le build)
git tag v1.0.2
git push origin v1.0.2
```

Le pipeline GitHub Actions se charge automatiquement de :

- Compiler l'application Android (AAB)
- Signer avec la clé de production
- Publier sur Google Play Store

## 📁 Structure du Projet

```
kivy_app/
├── main.py                    # Application principale Kivy
├── macartedetarotapp.kv       # Interface utilisateur
├── signification.py           # Logique métier tarot
├── requirements.txt           # Dépendances Python
├── buildozer.spec             # Configuration Android
├── .github/workflows/         # Pipeline CI/CD
│   ├── publish-android.yml    # Workflow principal Android
│   └── deploy-pages.yml       # Déploiement GitHub Pages
├── docs/                      # Site web (GitHub Pages)
│   ├── index.html            # Page d'accueil
│   └── privacy-policy.html   # Politique de confidentialité
├── tarot_img/                 # Images et icônes
├── googleplay.keystore        # Clé de signature Android
├── google-play-service-account.json  # Clé API Google Play
└── macartedetarot-signed-production.aab  # AAB final signé
```

## � Configuration des Secrets GitHub

Le projet nécessite les secrets suivants dans GitHub > Settings > Secrets and variables > Actions :

| Secret                          | Description                        |
| ------------------------------- | ---------------------------------- |
| `ANDROID_KEYSTORE`            | Clé de signature Android (base64) |
| `ANDROID_KEYSTORE_PASSWORD`   | Mot de passe du keystore           |
| `ANDROID_KEY_ALIAS`           | Alias de la clé (ex: googleplay)  |
| `ANDROID_KEY_PASSWORD`        | Mot de passe de la clé            |
| `GOOGLE_PLAY_SERVICE_ACCOUNT` | Clé API Google Play (JSON)        |

## 📱 Workflow Automatique

1. **Android App :** Tag Git → Build AAB → Signature → Upload Google Play
2. **GitHub Pages :** Push docs/ → Build site → Déploiement automatique
3. **Durée :** ~15-20 minutes pour Android, ~2 minutes pour le site
4. **Monitoring :** https://github.com/NunoMars/kivy_app/actions
5. **Site web :** https://nunomars.github.io/kivy_app/

## 🌐 Site Web

Le projet inclut un site web accessible via GitHub Pages :

- **Page d'accueil :** Présentation de l'application
- **Politique de confidentialité :** Conformité RGPD
- **Support utilisateur :** Contact et documentation

## 🎯 Fonctionnalités

- ✅ Application Kivy fonctionnelle avec Tarot de Marseille
- ✅ Pipeline CI/CD entièrement automatisé
- ✅ Build AAB optimisé (Android API 34)
- ✅ Signature automatique avec clé de production
- ✅ Publication automatique sur Google Play Console
- ✅ Conformité totale Google Play Store

---

🔮 **Découvrez votre avenir avec le Tarot de Marseille authentique !**
