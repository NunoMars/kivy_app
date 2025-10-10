# 🚀 Guide d'Intégration AdMob - Configuration JSON

## 📋 Vue d'ensemble

Ce système te permet de **changer les IDs AdMob sans recompiler** l'application, via un simple fichier JSON.

### ✅ Avantages
- 🔧 **Pas de rebuild** pour changer les IDs de pub
- 🧪 **Mode test facile** : switch instantané test ↔ prod
- 🌐 **Config à distance** : mise à jour via HTTP (optionnel)
- 📱 **Config locale** : modification via ADB ou interface
- 🎯 **Flexible** : change fréquence, position, activation des pubs

---

## 📁 Fichiers Créés

### 1. `config.default.json` (Racine du projet)
Configuration par défaut embarquée dans l'APK/AAB
```json
{
  "ads_enabled": true,
  "ads_test_mode": true,
  "remote_config_url": "",
  "admob_app_id": "ca-app-pub-3940256099942544~3347511713",
  "admob_banner_id": "ca-app-pub-3940256099942544/6300978111",
  "admob_inter_id": "ca-app-pub-3940256099942544/1033173712",
  "ads_frequency": 3,
  "banner_position": "bottom",
  "banner_enabled": true,
  "interstitial_enabled": true
}
```

### 2. `resources/values/strings.xml`
String resources Android pour AdMob
```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="admob_app_id">ca-app-pub-3940256099942544~3347511713</string>
</resources>
```

### 3. `ads_manager.py`
Module Python pour gérer AdMob avec configuration JSON

---

## 🔧 Modifications `buildozer.spec`

Les modifications suivantes ont été appliquées :

```ini
# Dependencies
requirements = python3,kivy==2.3.0,pillow==10.0.0,kivmob,requests

# Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,com.google.android.gms.permission.AD_ID

# AdMob metadata
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=@string/admob_app_id

# Android resources
android.add_resources = resources/

# Gradle dependencies
android.gradle_dependencies = com.android.tools.build:gradle:8.1.1,com.google.android.gms:play-services-ads:22.6.0
```

---

## 🎯 Intégration dans `main.py`

### Étape 1 : Importer le module

Ajoute en haut de `main.py` :

```python
from ads_manager import load_config, AdsManager, maybe_fetch_remote_config
```

### Étape 2 : Initialiser dans la classe App

Dans `class TarotApp(App):` :

```python
def build(self):
    # Charger la configuration
    self.cfg = load_config()
    
    # Optionnel : récupérer config à distance
    maybe_fetch_remote_config(self.cfg)
    
    # Initialiser AdMob
    self.ads = AdsManager(self.cfg)
    
    # ... reste du code ...
    return root_widget
```

### Étape 3 : Appeler lors du tirage de carte

Trouve la méthode où tu tires une carte et ajoute :

```python
def draw_card(self):
    # ... ton code de tirage ...
    
    # Notifier AdMob (affichera interstitiel selon fréquence)
    if hasattr(self, 'ads'):
        self.ads.on_card_drawn()
```

**OU** si tu veux plus de contrôle :

```python
def draw_card(self):
    # ... ton code de tirage ...
    
    # Afficher interstitiel manuellement
    if hasattr(self, 'ads'):
        self.ads.show_interstitial()
```

---

## 🧪 Phase de Test

### Build v1.7 avec mode TEST

1. **Vérifier config.default.json** :
   ```json
   "ads_test_mode": true
   ```

2. **Build release** :
   ```bash
   buildozer android release
   ```

3. **Tester sur appareil** :
   - Les pubs affichées seront des pubs de test Google
   - ID App: `ca-app-pub-3940256099942544~3347511713`
   - Banner: `ca-app-pub-3940256099942544/6300978111`
   - Interstitial: `ca-app-pub-3940256099942544/1033173712`

