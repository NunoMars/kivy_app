# 🔄 GUIDE DE MISE À JOUR - REBUILD AVEC ADMOB

## ✅ **BONNE NOUVELLE : PAS BESOIN DE REPAYER LES TESTEURS !**

Les **Tests Internes** Play Console sont **GRATUITS** et les testeurs restent actifs après chaque mise à jour.

---

## 📋 **AVANT DE REBUILD**

### ✅ Version mise à jour

**J'ai déjà fait ça pour toi :**

```
buildozer.spec:
  version = 1.7  →  version = 1.8  ✅
```

**Important :** Chaque nouveau build doit avoir un numéro de version **supérieur** à l'ancien.

---

## 🚀 **WORKFLOW DE REBUILD**

### Étape 1 : Clean (optionnel mais recommandé)

```powershell
buildozer android clean
```

**Pourquoi ?** Supprime les anciens fichiers de build pour éviter les conflits.

### Étape 2 : Build le nouvel APK/AAB

```powershell
buildozer android release
```

**Ce qui sera inclus :**
- ✅ Système AdMob complet (`ads_manager.py`)
- ✅ Config par défaut mode TEST (`config.default.json`)
- ✅ Bannière intégrée (écran réponse)
- ✅ Interstitielle intégrée (tous les 5 tirages)
- ✅ Tes IDs AdMob (dans `resources/values/strings.xml`)

**Temps de build :** 10-30 minutes

### Étape 3 : Upload sur Play Console

1. Va sur https://play.google.com/console/
2. Sélectionne **"Ma Carte de Tarot"**
3. **Tests Internes** → **Nouvelle version**
4. Upload `bin/macartedetarot-1.8-arm64-v8a_armeabi-v7a-release.aab`
5. **Publier**

**Résultat :** Les testeurs actuels reçoivent automatiquement la mise à jour !

### Étape 4 : Tester

**Option A : Toi-même (si tu es testeur)**

1. Ouvre Play Store sur ton téléphone
2. Va dans **"Mes jeux et apps"**
3. Mise à jour disponible pour "Ma Carte de Tarot"
4. Clique **Mettre à jour**

**Option B : Autre testeur**

Tes testeurs actuels voient automatiquement la mise à jour dans Play Store.

### Étape 5 : Vérifier les pubs

**Mode TEST (par défaut) :**

```powershell
adb logcat -s "AdMob:*"
```

**Devrait afficher :**
```
AdMob: Using TEST IDs
AdMob: Showing banner (TEST mode)
AdMob: Showing interstitial ad (count: 5)
```

**Pubs visibles :**
- Bannière "Test Ad" sur écran réponse
- Popup "Test Ad" tous les 3 tirages (config.default.json)

---

## 🔄 **SWITCHER EN MODE PRODUCTION (TES PUBS)**

Une fois que tu as vérifié que les pubs de test fonctionnent :

```powershell
.\deploy_config.ps1 prod
```

**Ce qui se passe :**
1. Crée `config.json` avec tes IDs AdMob
2. Pousse sur Android via ADB
3. Redémarre l'app

**Pubs visibles :**
- Ta bannière sur écran réponse
- Ta popup plein écran tous les 5 tirages

**Délai :** Max 1 heure pour que Google active tes nouveaux blocs

---

## 💡 **DIFFÉRENCE MODE TEST vs PRODUCTION**

### Mode TEST (par défaut dans l'APK)

```json
// config.default.json (embarqué dans l'APK)
{
  "ads_test_mode": true,
  "admob_banner_id": "ca-app-pub-3940256099942544/6300978111",  // Google test
  "ads_frequency": 3
}
```

**Avantages :**
- ✅ Pubs apparaissent immédiatement
- ✅ Pas de délai d'activation
- ✅ Idéal pour tester l'intégration

**Inconvénients :**
- ❌ Pas de vrais revenus
- ❌ Label "Test Ad" visible

### Mode PRODUCTION (via deploy_config.ps1)

```json
// config.json (poussé via ADB)
{
  "ads_test_mode": false,
  "admob_banner_id": "ca-app-pub-5749803259882370/8646786637",  // TON ID
  "admob_inter_id": "ca-app-pub-5749803259882370/4840878344",   // TON ID
  "ads_frequency": 5
}
```

**Avantages :**
- ✅ Vraies pubs → Vrais revenus
- ✅ Modifiable sans rebuild
- ✅ Dashboard AdMob actif

**Inconvénients :**
- ⏰ Délai 1h pour activation Google

---

## 📊 **TESTEURS ACTUELS - CE QUI SE PASSE**

