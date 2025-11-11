# 🎯 Vérifications AdMob (important)

> Note importante: Dans AdMob, la section « Campagnes » (auto‑promo/House ads) peut afficher « 0 activé(e)(s) » sans que cela bloque la diffusion des annonces AdMob classiques. Vous n'avez PAS besoin de créer/activer des campagnes pour voir des pubs AdMob standards. Le « 0 activé(e)(s) » de cette section n'est pas bloquant.

Ce document récapitule les vérifications utiles côté AdMob et côté app pour s'assurer que la diffusion est possible et optimale.

---

## ✅ Vérifier les blocs d'annonces

### Étape 1 : Aller sur AdMob Console

🔗 https://apps.admob.com/

### Étape 2 : Sélectionner l'application

1. Cliquer sur **"Applications"** dans le menu gauche
2. Chercher **"Ma Carte De Tarot"**
3. Cliquer dessus

### Étape 3 : Accéder aux blocs d'annonces

1. Cliquer sur **"Blocs d'annonces"** (ou "Ad units")
2. Tu devrais voir :
   - `Tarot_Banner` (Bannière)
   - `Ma carte de tarot pleine page` (Interstitiel)

### Étape 4 : Statut des blocs

- Ouvrir chaque bloc (bannière et interstitiel) et vérifier qu'il n'est pas en pause/supprimé.
- La mention « 0 activé(e)(s) » dans « Campagnes » n'a pas d'impact sur les blocs standards.

---

## 📋 Checklist complète

### Pour le bloc **Tarot_Banner** (Bannière)
- [ ] Ouvrir le bloc dans AdMob Console
- [ ] Vérifier l'ID : `ca-app-pub-5749803259882370/8646786637`
- [ ] **Activer** le bloc d'annonces
- [ ] Vérifier statut : **Actif** (vert)
- [ ] Vérifier compteur : **1 activé(e)(s)**

### Pour le bloc **Ma carte de tarot pleine page** (Interstitiel)
- [ ] Ouvrir le bloc dans AdMob Console
- [ ] Vérifier l'ID : `ca-app-pub-5749803259882370/4840878344`
- [ ] **Activer** le bloc d'annonces
- [ ] Vérifier statut : **Actif** (vert)
- [ ] Vérifier compteur : **1 activé(e)(s)**

---

## 🔧 Autres paramètres à vérifier

### 1. Médiation activée
Pour chaque bloc, vérifier que la médiation est configurée :
- Aller dans **"Médiation"** du bloc
- Vérifier que **ironSource** et **AppLovin** sont actifs
- Vérifier l'ordre de cascade (waterfall)

### 2. Limites de fréquence
Vérifier qu'il n'y a pas de limites trop restrictives :
```
Au niveau du bloc d'annonces : Aucune limite ✅
Au niveau de l'application : Aucune limite ✅
```

### 3. Pays ciblés
- Aller dans **"Ciblage"** → **"Pays"**
- Vérifier que **tous les pays** sont sélectionnés (ou au moins la France/Portugal)

### 4. Format d'annonce
- **Bannière** : Format standard (320x50)
- **Interstitiel** : Plein écran

---

## 🚨 Problèmes courants

### "Le bloc ne peut pas être activé"
**Causes possibles** :
1. **App-ads.txt manquant** → Push GitHub + attendre 24h
2. **Consentement UMP manquant en EEE** → Implémenter le SDK UMP (consentement RGPD)
3. **App non publiée/associée** → Lister l'app sur le Play Store et l'associer dans AdMob
4. **Compte AdMob non approuvé** → Vérifier le statut du compte

**Solution** :
```bash
# 1. Push app-ads.txt
git add docs/app-ads.txt
git commit -m "Add app-ads.txt for AdMob verification"
git push

# 2. Vérifier que GitHub Pages sert le fichier
curl https://nunomars.github.io/kivy_app/app-ads.txt
# Doit afficher : google.com, pub-5749803259882370, DIRECT, f08c47fec0942fa0

# 3. Dans AdMob Console → Paramètres → app-ads.txt
# Ajouter l'URL : https://nunomars.github.io/kivy_app/app-ads.txt

# 4. Attendre 24-48h pour validation
```

