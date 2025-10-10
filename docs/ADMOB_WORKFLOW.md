# 🚀 Workflow AdMob - Configuration JSON

## ✅ Intégration Terminée

L'intégration AdMob avec système de configuration JSON est **complète** :

- ✅ `ads_manager.py` créé (250+ lignes)
- ✅ `config.default.json` embarqué avec IDs de test
- ✅ `buildozer.spec` modifié (kivmob, permissions, gradle)
- ✅ `resources/values/strings.xml` créé (AdMob App ID)
- ✅ `main.py` intégré (imports + initialisation + on_card_drawn)
- ✅ Documentation complète (`ADMOB_INTEGRATION.md`)

---

## 📋 Étape 1 : Test en Mode TEST (IDs Google de test)

### 1.1 Vérifier la configuration par défaut

```bash
cat config.default.json
```

**Devrait afficher :**
```json
{
  "ads_enabled": true,
  "ads_test_mode": true,  // ← MODE TEST
  "admob_app_id": "ca-app-pub-3940256099942544~3347511713",
  "admob_banner_id": "ca-app-pub-3940256099942544/9214589741",
  "admob_interstitial_id": "ca-app-pub-3940256099942544/1033173712",
  "ads_frequency": 3,
  "banner_position": "bottom",
  "remote_config_url": ""
}
```

### 1.2 Build en mode TEST

```bash
buildozer android release
```

**Log attendu au démarrage :**
```
=== CONSTRUCTION APP TAROT ===
📱 Chargement configuration AdMob...
   → Mode test: True
   → Pubs activées: True
   → Fréquence: 3 tirages
🔧 AdMob: Using TEST IDs
   App: ca-app-pub-3940256099942544~3347511713
   Banner: ca-app-pub-3940256099942544/9214589741
   Interstitial: ca-app-pub-3940256099942544/1033173712
✅ AdMob initialisé
```

### 1.3 Test sur appareil réel

```bash
# Installer l'APK
adb install -r bin/macartedetarot-0.01-arm64-v8a_armeabi-v7a-release.aab

# Suivre les logs
adb logcat | findstr /I "AdMob TarotApp"
```

**Comportement attendu :**
- Tirage 1 : Pas de pub
- Tirage 2 : Pas de pub
- Tirage 3 : **PUB INTERSTITIELLE DE TEST** (label "Test Ad")
- Tirage 4-5 : Pas de pub
- Tirage 6 : **PUB INTERSTITIELLE DE TEST**

**Si tu vois la pub de test :** ✅ L'intégration fonctionne !

---

## 🔄 Étape 2 : Switcher en Mode PRODUCTION (sans rebuild)

### 2.1 Créer config.json avec tes VRAIS IDs AdMob

Sur ton PC, crée `config.json` :

```json
{
  "ads_enabled": true,
  "ads_test_mode": false,
  "admob_app_id": "ca-app-pub-XXXXXXXXXXXXXXXX~YYYYYYYYYY",
  "admob_banner_id": "ca-app-pub-XXXXXXXXXXXXXXXX/ZZZZZZZZZZ",
  "admob_interstitial_id": "ca-app-pub-XXXXXXXXXXXXXXXX/AAAAAAAAAA",
  "ads_frequency": 5,
  "banner_position": "bottom",
  "remote_config_url": ""
}
```

**Où trouver tes IDs :**
1. Va sur https://apps.admob.com/
2. Sélectionne ton app "Ma Carte de Tarot"
3. **Ad Units** → Copie les IDs :
   - Interstitial : `ca-app-pub-XXXXXXXXXXXXXXXX/AAAAAAAAAA`
   - Banner : `ca-app-pub-XXXXXXXXXXXXXXXX/ZZZZZZZZZZ`
4. **App Settings** → App ID : `ca-app-pub-XXXXXXXXXXXXXXXX~YYYYYYYYYY`

### 2.2 Pousser le fichier sur Android (via ADB)

```bash
adb push config.json /sdcard/config.json
adb shell run-as org.tarot.macartedetarot cp /sdcard/config.json /data/data/org.tarot.macartedetarot/files/config.json
adb shell rm /sdcard/config.json
```

### 2.3 Redémarrer l'app

```bash
adb shell am force-stop org.tarot.macartedetarot
adb shell am start -n org.tarot.macartedetarot/.MainActivity
```