4. **Vérifier les logs** :
   ```bash
   adb logcat | grep AdMob
   ```
   
   Tu devrais voir :
   ```
   AdMob: Using TEST IDs
   AdMob: Initialized ✅
   AdMob: Banner initialized
   AdMob: Interstitial initialized
   ```

---

## 🚀 Passage en Production

### Option A : Modifier config local (via ADB)

1. **Créer `config.json` de prod** :
   ```json
   {
     "ads_enabled": true,
     "ads_test_mode": false,
     "admob_app_id": "ca-app-pub-XXXXXXXXXXXXXXXX~XXXXXXXXXX",
     "admob_banner_id": "ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX",
     "admob_inter_id": "ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX",
     "ads_frequency": 5
   }
   ```

2. **Pousser via ADB** :
   ```bash
   # Trouver le dossier app
   adb shell run-as org.tarot.macartedetarot
   
   # Copier le fichier
   adb push config.json /data/data/org.tarot.macartedetarot/files/config.json
   ```

3. **Redémarrer l'app** → Les nouveaux IDs sont actifs ! 🎉

### Option B : Config à distance (Avancé)

1. **Héberger `config.json`** :
   - GitHub Pages
   - AWS S3
   - Google Cloud Storage
   - Ton propre serveur

   Exemple URL : `https://ton-domaine.com/tarot/config.json`

2. **Modifier config.default.json** :
   ```json
   {
     "remote_config_url": "https://ton-domaine.com/tarot/config.json",
     ...
   }
   ```

3. **Rebuild une fois**, puis :
   - Change `config.json` distant
   - L'app téléchargera automatiquement au démarrage
   - Redémarrage → nouvelle config active

---

## 📊 Structure de Priorité

```
1. /data/data/org.tarot.macartedetarot/files/config.json  ← PRIORITÉ MAX (modifiable)
2. config.default.json (embarqué dans l'APK)              ← Fallback
3. Valeurs codées en dur                                  ← Ultime fallback
```

---

## 🎛️ Options de Configuration Disponibles

| Clé | Type | Description | Défaut |
|-----|------|-------------|--------|
| `ads_enabled` | boolean | Active/désactive toutes les pubs | `true` |
| `ads_test_mode` | boolean | Mode test (IDs Google) vs prod | `true` |
| `admob_app_id` | string | ID Application AdMob | Test ID |
| `admob_banner_id` | string | ID Bannière | Test ID |
| `admob_inter_id` | string | ID Interstitiel | Test ID |
| `ads_frequency` | integer | Fréquence interstitiel (tous les X tirages) | `3` |
| `banner_position` | string | Position bannière (`"top"` ou `"bottom"`) | `"bottom"` |
| `banner_enabled` | boolean | Active/désactive bannière | `true` |
| `interstitial_enabled` | boolean | Active/désactive interstitiel | `true` |
| `remote_config_url` | string | URL config à distance (optionnel) | `""` |

---

## 🧪 Scénarios de Test

### Test 1 : Mode Test par défaut
```bash
# Build
buildozer android release

# Installer
adb install -r bin/*.aab

# Vérifier logs
adb logcat | grep AdMob
# Doit voir : "Using TEST IDs"
```

### Test 2 : Switch vers Production (sans rebuild)
```bash
# Créer config.json local
echo '{
  "ads_test_mode": false,
  "admob_app_id": "ca-app-pub-REAL~REAL"
}' > /tmp/config.json

# Pousser
adb push /tmp/config.json /sdcard/config.json
adb shell run-as org.tarot.macartedetarot cp /sdcard/config.json files/config.json

# Redémarrer app
adb shell am force-stop org.tarot.macartedetarot
adb shell am start -n org.tarot.macartedetarot/.MainActivity

# Vérifier logs
adb logcat | grep AdMob
# Doit voir : "Using PRODUCTION IDs"
```

