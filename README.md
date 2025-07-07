# 🃏 Ma Carte de Tarot - Application And## 🔐 Configuration des Secrets GitHub

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
