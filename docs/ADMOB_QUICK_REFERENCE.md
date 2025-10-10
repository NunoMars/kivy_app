# 🎯 ADMOB - Guide de Référence Rapide

## 📋 Fichiers du Système AdMob

```
kivy_app/
├── ads_manager.py              ← Gestionnaire AdMob (250+ lignes)
├── config.default.json         ← Config embarquée (mode TEST par défaut)
├── deploy_config.ps1           ← Script PowerShell de déploiement
├── buildozer.spec              ← Modifié (kivmob, permissions, gradle)
├── main.py                     ← Modifié (imports + init + on_card_drawn)
├── resources/
│   └── values/
│       └── strings.xml         ← AdMob App ID Android
└── docs/
    ├── ADMOB_INTEGRATION.md    ← Documentation complète (400+ lignes)
    ├── ADMOB_WORKFLOW.md       ← Workflow test/prod (ce fichier)
    └── ADMOB_INTEGRATION_EXAMPLE.py  ← Exemples de code
```

---

## ⚡ Commandes Rapides

### Déployer Config en Mode TEST

```powershell
.\deploy_config.ps1 test
```

### Déployer Config en Mode PRODUCTION

```powershell
.\deploy_config.ps1 prod
```

### Vérifier Config Actuelle

```powershell
adb shell run-as org.tarot.macartedetarot cat files/config.json
```

### Suivre Logs AdMob

```powershell
adb logcat -s "AdMob:* TarotApp:* Python:*"
```

### Redémarrer App

```powershell
adb shell am force-stop org.tarot.macartedetarot
adb shell am start -n org.tarot.macartedetarot/.MainActivity
```

### Réinitialiser Config (revenir au défaut)

```powershell
adb shell run-as org.tarot.macartedetarot rm files/config.json
```

---

## 🔧 Configuration JSON

### Structure du Fichier

```json
{
  "ads_enabled": true,              // ← Activer/désactiver les pubs
  "ads_test_mode": false,           // ← true = IDs test, false = IDs prod
  "admob_app_id": "ca-app-pub-...", // ← App ID AdMob
  "admob_banner_id": "ca-app-pub-...", // ← Banner Ad Unit ID
  "admob_interstitial_id": "ca-app-pub-...", // ← Interstitial Ad Unit ID
  "ads_frequency": 5,               // ← Afficher pub tous les X tirages
  "banner_position": "bottom",      // ← Position bannière (top/bottom)
  "remote_config_url": ""           // ← URL config à distance (optionnel)
}
```

### IDs de Test Google (par défaut)

```json
{
  "admob_app_id": "ca-app-pub-3940256099942544~3347511713",
  "admob_banner_id": "ca-app-pub-3940256099942544/9214589741",
  "admob_interstitial_id": "ca-app-pub-3940256099942544/1033173712"
}
```

**Note :** Ces IDs affichent des pubs de test Google avec label "Test Ad".

### Obtenir tes IDs de Production

1. Va sur https://apps.admob.com/
2. Sélectionne ton app "Ma Carte de Tarot"
3. **Ad Units** :
   - Clique sur **"Interstitial"** → Copie l'ID
   - Clique sur **"Banner"** → Copie l'ID
4. **App Settings** :
   - Copie **"App ID"**

---

## 📊 Priorité de Configuration

```
1. config.json (user data dir)
   ↓ (si absent)
2. config.default.json (embarqué APK)
   ↓ (si absent)
3. Valeurs codées en dur (ads_manager.py)
```

**Avantage :** Tu peux modifier `config.json` **sans rebuild** de l'APK.

---

## 🎯 Comportement des Pubs

### Fréquence Recommandée

| Fréquence | Comportement | UX | Revenus |
|-----------|--------------|-----|---------|
| 1-2 | Pub à chaque tirage | ⚠️ Très intrusif | 💰💰💰💰 |
| 3-4 | Pub tous les 3-4 tirages | ⚠️ Moyennement intrusif | 💰💰💰 |
| **5-7** | **Pub tous les 5-7 tirages** | ✅ **Optimal** | 💰💰 |
| 10+ | Pub rarement | ✅ Peu intrusif | 💰 |

**Recommandation :** Commence avec `"ads_frequency": 5`

### Types de Pubs

| Type | Description | Quand afficher | Revenus |
|------|-------------|----------------|---------|
| **Interstitial** | Plein écran | Entre 2 tirages | 💰💰💰 |
| **Banner** | Petite bannière | En permanence | 💰 |