### Test 3 : Désactiver toutes les pubs
```bash
echo '{"ads_enabled": false}' > /tmp/config.json
adb push /tmp/config.json /sdcard/config.json
adb shell run-as org.tarot.macartedetarot cp /sdcard/config.json files/config.json
# Redémarrer → plus aucune pub
```

---

## 🔍 Debugging

### Vérifier config chargée
Ajoute dans `main.py` après `load_config()` :
```python
self.cfg = load_config()
print(f"📋 Config loaded: {json.dumps(self.cfg, indent=2)}")
```

### Vérifier emplacement fichier
```python
from kivy.app import App
app = App.get_running_app()
print(f"📂 Config path: {os.path.join(app.user_data_dir, 'config.json')}")
```

### Logs AdMob complets
```bash
adb logcat -s python:D AdMob:V GoogleAds:V
```

---

## ⚠️ Points d'Attention

### 1. **Permissions Android**
Les permissions sont maintenant dans `buildozer.spec` :
- `INTERNET` - Requis pour AdMob
- `ACCESS_NETWORK_STATE` - Requis pour AdMob
- `com.google.android.gms.permission.AD_ID` - Play Store compliance

### 2. **Test IDs vs Production**
⚠️ **IMPORTANT** : Ne jamais publier sur Play Store avec `ads_test_mode: true` !

Les IDs de test sont uniquement pour développement.

### 3. **resources/values/strings.xml**
Le fichier DOIT exister pour AdMob, même si tu changes les IDs via JSON.
Garde l'ID de test dedans, la vraie config viendra du JSON.

### 4. **Fréquence des interstitiels**
Google recommande de ne pas trop spammer :
- ❌ Toutes les 1-2 lectures (trop agressif)
- ✅ Toutes les 3-5 lectures (acceptable)
- 👍 Toutes les 5-7 lectures (optimal UX)

---

## 🎯 Checklist de Déploiement

### Phase 1 : Build Test
- [x] `config.default.json` créé avec IDs de test
- [x] `resources/values/strings.xml` créé
- [x] `buildozer.spec` modifié
- [x] `ads_manager.py` créé
- [ ] Intégration dans `main.py`
- [ ] Build : `buildozer android release`
- [ ] Test sur appareil physique
- [ ] Vérifier pubs de test s'affichent
- [ ] Vérifier logs AdMob

### Phase 2 : Tests Internes Play Store
- [ ] Upload AAB sur Play Console (Tests Internes)
- [ ] Smoke test : pubs de test OK
- [ ] Test changement config via ADB
- [ ] Vérifier compteur fréquence fonctionne

### Phase 3 : Production
- [ ] Obtenir vrais IDs AdMob depuis console
- [ ] Mettre à jour `strings.xml` avec vrai App ID
- [ ] Créer `config.json` de prod
- [ ] Tester en local avec config prod
- [ ] Upload sur Tests Fermés
- [ ] Vérifier revenus dans AdMob dashboard

---

## 📱 Commandes Utiles

### Lister configs disponibles
```bash
# Config par défaut (dans APK)
unzip -p bin/*.apk config.default.json

# Config utilisateur
adb shell run-as org.tarot.macartedetarot cat files/config.json
```

### Reset config utilisateur
```bash
adb shell run-as org.tarot.macartedetarot rm files/config.json
# Redémarrer → retour à config.default.json
```

### Pousser nouvelle config
```bash
adb push config.json /sdcard/
adb shell run-as org.tarot.macartedetarot cp /sdcard/config.json files/
```

---

## 🎉 Résumé

Tu as maintenant un système **complètement découplé** :

✅ **Build une fois** avec mode test
✅ **Test** sur plusieurs appareils
✅ **Publie** en Tests Internes
✅ **Active prod** en changeant juste le JSON
✅ **Ajuste fréquence** sans rebuild
✅ **Désactive** temporairement si besoin
✅ **Config à distance** (optionnel)

**Prochaine étape :** Intégrer dans `main.py` ! 🚀
