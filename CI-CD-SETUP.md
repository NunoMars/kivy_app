# 🚀 CI/CD Simplifié - Android Build

## Workflows GitHub Actions

### ✅ Workflows actifs

1. **`build-android.yml`** - Build principal Android APK + AAB
   - Déclenché sur push/PR des fichiers app (`.py`, `.kv`, etc.)
   - Build APK debug pour tests
   - Build AAB release (signé si keystore configuré)
   - Upload des artifacts automatique

2. **`deploy-pages.yml`** - Déploiement GitHub Pages
   - Pour la documentation/démo web

### 🔑 Configuration keystore (AAB signé)

Pour activer la signature AAB automatique, configurez ces **GitHub Secrets** :

```
ANDROID_KEYSTORE          # Keystore en base64
ANDROID_KEYSTORE_PASSWORD # Mot de passe du keystore  
ANDROID_KEY_PASSWORD      # Mot de passe de la clé
ANDROID_KEY_ALIAS         # Alias de la clé
```

### 📋 Configuration buildozer

Un seul fichier : **`buildozer.spec`**
- Configuration complète pour APK + AAB
- Signature automatique si secrets configurés
- Exclusions optimisées pour CI/CD

### 🎯 Résultats

**Avec keystore :**
- APK debug pour tests
- **AAB signé prêt pour Play Store** ✅

**Sans keystore :**
- APK debug pour tests  
- AAB non-signé (pour tests)

### 📦 Artifacts

Les builds sont automatiquement uploadés :
- `android-apk-debug` - APK de test
- `android-aab-build` - AAB (signé ou non selon config)

Retention : 90 jours pour AAB, 30 jours pour APK debug.

## 🧹 Nettoyage effectué

Supprimés les workflows redondants :
- ❌ `build-buildozer.yml`
- ❌ `build-p4a.yml` 
- ❌ `test-build.yml`
- ❌ `pre-build-validation.yml`
- ❌ `deploy-release.yml`
- ❌ `publish-android.yml`
- ❌ `buildozer-ci.spec`

**→ Setup propre et efficace maintenant !** 🎉