**Implémentation actuelle :** Interstitiel uniquement (plus de revenus, moins intrusif qu'une bannière permanente).

---

## 🚀 Workflow Développement

### Phase 1 : Développement Local

```bash
# Build avec IDs de test
buildozer android debug
adb install -r bin/macartedetarot-0.01-arm64-v8a_armeabi-v7a-debug.apk

# Vérifier logs
adb logcat -s "AdMob:* TarotApp:*"
```

**Log attendu :**
```
AdMob: Using TEST IDs
AdMob: Showing interstitial ad (count: 3)
```

### Phase 2 : Tests Internes (Play Console)

```bash
# Build release avec IDs de test
buildozer android release

# Upload sur Play Console → Tests Internes
```

**Important :** Garde `ads_test_mode: true` dans `config.default.json` !

### Phase 3 : Switch Production (via ADB)

```bash
# Créer config.json avec vrais IDs
.\deploy_config.ps1 prod

# Tester
adb logcat -s "AdMob:*"
```

**Log attendu :**
```
AdMob: Using PRODUCTION IDs
AdMob: Showing interstitial ad (count: 5)
```

### Phase 4 : Déploiement Production

```bash
# Upload sur Play Console → Production
```

**Note :** Les utilisateurs auront `config.default.json` (mode test) par défaut. Tu peux :
1. Pousser `config.json` via remote URL
2. Ou modifier `config.default.json` et rebuild (moins flexible)

---

## 🐛 Debugging

### Problème : Aucune pub ne s'affiche

**Checklist :**

```bash
# 1. Vérifier que les pubs sont activées
adb shell run-as org.tarot.macartedetarot cat files/config.json | findstr "ads_enabled"
# → Devrait afficher: "ads_enabled": true

# 2. Vérifier le mode
adb logcat -s "AdMob:*" | findstr "Using"
# → Devrait afficher: "Using TEST IDs" ou "Using PRODUCTION IDs"

# 3. Vérifier la fréquence
adb shell run-as org.tarot.macartedetarot cat files/config.json | findstr "ads_frequency"
# → Ex: "ads_frequency": 3

# 4. Vérifier les permissions
adb shell dumpsys package org.tarot.macartedetarot | findstr "INTERNET"
# → Devrait afficher: android.permission.INTERNET: granted=true
```

### Problème : Pub de test en mode PROD

**Cause :** `config.json` n'a pas été poussé correctement.

**Solution :**

```bash
# Re-déployer
.\deploy_config.ps1 prod

# Vérifier
adb shell run-as org.tarot.macartedetarot cat files/config.json
# → Devrait afficher "ads_test_mode": false
```

### Problème : App crash au démarrage

**Cause possible :** `ads_manager.py` ou `config.default.json` manquant.

**Solution :**

```bash
# Vérifier les fichiers
ls ads_manager.py
ls config.default.json

# Rebuild
buildozer android clean
buildozer android release
```

---

## 📈 Monitoring Revenus

### Dashboard AdMob

1. Va sur https://apps.admob.com/
2. **Sélectionne ton app**
3. **Metrics** :
   - **Impressions** : Nombre de pubs affichées
   - **Clicks** : Nombre de clics
   - **eCPM** : Revenu par 1000 impressions (€)
   - **Estimated Earnings** : Revenus estimés (€)

**Délai :** Les données apparaissent sous **24-48h**.

### Revenus Typiques (France)

| eCPM | Fréquence | 1000 tirages | 10000 tirages |
|------|-----------|--------------|---------------|
| €2 | 5 tirages | €0.40 | €4.00 |
| €3 | 5 tirages | €0.60 | €6.00 |
| €5 | 5 tirages | €1.00 | €10.00 |

**Formule :** Revenus = (Tirages ÷ Fréquence) × (eCPM ÷ 1000)

**Exemple :**
- 10,000 tirages
- Fréquence = 5 (pub tous les 5 tirages)
- eCPM = €3
- **Revenus = (10,000 ÷ 5) × (€3 ÷ 1000) = €6**

---

## 🔐 Sécurité

### IDs AdMob

⚠️ **NE JAMAIS** commit tes vrais IDs AdMob sur GitHub public !

**Bonne pratique :**

```bash
# .gitignore
config.json           # ← IDs de production
deploy_config.ps1     # ← Peut contenir des IDs
```

**Garder sur GitHub :**

```bash
config.default.json   # ← IDs de test Google uniquement
ads_manager.py        # ← Code générique
```

### Protection des Revenus

**AdMob peut bannir ton compte si :**
- Tu cliques sur tes propres pubs
- Tu incites les utilisateurs à cliquer
- Tu caches la pub (transparent, hors écran)

**Bonnes pratiques :**
- Utilise TOUJOURS le mode test pendant le développement
- Ne clique JAMAIS sur tes pubs de production
- Respecte la politique AdMob : https://support.google.com/admob/answer/6128543

---

## 📚 Ressources

### Documentation

- **AdMob Setup :** `docs/ADMOB_INTEGRATION.md`
- **Workflow :** `docs/ADMOB_WORKFLOW.md` (ce fichier)
- **Exemples :** `docs/ADMOB_INTEGRATION_EXAMPLE.py`

### Liens Externes

- **AdMob Dashboard :** https://apps.admob.com/
- **Play Console :** https://play.google.com/console/
- **Politique AdMob :** https://support.google.com/admob/answer/6128543
- **kivmob GitHub :** https://github.com/MichaelStott/KivMob

---

## ✅ Checklist de Déploiement

### Avant le Premier Build

- [ ] `ads_manager.py` créé
- [ ] `config.default.json` créé (mode TEST)
- [ ] `buildozer.spec` modifié (kivmob, permissions, gradle)
- [ ] `resources/values/strings.xml` créé
- [ ] `main.py` modifié (imports + init + on_card_drawn)

### Avant Tests Internes

- [ ] Build avec `ads_test_mode: true`
- [ ] Upload sur Play Console
- [ ] Test sur appareil réel
- [ ] Pubs de test s'affichent correctement
- [ ] Fréquence testée (ex: tous les 3 tirages)

### Avant Production

- [ ] Créer compte AdMob (https://admob.google.com/)
- [ ] Créer app "Ma Carte de Tarot"
- [ ] Créer 2 ad units : Interstitial + Banner
- [ ] Copier les IDs dans `config.json`
- [ ] Tester avec `.\deploy_config.ps1 prod`
- [ ] Vérifier dashboard AdMob (impressions comptées)

### Après Production

- [ ] Surveiller dashboard AdMob (24-48h pour les premières données)
- [ ] Ajuster `ads_frequency` si besoin (trop/pas assez de pubs)
- [ ] Vérifier taux de clics (CTR)
- [ ] Optimiser eCPM

---

## 🎓 FAQ

### Q: Puis-je changer la fréquence des pubs sans rebuild ?

**R:** Oui ! Modifie `config.json` et pousse-le via ADB :

```bash
# Modifier config.json localement
# "ads_frequency": 10

# Déployer
.\deploy_config.ps1
```

### Q: Puis-je désactiver les pubs temporairement ?

**R:** Oui ! Modifie `config.json` :

```json
{
  "ads_enabled": false
}
```

Puis pousse via ADB.

### Q: Comment tester sans appareil Android ?

**R:** Impossible. AdMob ne fonctionne que sur Android/iOS. Sur desktop, les pubs sont automatiquement désactivées.

### Q: Les pubs fonctionnent sur iOS ?

**R:** Non, pas avec `kivmob`. Il faut utiliser `pyobjus` (plus complexe). Pour l'instant, focus sur Android.

### Q: Combien je peux gagner ?

**R:** Ça dépend de :
- Nombre d'utilisateurs actifs
- Nombre de tirages par utilisateur
- Fréquence des pubs
- eCPM (varie selon pays, heure, saisonnalité)

**Estimation France :**
- 1000 utilisateurs/mois
- 10 tirages/utilisateur
- Fréquence = 5 (pub tous les 5 tirages)
- eCPM = €3

**Calcul :**
- Tirages totaux = 1000 × 10 = 10,000
- Impressions = 10,000 ÷ 5 = 2,000
- Revenus = 2,000 × (€3 ÷ 1000) = **€6/mois**

Pour gagner €100/mois, il te faut environ **17,000 utilisateurs actifs**.

### Q: Puis-je combiner bannière + interstitiel ?

**R:** Oui ! Modifie `main.py` :

```python
class ResponseScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        if hasattr(app, 'ads'):
            app.ads.show_banner()  # Afficher bannière
    
    def on_leave(self):
        app = App.get_running_app()
        if hasattr(app, 'ads'):
            app.ads.hide_banner()  # Masquer bannière
```

---

## 🚀 Prochaines Étapes

1. **Build l'APK :**
   ```bash
   buildozer android release
   ```

2. **Tester avec IDs de test :**
   ```bash
   adb install -r bin/macartedetarot-0.01-arm64-v8a_armeabi-v7a-release.aab
   ```

3. **Switcher en mode PROD :**
   ```bash
   .\deploy_config.ps1 prod
   ```

4. **Uploader sur Play Console** et **surveiller les revenus !**

---

**🎉 Bonne monétisation ! 💰**