**Log attendu :**
```
📱 Chargement configuration AdMob...
   → Mode test: False  // ← CHANGÉ !
   → Pubs activées: True
   → Fréquence: 5      // ← CHANGÉ !
🎯 AdMob: Using PRODUCTION IDs
   App: ca-app-pub-XXXXXXXXXXXXXXXX~YYYYYYYYYY
   Interstitial: ca-app-pub-XXXXXXXXXXXXXXXX/AAAAAAAAAA
✅ AdMob initialisé
```

**Nouveau comportement :**
- Tirage 1-4 : Pas de pub
- Tirage 5 : **PUB RÉELLE** (sans label "Test Ad")
- Tirage 10 : **PUB RÉELLE**

**🎉 Tu viens de changer la config SANS REBUILD !**

---

## 🌐 Étape 3 (Avancé) : Configuration à Distance

### 3.1 Héberger config.json sur un serveur

Upload `config.json` sur un serveur HTTP (ex: GitHub raw, Firebase Hosting, ton serveur perso).

Exemple URL : `https://raw.githubusercontent.com/TON_USER/TON_REPO/main/config.json`

### 3.2 Activer le fetch à distance

Modifie `config.json` :

```json
{
  "ads_enabled": true,
  "ads_test_mode": false,
  "admob_app_id": "ca-app-pub-XXXXXXXXXXXXXXXX~YYYYYYYYYY",
  "admob_banner_id": "ca-app-pub-XXXXXXXXXXXXXXXX/ZZZZZZZZZZ",
  "admob_interstitial_id": "ca-app-pub-XXXXXXXXXXXXXXXX/AAAAAAAAAA",
  "ads_frequency": 5,
  "banner_position": "bottom",
  "remote_config_url": "https://raw.githubusercontent.com/TON_USER/TON_REPO/main/config.json"
}
```

### 3.3 Pousser sur Android

```bash
adb push config.json /sdcard/config.json
adb shell run-as org.tarot.macartedetarot cp /sdcard/config.json /data/data/org.tarot.macartedetarot/files/config.json
adb shell rm /sdcard/config.json
```

### 3.4 Redémarrer l'app

**Log attendu :**
```
🌐 Tentative de téléchargement config à distance...
✅ Config à distance récupérée et sauvegardée
   → Mode test: False
   → Fréquence: 7  // ← Valeur du serveur distant
```

**Avantage :** Tu peux maintenant changer la config sur le serveur, et elle sera automatiquement appliquée au prochain démarrage de l'app (sans rebuild ni ADB) !

---

## 🧪 Tests de Validation

### Test 1 : Vérifier le mode actuel

```bash
adb shell run-as org.tarot.macartedetarot cat files/config.json
```

### Test 2 : Désactiver complètement les pubs

```json
{
  "ads_enabled": false  // ← Aucune pub ne s'affichera
}
```

### Test 3 : Changer la fréquence

```json
{
  "ads_frequency": 1  // ← Pub à CHAQUE tirage (très agressif)
}
```

```json
{
  "ads_frequency": 10  // ← Pub tous les 10 tirages (plus doux)
}
```

### Test 4 : Simuler un nouvel utilisateur

```bash
# Supprimer config.json (revient aux valeurs par défaut)
adb shell run-as org.tarot.macartedetarot rm files/config.json

# Redémarrer
adb shell am force-stop org.tarot.macartedetarot
adb shell am start -n org.tarot.macartedetarot/.MainActivity
```

**Résultat :** L'app utilise `config.default.json` embarqué (mode TEST).

---

## 🎯 Workflow de Déploiement Production

### Étape 1 : Build avec IDs de TEST

```bash
buildozer android release
```

### Étape 2 : Upload sur Play Console

1. Va sur https://play.google.com/console/
2. **Tests Internes** → Nouvelle version
3. Upload `bin/macartedetarot-0.01-arm64-v8a_armeabi-v7a-release.aab`
4. Ajoute testeurs (ton email)

### Étape 3 : Download sur appareil de test

1. Ouvre Play Store sur ton appareil
2. Va dans "Mes Jeux et Apps"
3. Installe la version de test

### Étape 4 : Vérifier le mode TEST

```bash
adb logcat | findstr /I "AdMob"
```

**Devrait afficher :** `Using TEST IDs`

### Étape 5 : Pousser config PRODUCTION via ADB

```bash
adb push config.json /sdcard/
adb shell run-as org.tarot.macartedetarot cp /sdcard/config.json /data/data/org.tarot.macartedetarot/files/config.json
adb shell rm /sdcard/config.json
```

### Étape 6 : Redémarrer et vérifier

