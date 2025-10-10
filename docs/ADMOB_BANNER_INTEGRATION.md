# 🎯 INTÉGRATION BANNIÈRE ADMOB - Ma Carte de Tarot

## ✅ Statut : INTÉGRÉ

La bannière AdMob a été **intégrée avec succès** dans l'application !

---

## 📋 Tes IDs AdMob (PRODUCTION)

| Type | ID |
|------|-----|
| **App ID** | `ca-app-pub-5749803259882370~1482612480` |
| **Bannière** | `ca-app-pub-5749803259882370/8646786637` |
| **Interstitielle** | *À créer* (pour l'instant : IDs Google de test) |

---

## 🔧 Modifications Apportées

### 1. Fichiers Créés

- ✅ `config.production.json` - Config avec tes IDs de production

### 2. Fichiers Modifiés

- ✅ `resources/values/strings.xml` - App ID mis à jour
- ✅ `main.py` - Ajout méthodes `on_enter` / `on_leave` sur `ResponseScreen`

---

## 📱 Comportement de la Bannière

### Où s'affiche-t-elle ?

**Écran de réponse (ResponseScreen) uniquement**

- ✅ Apparaît quand tu arrives sur l'écran de réponse (après tirage)
- ✅ Disparaît quand tu quittes l'écran (retour au tirage)
- ✅ Position : `bottom` (bas de l'écran)

### Configuration

Dans `config.production.json` :

```json
{
  "banner_enabled": true,        // ← Activer la bannière
  "banner_position": "bottom",   // ← Position (bottom ou top)
  "interstitial_enabled": false  // ← Désactiver interstitielle pour l'instant
}
```

---

## 🚀 Comment Tester

### Étape 1 : Build l'APK

```powershell
buildozer android release
```

### Étape 2 : Installer sur Android

```powershell
adb install -r bin/macartedetarot-0.01-arm64-v8a_armeabi-v7a-release.aab
```

### Étape 3 : Mode TEST (bannière Google de test)

Par défaut, `config.default.json` est en mode TEST.

**Comportement attendu :**
- Tire une carte
- Va sur l'écran de réponse
- **Bannière de test Google** apparaît en bas (label "Test Ad")

**Logs :**
```powershell
adb logcat -s "AdMob:* ResponseScreen:* TarotApp:*"
```

**Output attendu :**
```
📱 ResponseScreen: on_enter - Affichage bannière AdMob
AdMob: Showing banner (TEST mode)
```

### Étape 4 : Mode PRODUCTION (ta vraie bannière)

```powershell
# Copier la config production
Copy-Item config.production.json config.json

# Déployer sur Android
.\deploy_config.ps1
```

**Ou utiliser le script interactif :**
```powershell
.\deploy_config.ps1 prod
```

**Comportement attendu :**
- Tire une carte
- Va sur l'écran de réponse
- **Ta vraie bannière AdMob** apparaît en bas

**Logs :**
```
📱 ResponseScreen: on_enter - Affichage bannière AdMob
AdMob: Showing banner (PRODUCTION mode)
AdMob Banner ID: ca-app-pub-5749803259882370/8646786637
```

---

## ⚠️ Délai de Diffusion AdMob

**Important :** Selon Google, un **délai d'une heure** peut être nécessaire pour que les nouveaux blocs commencent à diffuser des annonces.

**Pendant ce délai, tu verras :**
- Espace blanc à la place de la bannière
- Ou bannière vide

**Après 1 heure, tu verras :**
- Ta vraie bannière avec pubs

**Vérification :**
- Dashboard AdMob : https://apps.admob.com/
- **Metrics** → Impressions (données sous 24-48h)

---

## 🎨 Personnalisation de la Bannière

### Changer la Position

**Option 1 : En haut de l'écran**

```json
// config.production.json
{
  "banner_position": "top"
}
```

**Option 2 : En bas de l'écran (actuel)**

```json
// config.production.json
{
  "banner_position": "bottom"
}
```

### Désactiver la Bannière Temporairement

```json
// config.production.json
{
  "banner_enabled": false
}
```

Puis redéploie :
```powershell
.\deploy_config.ps1
```

---

## 📊 Bannière vs Interstitielle

### Bannière (Actuelle)

**Avantages :**
- ✅ Toujours visible
- ✅ Pas intrusif
- ✅ Bonne UX

**Inconvénients :**
- ❌ Revenus faibles (eCPM €0.50-2)
- ❌ Prend de la place à l'écran

**Revenus estimés (France, eCPM €1) :**
- 1,000 utilisateurs/mois × 10 tirages = **€10/mois**

### Interstitielle (À Créer)

**Avantages :**
- ✅ Revenus élevés (eCPM €2-5)
- ✅ Plein écran, plus visible

**Inconvénients :**
- ❌ Intrusif si trop fréquent
- ❌ Peut dégrader l'UX

**Revenus estimés (France, eCPM €3, fréquence 5) :**
- 1,000 utilisateurs/mois × 10 tirages = **€6/mois**

### Recommandation : HYBRIDE (Bannière + Interstitielle)

**Meilleur compromis :**
- Bannière **toujours visible** (revenus continus)
- Interstitielle **tous les 5-7 tirages** (boost revenus)

**Revenus estimés (France) :**
- Bannière (eCPM €1) : €10/mois
- Interstitielle (eCPM €3, freq 5) : €6/mois
- **Total : €16/mois** (1,000 utilisateurs)

---

## 🔜 Prochaines Étapes

### Étape 1 : Créer Bloc Interstitiel AdMob

1. Va sur https://apps.admob.com/
2. Sélectionne "Ma Carte de Tarot"
3. **Ad units** → **Add ad unit**
4. Choisis **"Interstitial"**
5. Nom : `Tarot_Interstitial`
6. Copie l'ID généré : `ca-app-pub-5749803259882370/XXXXXXXXXX`

### Étape 2 : Mettre à Jour config.production.json

```json
{
  "admob_inter_id": "ca-app-pub-5749803259882370/XXXXXXXXXX",
  "interstitial_enabled": true,
  "ads_frequency": 5
}
```

### Étape 3 : Redéployer

```powershell
.\deploy_config.ps1 prod
```

**Résultat :**
- Bannière sur écran de réponse
- Interstitielle tous les 5 tirages

---

## 🐛 Debugging

### Problème : Bannière ne s'affiche pas

**Checklist :**

1. **Vérifier que la bannière est activée :**
   ```powershell
   adb shell run-as org.tarot.macartedetarot cat files/config.json | findstr "banner_enabled"
   ```
   → Devrait afficher : `"banner_enabled": true`

2. **Vérifier les logs :**
   ```powershell
   adb logcat -s "AdMob:* ResponseScreen:*"
   ```
   → Devrait afficher : `Showing banner`

3. **Attendre 1 heure** (délai Google pour nouveaux blocs)

4. **Vérifier l'ID de bannière :**
   ```powershell
   adb shell run-as org.tarot.macartedetarot cat files/config.json | findstr "banner_id"
   ```
   → Devrait afficher : `"admob_banner_id": "ca-app-pub-5749803259882370/8646786637"`

### Problème : Espace blanc au lieu de la bannière

**Cause :** Délai de diffusion AdMob (max 1h)

**Solution :** Attendre ou tester avec IDs de test Google :

```json
// Temporairement dans config.json
{
  "ads_test_mode": true,
  "admob_banner_id": "ca-app-pub-3940256099942544/6300978111"
}
```

### Problème : Bannière s'affiche partout

**Cause :** Méthode `on_leave` non appelée

**Solution :** Vérifier les logs :
```powershell
adb logcat -s "ResponseScreen:*"
```

Devrait afficher :
```
on_enter - Affichage bannière
on_leave - Masquage bannière
```

---

## ✅ Checklist Bannière

- [✅] Bloc d'annonces créé sur AdMob
- [✅] `config.production.json` créé avec ton ID
- [✅] `resources/values/strings.xml` mis à jour
- [✅] `main.py` modifié (on_enter / on_leave)
- [✅] Documentation complète

**À Faire :**

- [ ] Build l'APK
- [ ] Tester en mode TEST (bannière Google de test)
- [ ] Déployer config production
- [ ] Attendre 1h (délai AdMob)
- [ ] Vérifier bannière de production
- [ ] Créer bloc interstitiel
- [ ] Tester système hybride (bannière + interstitiel)

---

## 📚 Ressources

- **AdMob Dashboard :** https://apps.admob.com/
- **Guide Bannières :** https://developers.google.com/admob/android/banner
- **Politique AdMob :** https://support.google.com/admob/answer/6128543

---

**🎉 Ta bannière est intégrée et prête à monétiser !**

**💰 Prochaine étape : Créer le bloc interstitiel pour maximiser les revenus.**
