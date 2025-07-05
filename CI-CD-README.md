# 🤖 Système de CI/CD Automatisé - Kivy Tarot App

## 📋 Vue d'ensemble

Ce projet utilise maintenant un système de CI/CD intelligent qui ne déclenche les builds que lorsque c'est nécessaire, optimisant ainsi les ressources et le temps de développement.

## 🔄 Workflows Automatisés

### 1. **Pre-Build Validation** (`pre-build-validation.yml`)
- **Déclenchement** : Pull Requests sur `main`/`master`
- **Rôle** : Validation rapide avant merge
- **Actions** :
  - ✅ Vérification syntaxe Python
  - ✅ Validation `buildozer.spec`
  - ✅ Vérification `requirements.txt`
  - ✅ Test structure projet
  - ✅ Test d'import des modules

### 2. **Test Build** (`test-build.yml`)
- **Déclenchement** : Push sur `main` + fichiers applicatifs modifiés
- **Rôle** : Tests rapides de configuration
- **Durée** : ~2-3 minutes
- **Fichiers surveillés** :
  - `*.py`
  - `*.kv`
  - `requirements.txt`
  - `buildozer.spec`
  - `.github/workflows/**`

### 3. **Build Android AAB** (`build-p4a.yml`)
- **Déclenchement** : Push sur `main` + fichiers app/assets modifiés
- **Rôle** : Build complète Android avec signature
- **Durée** : ~15-20 minutes
- **Fichiers surveillés** :
  - `*.py`
  - `*.kv`
  - `requirements.txt`
  - `buildozer.spec`
  - `tarot_img/**`

### 4. **Deploy Release** (`deploy-release.yml`)
- **Déclenchement** : Release GitHub publiée
- **Rôle** : Build finale signée pour Play Store
- **Durée** : ~20-25 minutes
- **Outputs** : AAB signé prêt pour production

## 🎯 Déclenchements Conditionnels

### ✅ Déclenche une build complète :
```
main.py
macartedetarotapp.kv
signification.py
requirements.txt
buildozer.spec
tarot_img/nouvelle_image.jpg
```

### ⏭️ Ne déclenche PAS de build :
```
README.md
guides/guide_wsl2.py
docs/installation.md
.gitignore
__pycache__/
.vscode/settings.json
```

## 🔧 Configuration Manuelle

### Déclenchement Manuel
Tous les workflows peuvent être lancés manuellement via :
- GitHub Actions → Workflow → "Run workflow"

### Variables Secrètes Requises
```bash
ANDROID_KEYSTORE          # Keystore base64
ANDROID_KEYSTORE_PASSWORD # Mot de passe keystore
ANDROID_KEY_PASSWORD      # Mot de passe clé
ANDROID_KEY_ALIAS         # Alias de la clé
```

## 📊 Optimisations Implementées

### 🚀 Performance
- **Builds conditionnelles** : Économie de ~80% des builds inutiles
- **Cache intelligent** : Réutilisation des dépendances
- **Validation précoce** : Détection d'erreurs avant build complète

### 🔒 Sécurité
- **Signature automatique** : AAB signés automatiquement
- **Gestion des secrets** : Keystore sécurisé
- **Isolation des environnements** : Builds isolées

### 📈 Monitoring
- **Artifacts automatiques** : AAB uploadés pour chaque build
- **Logs détaillés** : Debugging facilité
- **Résumés visuels** : Status visible dans GitHub

## 🎮 Utilisation Pratique

### Pour un développement normal :
1. **Code** → **Commit** → **Push**
2. Si fichiers app modifiés → Build automatique
3. Si seulement docs → Aucune build

### Pour une release :
1. **Create Release** sur GitHub
2. Build automatique de production
3. AAB signé disponible en artifact
4. Upload manuel sur Play Store

### Pour des tests :
1. **Pull Request** → Validation automatique
2. **Merge** → Build complète si nécessaire

## 🔍 Monitoring des Builds

### Status des Workflows
- ✅ **Success** : Build réussie, AAB disponible
- ❌ **Failed** : Voir les logs pour diagnostic
- ⏭️ **Skipped** : Aucun fichier pertinent modifié
- 🔄 **Running** : Build en cours

### Artifacts Disponibles
- `test-build-{number}` : Résultats des tests
- `android-aab-{number}` : AAB de développement
- `release-aab-{number}` : AAB signé de production

## 🛠️ Maintenance

### Mise à jour des déclencheurs
Modifier les `paths:` dans les fichiers workflow pour ajuster la sensibilité.

### Ajout de nouveaux tests
Éditer `pre-build-validation.yml` pour ajouter des validations.

### Configuration avancée
Voir `.github/build-triggers.yml` pour la documentation complète.

---

🎯 **Résultat** : Pipeline robuste, économe en ressources, et automatisé pour un déploiement professionnel sur Google Play Store !
