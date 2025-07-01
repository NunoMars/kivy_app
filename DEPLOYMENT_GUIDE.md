# 🚀 Guide de Déploiement AAB - Ma Carte de Tarot

## ✅ État Actuel du Projet

**Validation réussie !** Le workflow est prêt pour générer des App Bundles Android (AAB) pour Google Play Store.

### 📊 Configuration Validée

- ✅ **Application Kivy** : main.py, interface KV, ressources images
- ✅ **buildozer.spec** : Debug APK, Release AAB, NDK 25c, API 33
- ✅ **GitHub Actions** : Workflows build et publication optimisés
- ✅ **Scripts utilitaires** : Configuration SDK, tests, diagnostics

## 🔧 Architecture du Workflow

### 📱 Modes de Build
```bash
# Debug : Génère un APK
buildozer android debug
→ bin/macartedetarot-debug.apk

# Release : Génère un AAB
buildozer android release  
→ bin/macartedetarot-release.aab
```

### 🔑 Système de Signature
1. **Sans secrets** : Clé temporaire pour tests
2. **Avec secrets** : Clé production pour Google Play

## 🚀 Déploiement

### 1. Pousser le Code
```bash
git add .
git commit -m "feat: workflow AAB prêt pour Google Play Store"
git push origin main
```

### 2. Déclencher un Build de Test
Le workflow se lance automatiquement sur push et génère :
- APK debug pour tests
- AAB avec clé temporaire

### 3. Déclencher une Release
```bash
# Créer un tag pour déclencher la publication
git tag v1.0.0
git push origin v1.0.0
```

## 🔑 Configuration Secrets Production

Pour publier sur Google Play Store, configurer dans GitHub Settings > Secrets :

### Clé de Signature Android
```bash
# Générer une clé keystore
keytool -genkey -v -keystore macartedetarot.keystore -alias macartedetarot \
  -keyalg RSA -keysize 2048 -validity 10000

# Encoder en base64
base64 -w 0 macartedetarot.keystore > keystore.base64
```

### Secrets GitHub Required
- `ANDROID_KEYSTORE_BASE64` : Contenu du fichier keystore.base64
- `KEYSTORE_PASSWORD` : Mot de passe du keystore
- `KEY_ALIAS` : Alias de la clé (ex: macartedetarot)
- `KEY_PASSWORD` : Mot de passe de la clé

### Google Play Console API
- `GOOGLE_PLAY_SERVICE_ACCOUNT` : JSON du compte de service Google Play

## 📦 Artefacts Générés

### GitHub Actions Artifacts
- `tarot-app-bundle` : AAB et APK générés
- Rétention : 30 jours

### GitHub Releases (sur tag)
- `ma-carte-tarot-v1.0.0.aab` : AAB signé pour Google Play
- Description automatique avec notes de version

### Google Play Console (si configuré)
- Publication automatique sur track "internal"
- Promotion manuelle vers production

## 🛠️ Diagnostics et Tests

### Scripts Disponibles
```bash
# Valider la configuration complète
python validate_aab_workflow.py

# Tester la config AAB
python .github/scripts/test_aab_config.py

# Diagnostic SDK (sur Ubuntu CI)
python .github/scripts/fix_sdk_paths.py

# Configuration buildozer
python .github/scripts/configure_buildozer_sdk.py
```

### Tests Locaux (si buildozer installé)
```bash
# Test génération AAB complet
python test_aab_generation.py
```

## 🔍 Monitoring et Debug

### Logs GitHub Actions
- Workflow `publish-android.yml` : Build et publication
- Workflow `build-android.yml` : Build simple
- Diagnostics détaillés activés

### Vérifications Post-Build
- Présence du fichier `.aab` dans `bin/`
- Signature correcte avec `jarsigner`
- Upload vers les plateformes cibles

## 📋 Checklist Finale

- [x] Configuration buildozer : APK debug, AAB release
- [x] Workflow GitHub Actions opérationnel
- [x] Scripts de diagnostic et configuration
- [x] Validation complète réussie
- [ ] Secrets GitHub configurés (pour production)
- [ ] Test de build réel via GitHub Actions
- [ ] Première publication test sur Google Play

## 🎯 Prochaines Étapes

1. **Push et Test** : Pousser le code et vérifier le build automatique
2. **Configuration Secrets** : Ajouter les clés de signature production
3. **Test Release** : Créer un tag et vérifier la génération AAB
4. **Google Play Setup** : Configurer l'API et publier la première version
5. **Automatisation Complète** : Publication automatique sur tag

## 🆘 Support et Dépannage

### Erreurs Communes
- **SDK/NDK** : Scripts de diagnostic disponibles
- **Signature** : Clés temporaires pour tests sans secrets
- **Build Timeout** : Timeout 30min configuré pour builds longs

### Contacts et Ressources
- Documentation Kivy : https://kivy.org/doc/stable/
- Documentation Buildozer : https://github.com/kivy/buildozer
- Google Play Console : https://play.google.com/console

---
**✨ Configuration AAB finalisée et validée !**
Le workflow est prêt pour générer des App Bundles optimisés pour Google Play Store.
