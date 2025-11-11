# 🔍 Guide de diagnostic des publicités

## Problème : Les pubs ne s'affichent pas en production

### ✅ Correction appliquée

**Problème identifié** : Au premier lancement, `consent_personalized = None` désactivait les pubs.

**Solution** : Pubs activées par défaut (mode non personnalisé/NPA conforme RGPD).

---

## 📱 Comment tester sur votre device

### 1. Installer l'app via ADB

```bash
# Si vous avez l'AAB
bundletool build-apks --bundle=bin/macartedetarot-2.0-*.aab \
  --output=/tmp/app.apks \
  --ks=googleplay.keystore \
  --ks-pass=pass:nunotheboss \
  --ks-key-alias=upload \
  --key-pass=pass:nunotheboss \
  --mode=universal

bundletool install-apks --apks=/tmp/app.apks

# OU directement si vous avez un APK de debug
adb install -r bin/*.apk
```

### 2. Vérifier les logs en temps réel

```bash
adb logcat | grep -E "KivMob|AdMob|MobileAds|AdsManager|Interstitial|Banner"
```

### 3. Logs attendus au démarrage

```
✅ CORRECT :
I/python: ℹ️ Consentement inconnu → pubs non personnalisées activées (NPA)
I/python: ⏳ MobileAds.initialize lancé
I/python: ✅ MobileAds init status: ...
I/python: AdMob: Using PRODUCTION IDs
I/python: KivMob: Banner created (ca-app-pub-5749803259882370/8646786637, position=bottom)
I/python: KivMob: Banner load requested
I/python: KivMob: Banner attached to UI
I/python: KivMob: Requesting interstitial (ca-app-pub-5749803259882370/4840878344)
I/python: KivMob: Interstitial loaded  ← CRUCIAL !

❌ INCORRECT :
I/python: AdMob: Disabled by config
I/python: AdMob: Not on Android
```

### 4. Test bannière

- **Attendu** : Bannière visible en bas de l'écran dès l'ouverture de l'app
- **Si pas visible** : vérifier dans logcat si `Banner load requested` apparaît
- **Erreur courante** : `AdError: No fill` (pas de pub dispo, normal en test)

### 5. Test interstitiel

```bash
# Tirer 3 cartes de suite
# Au 3ème tirage, un interstitiel plein écran doit s'afficher

# Dans logcat, vérifier :
I/python: AdMob: Card drawn #3
I/python: AdMob: Showing interstitial
I/python: KivMob: Interstitial displayed
```

---

## 🐛 Diagnostic des erreurs courantes

### Erreur 1 : "Interstitial not loaded yet"

**Cause** : Le preload n'a pas eu le temps de finir
**Solution** : Attendre quelques secondes après le lancement

**Log attendu** :
```
W/python: KivMob: Interstitial not loaded yet
I/python: KivMob: Interstitial loaded  ← attendre ce message
```

### Erreur 2 : "Ad failed to load (code 3)"

**Cause** : `ERROR_CODE_NO_FILL` - Pas de pub disponible
**Raisons** :
- Nouvelle app, AdMob n'a pas encore de campagnes
- Quota quotidien atteint
- Pas de connexion internet
- App pas approuvée dans AdMob Console

**Solution** : 
1. Vérifier AdMob Console → Apps → Status : "Ready" ou "Getting ready"
2. Attendre 24-48h après première soumission
3. Tester avec test IDs : `ads_test_mode: true` dans config

### Erreur 3 : "App ID is missing"

**Cause** : Meta-data AdMob manquante dans AndroidManifest.xml
**Vérification** :

```bash
unzip -p bin/*.aab base/manifest/AndroidManifest.xml | grep -A2 "com.google.android.gms.ads.APPLICATION_ID"
```

**Attendu** :
```xml
<meta-data
    android:name="com.google.android.gms.ads.APPLICATION_ID"
    android:value="ca-app-pub-5749803259882370~1482612480"/>
```

### Erreur 4 : Listeners GC (Garbage Collected)

**Symptôme** : `onAdLoaded` jamais appelé
**Cause** : Références faibles sur callbacks Java
**Correction** : Déjà appliquée dans `ads_manager.py` et `libs/kivmob.py`

---

## 🔧 Rebuild avec correction

```bash
# 1. Clean build
buildozer android clean

# 2. Rebuild AAB
buildozer android release

# 3. Vérifier signature
jarsigner -verify -verbose bin/macartedetarot-*.aab

# 4. Copier sur bureau
cp bin/macartedetarot-*.aab /mnt/c/Users/loupy/Desktop/
```

---

## 📊 Vérifier dans AdMob Console

1. **Apps** → Votre app → **App settings**
   - Status : "Ready" ou "Getting ready"
   - Store presence : ✅ Published

2. **Ad units**
   - Banner : Active
   - Interstitial : Active
   - Impressions récentes : visible après quelques heures

3. **Mediation** (optionnel)
   - Si configuré : vérifier waterfalls ironSource/AppLovin

4. **app-ads.txt**
   - URL : https://nunomars.github.io/kivy_app/app-ads.txt
   - Status : ✅ Verified

---

## 🎯 Checklist complète

- [ ] `config.default.json` : `ads_enabled: true`, `ads_test_mode: false`
- [ ] IDs production corrects dans config
- [ ] `buildozer.spec` : `play-services-ads:23.6.0`
- [ ] Meta-data AdMob dans manifest
- [ ] Permission `AD_ID` présente
- [ ] Code corrections appliquées (race condition, listeners, workflow)
- [ ] AAB rebuild avec corrections
- [ ] Logs device : "MobileAds init", "Banner created", "Interstitial loaded"
- [ ] AdMob Console : app "Ready", ad units actives
- [ ] `app-ads.txt` publié et vérifié

---

## 📞 Support AdMob

Si les pubs ne s'affichent toujours pas après 48h :

1. AdMob Help Center : https://support.google.com/admob
2. Vérifier : **Policy violations** dans AdMob Console
3. Attendre l'approbation complète (peut prendre 2-3 jours)

---

**Dernière mise à jour** : 11 novembre 2025