```bash
adb shell am force-stop org.tarot.macartedetarot
adb shell am start -n org.tarot.macartedetarot/.MainActivity
adb logcat | findstr /I "AdMob"
```

**Devrait afficher :** `Using PRODUCTION IDs`

### Étape 7 : Test final

- Tire 5 cartes
- La 5ème devrait afficher une **vraie pub AdMob**
- Vérifie sur le dashboard AdMob (apps.admob.com) que l'impression est comptée

---

## 🐛 Debugging

### Problème : Aucune pub ne s'affiche

**1. Vérifie que les pubs sont activées :**
```bash
adb shell run-as org.tarot.macartedetarot cat files/config.json | findstr "ads_enabled"
```

Devrait afficher : `"ads_enabled": true`

**2. Vérifie le mode :**
```bash
adb logcat | findstr /I "AdMob"
```

Devrait afficher :
- `Using TEST IDs` ou `Using PRODUCTION IDs`
- `Showing interstitial ad`

**3. Vérifie les permissions :**
```bash
adb shell dumpsys package org.tarot.macartedetarot | findstr "INTERNET"
```

Devrait afficher : `android.permission.INTERNET: granted=true`

### Problème : Pub de test s'affiche en mode PROD

**Cause :** Le fichier `config.json` n'a pas été correctement poussé.

**Solution :**
```bash
# Vérifier
adb shell run-as org.tarot.macartedetarot cat files/config.json

# Re-pousser
adb push config.json /sdcard/
adb shell run-as org.tarot.macartedetarot cp /sdcard/config.json /data/data/org.tarot.macartedetarot/files/config.json
adb shell rm /sdcard/config.json

# Redémarrer
adb shell am force-stop org.tarot.macartedetarot
adb shell am start -n org.tarot.macartedetarot/.MainActivity
```

### Problème : Config à distance ne fonctionne pas

**1. Vérifie l'URL :**
```bash
adb shell run-as org.tarot.macartedetarot cat files/config.json | findstr "remote_config_url"
```

**2. Teste l'URL manuellement :**
```bash
curl https://ton-url.com/config.json
```

**3. Vérifie les logs :**
```bash
adb logcat | findstr /I "remote_config"
```

---

## 📊 Monitoring

### Dashboard AdMob

1. Va sur https://apps.admob.com/
2. Sélectionne "Ma Carte de Tarot"
3. **Metrics** :
   - Impressions : Nombre de pubs affichées
   - Clicks : Nombre de clics sur les pubs
   - eCPM : Revenu par 1000 impressions
   - Estimated Earnings : Revenus estimés

**Note :** Les données mettent **24-48h** à apparaître.

### Logs temps réel

```bash
# Suivre les tirages et pubs
adb logcat | findstr /I "TIRAGE AdMob"
```

**Output typique :**
```
=== NOUVEAU TIRAGE ===
Carte tirée: Le Bateleur - a l'envers
📊 Lecture #5
AdMob: Showing interstitial ad (count: 5)
```

---

## 🔑 Résumé des Commandes

```bash
# Vérifier config actuelle
adb shell run-as org.tarot.macartedetarot cat files/config.json

# Pousser nouvelle config
adb push config.json /sdcard/
adb shell run-as org.tarot.macartedetarot cp /sdcard/config.json /data/data/org.tarot.macartedetarot/files/config.json
adb shell rm /sdcard/config.json

# Redémarrer app
adb shell am force-stop org.tarot.macartedetarot
adb shell am start -n org.tarot.macartedetarot/.MainActivity

# Suivre logs AdMob
adb logcat | findstr /I "AdMob TarotApp"

# Réinitialiser config (revenir aux valeurs par défaut)
adb shell run-as org.tarot.macartedetarot rm files/config.json
```

---

## ✅ Checklist Finale

Avant de publier sur Play Store :

- [ ] Build avec `ads_test_mode: true` dans `config.default.json`
- [ ] Upload sur **Tests Internes** Play Console
- [ ] Test avec pubs de test Google
- [ ] Créer `config.json` avec **vrais IDs AdMob**
- [ ] Pousser `config.json` sur appareil de test via ADB
- [ ] Vérifier que les **vraies pubs** s'affichent
- [ ] Vérifier dashboard AdMob (impressions comptées)
- [ ] Tester fréquence (ex: tous les 5 tirages)
- [ ] Tester désactivation (`ads_enabled: false`)
- [ ] Uploader fichier AAB final sur **Production**

**🚀 Ton app est prête pour la monétisation !**