### Avant rebuild (version 1.7)

```
Testeur A : Version 1.7 installée (sans AdMob)
Testeur B : Version 1.7 installée (sans AdMob)
```

### Après upload version 1.8

```
Play Console → Tests Internes → Nouvelle version 1.8 publiée
```

**Automatiquement :**

```
Testeur A : Play Store affiche "Mise à jour disponible"
Testeur B : Play Store affiche "Mise à jour disponible"
```

**Après mise à jour :**

```
Testeur A : Version 1.8 avec AdMob (mode TEST par défaut)
Testeur B : Version 1.8 avec AdMob (mode TEST par défaut)
```

**Pas besoin de :**
- ❌ Réinviter les testeurs
- ❌ Créer un nouveau lien de test
- ❌ Payer quoi que ce soit

**Les testeurs voient automatiquement la mise à jour !** 🎉

---

## ⚙️ **CONFIGURATION RECOMMANDÉE POUR TESTS INTERNES**

### buildozer.spec (déjà configuré)

```
version = 1.8  ✅
```

### config.default.json (embarqué dans l'APK)

**Garde le mode TEST pour les testeurs :**

```json
{
  "ads_test_mode": true,     ← Pubs Google de test
  "ads_frequency": 3,        ← Popup tous les 3 tirages (plus fréquent pour tester)
  "banner_enabled": true,
  "interstitial_enabled": true
}
```

**Pourquoi ?**
- Les testeurs voient des pubs immédiatement (pas de délai 1h)
- Tu peux vérifier que l'intégration fonctionne
- Pas besoin de pousser config via ADB sur chaque appareil de test

### Pour TOI uniquement (mode PRODUCTION)

```powershell
.\deploy_config.ps1 prod
```

**Résultat :**
- Toi : Pubs de production (tes IDs)
- Testeurs : Pubs de test (IDs Google)

---

## 🔢 **GESTION DES VERSIONS**

### Quand incrémenter la version ?

**À chaque nouveau build uploadé sur Play Console !**

```
Version actuelle : 1.8
Prochain build : 1.9
Build suivant : 2.0
```

**Play Console refuse les versions identiques.**

### Comment incrémenter ?

**Modification manuelle :**

```plaintext
# buildozer.spec
version = 1.8  →  version = 1.9
```

**Ou automatique (futur) :**

Tu pourrais créer un script PowerShell pour incrémenter automatiquement.

---

## ✅ **CHECKLIST REBUILD**

Avant de lancer `buildozer android release` :

- [✅] Version incrémentée dans buildozer.spec (1.7 → 1.8)
- [✅] ads_manager.py présent
- [✅] config.default.json présent (mode TEST)
- [✅] config.production.json présent (tes IDs)
- [✅] resources/values/strings.xml présent (App ID)
- [✅] main.py modifié (AdMob intégré)
- [✅] buildozer.spec modifié (kivmob, permissions, gradle)

**Tout est déjà fait ! Tu peux lancer le build.** ✅

---

## 🚀 **COMMANDES FINALES**

```powershell
# 1. Clean (optionnel)
buildozer android clean

# 2. Build
buildozer android release

# 3. Upload sur Play Console (manuel via navigateur)
# https://play.google.com/console/ → Tests Internes → Nouvelle version

# 4. Tester mode TEST (après installation depuis Play Store)
adb logcat -s "AdMob:*"

# 5. Switcher en mode PRODUCTION (sur ton appareil uniquement)
.\deploy_config.ps1 prod
```

---

## 💰 **RÉSUMÉ COÛTS**

| Action | Coût |
|--------|------|
| Tests Internes Play Console | **GRATUIT** ✅ |
| Nouveau build/upload | **GRATUIT** ✅ |
| Testeurs (jusqu'à 100) | **GRATUIT** ✅ |
| Mises à jour | **GRATUIT** ✅ |
| Publication Production | **25€ une fois** (déjà payé) ✅ |

**Conclusion : Tu peux rebuild et uploader autant que tu veux, c'est GRATUIT !** 🎉

---

## 📚 **PROCHAINES ÉTAPES**

1. **Lance le build :**
   ```powershell
   buildozer android release
   ```

2. **Upload sur Play Console Tests Internes**

3. **Teste avec pubs Google de test**

4. **Une fois validé, active tes pubs :**
   ```powershell
   .\deploy_config.ps1 prod
   ```

5. **Attends 1h (délai Google)**

6. **Vérifie dashboard AdMob :**
   https://apps.admob.com/

---

**🎉 Prêt pour le rebuild ! Tout est gratuit, tes testeurs restent actifs.** 🚀