### "Activé mais toujours 0 impressions"
**Vérifier** :
1. L'app est bien publiée sur Play Store (version production)
2. L'ID app AdMob est correct dans `config.default.json`
3. Les IDs blocs sont corrects dans `config.default.json`
4. Le mode test est désactivé : `"ads_test_mode": false`

---

## 🎯 Configuration finale attendue

### Dans config.default.json
```json
{
  "ads_enabled": true,
  "ads_test_mode": false,  ← IMPORTANT : false en production !
  "admob_app_id": "ca-app-pub-5749803259882370~1482612480",
  "admob_banner_id": "ca-app-pub-5749803259882370/8646786637",
  "admob_inter_id": "ca-app-pub-5749803259882370/4840878344"
}
```

### Dans AdMob Console
```
App : Ma Carte De Tarot
├─ Statut app : ✅ Actif
├─ App-ads.txt : ✅ Validé (après 24-48h)
├─ Blocs d'annonces :
   ├─ Tarot_Banner
   │  ├─ Type : Bannière
   │  ├─ Statut : ✅ Actif (pas en pause)
   │  └─ Médiation : ironSource + AppLovin
   └─ Ma carte de tarot pleine page
      ├─ Type : Interstitiel
   ├─ Statut : ✅ Actif (pas en pause)
      └─ Médiation : ironSource + AppLovin
```

---

## ⏱️ Délais à prévoir

### Activation immédiate
- ✅ Cliquer sur "Activer" → Effet immédiat dans AdMob Console

### Premières pubs
- ⏳ **15-30 minutes** : Temps de propagation AdMob
- ⏳ **1-2 heures** : Premières demandes de pub enregistrées
- ⏳ **24 heures** : Premières statistiques fiables

### App-ads.txt
- ⏳ **24-48 heures** : Validation par Google après push GitHub
- ⏳ **48-72 heures** : Amélioration du taux de remplissage

---

## 🔍 Vérification après activation

### Dans AdMob Console (30 min après activation)
1. Aller dans **"Statistiques"**
2. Filtrer par **"Bloc d'annonces"**
3. Sélectionner **"Dernières 24 heures"**
4. Vérifier :
   - **Demandes** > 0 (l'app demande des pubs)
   - **Impressions** > 0 (des pubs sont affichées)
   - **Taux de remplissage** > 0% (idéalement > 30%)

### Dans l'app (en production)
```bash
# Installer l'app depuis Play Store
# Ouvrir l'app
# Vérifier avec logcat :
adb logcat | grep -E "AdMob|KivMob|Banner|Interstitial"

# Logs attendus :
# ✅ "AdMob: KivMob instance created (NPA=enabled)"
# ✅ "KivMob: Banner created"
# ✅ "KivMob: Banner load requested"
# ✅ "KivMob: Banner loaded successfully" ← Important !
# ✅ "KivMob: Interstitial loaded"
```

---

## 📞 Support

Si les blocs restent inactifs après 48h :
1. Vérifier le statut du compte AdMob (pas de violation de politique)
2. Vérifier que l'app est publiée (pas en draft)
3. Contacter le support AdMob avec les IDs des blocs

---

## 🚀 Actions prioritaires MAINTENANT

1. **[ ] Push app-ads.txt sur GitHub** (pour validation)
2. **[ ] Activer les 2 blocs dans AdMob Console** (Bannière + Interstitiel)
3. **[ ] Vérifier config.default.json** (`ads_test_mode: false`)
4. **[ ] Attendre 24-48h** pour validation app-ads.txt
5. **[ ] Monitorer statistiques AdMob** après 48h

---

## ✅ Succès attendu

Après ces étapes, dans 24-48h :
- ✅ Blocs AdMob : **1 activé(e)(s)** au lieu de 0
- ✅ App-ads.txt : **Validé** dans AdMob
- ✅ Statistiques : **Demandes > 0**, **Impressions > 0**
- ✅ Utilisateurs voient les pubs dans l'app
