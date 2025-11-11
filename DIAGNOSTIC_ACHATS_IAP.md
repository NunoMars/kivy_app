# 🛒 Diagnostic Achats In-App (IAP)

## Problème : "Toujours en validation" alors que validé

### 🔍 Causes possibles

#### 1. **ID produit incorrect**
Le code utilise : `premium_features`

**Vérification Play Console** :
1. Play Console → Votre app → **Monétisation** → **Produits in-app**
2. Vérifier que l'ID exact est : `premium_features`
3. Status doit être : **Actif** (pas "Brouillon" ou "Inactif")

#### 2. **App non publiée sur une piste**
Google Play Billing nécessite que l'app soit publiée (même sur piste interne).

**Vérification** :
- Play Console → **Production**, **Tests ouverts**, **Tests fermés** ou **Tests internes**
- Au moins une version publiée sur une piste

#### 3. **Délai de propagation**
Après activation d'un produit in-app, attendre **4-24 heures** pour propagation.

#### 4. **Compte de test non configuré**
Pour tester les achats sans payer :

**Configuration** :
1. Play Console → **Configuration** → **Testeurs de licence**
2. Ajouter votre compte Gmail
3. Utiliser ce compte sur le device de test

---

## 🐛 Logs de diagnostic

### Ajouter logs détaillés dans billing.py

Cherchez cette fonction et ajoutez des logs :

```python
@java_method("(Lcom/android/billingclient/api/BillingResult;Ljava/util/List;)V")
def onProductDetailsResponse(self, billing_result, product_details_list):
    try:
        rc = billing_result.getResponseCode()
        # AJOUT: Log du code de réponse
        print(f"🔍 ProductDetails response code: {rc}")
        
        OK = self.manager.google_client_class.BillingResponseCode.OK
        if rc == OK and product_details_list and product_details_list.size() > 0:
            # AJOUT: Log du nombre de produits trouvés
            print(f"📦 Nombre de produits trouvés: {product_details_list.size()}")
            
            details = product_details_list.get(0)
            # AJOUT: Log de l'ID produit
            try:
                product_id = details.getProductId()
                print(f"✅ Produit ID trouvé: {product_id}")
            except:
                pass
                
            self.manager.google_product_details = details
            # ... reste du code
        else:
            # AJOUT: Log détaillé de l'erreur
            print(f"❌ ProductDetails échec - Code: {rc}")
            if product_details_list:
                print(f"   Liste size: {product_details_list.size()}")
            else:
                print(f"   Liste NULL")
```

### Vérifier logs device

```bash
adb logcat | grep -E "ProductDetails|Billing|premium_features"
```

**Logs attendus si OK** :
```
I/python: 🔍 ProductDetails response code: 0  ← 0 = OK
I/python: 📦 Nombre de produits trouvés: 1
I/python: ✅ Produit ID trouvé: premium_features
I/python: ✅ ProductDetails Google récupérés: 4,99 €
```

**Logs si problème** :
```
I/python: 🔍 ProductDetails response code: 4  ← 4 = ITEM_UNAVAILABLE
I/python: ❌ ProductDetails échec - Code: 4
I/python: ⚠️ ProductDetails indisponibles (code 4)
```

### Codes d'erreur Google Billing

| Code | Constante | Signification | Solution |
|------|-----------|---------------|----------|
| 0 | OK | Succès | ✅ Tout va bien |
| 1 | USER_CANCELED | Utilisateur a annulé | Normal |
| 2 | SERVICE_UNAVAILABLE | Service indisponible | Réessayer plus tard |
| 3 | BILLING_UNAVAILABLE | Billing désactivé | Vérifier Play Services |
| 4 | ITEM_UNAVAILABLE | Produit introuvable | **Vérifier ID produit + Status** |
| 5 | DEVELOPER_ERROR | Erreur config | Vérifier signing + package name |
| 6 | ERROR | Erreur générale | Vérifier logs détaillés |
| 7 | ITEM_ALREADY_OWNED | Déjà acheté | Normal, restaurer |
| 8 | ITEM_NOT_OWNED | Pas possédé | Normal |

---

## ✅ Checklist de vérification

### Dans Play Console

- [ ] **Produits in-app** → `premium_features` existe
- [ ] Status du produit : **Actif** (pas Brouillon/Inactif)
- [ ] Prix configuré (ex: 4,99 €)
- [ ] Au moins une version de l'app publiée (piste interne minimum)
- [ ] Compte de test ajouté dans "Testeurs de licence"

### Dans le code

- [ ] `billing.py` ligne 371 : `GOOGLE_INAPP_PRODUCT_ID = "premium_features"`
- [ ] ID correspond exactement à Play Console (casse sensible)
- [ ] `buildozer.spec` : `billing-ktx:8.0.0` présent
- [ ] Signing : AAB signé avec même keystore que versions précédentes

### Sur le device

- [ ] App installée via Play Store (ou APK signé avec bon keystore)
- [ ] Package name correspond : `org.tarot.macartedetarot`
- [ ] Compte Google utilisé dans la liste des testeurs
- [ ] Connexion internet active
- [ ] Play Services à jour

---

## 🔧 Solutions selon le code d'erreur

### Code 4 (ITEM_UNAVAILABLE) - Produit introuvable

**Cause** : L'ID `premium_features` n'existe pas ou n'est pas actif dans Play Console.

**Solutions** :
1. Vérifier ID exact dans Play Console (copier/coller)
2. Activer le produit s'il est en brouillon
3. Attendre 24h après création/activation
4. Vérifier que l'app est publiée sur au moins une piste

### Code 5 (DEVELOPER_ERROR) - Erreur développeur

**Cause** : Configuration incorrecte (signing, package, version).

**Solutions** :
1. Vérifier signing : même keystore que versions précédentes
2. Vérifier package name : `org.tarot.macartedetarot`
3. Vérifier version code : incrémenté vs versions précédentes
4. Installer via Play Store (pas ADB direct)

### Code 2 (SERVICE_UNAVAILABLE) - Service indisponible

**Cause** : Google Play Services problème temporaire.

**Solutions** :
1. Vérifier connexion internet
2. Mettre à jour Play Services : Play Store → Mes applis
3. Redémarrer device
4. Réessayer plus tard

---

## 🧪 Test complet achats in-app

### 1. Préparer l'environnement

```bash
# Vérifier que le device est bien configuré
adb shell dumpsys package org.tarot.macartedetarot | grep -A 5 "versionCode"

# Vérifier Play Services
adb shell dumpsys package com.android.vending | grep versionName
```

### 2. Installer l'app

```bash
# Via Play Console (recommandé) : piste interne/fermée
# OU via bundletool si test local :
bundletool build-apks --bundle=bin/macartedetarot-2.1-*.aab \
  --output=/tmp/app.apks \
  --ks=googleplay.keystore \
  --ks-pass=pass:nunotheboss \
  --ks-key-alias=upload \
  --key-pass=pass:nunotheboss

bundletool install-apks --apks=/tmp/app.apks
```

### 3. Lancer avec logs

```bash
# Terminal 1 : Logs
adb logcat -c && adb logcat | grep -E "Billing|premium_features|ProductDetails"

# Terminal 2 : Lancer l'app
adb shell am start -n org.tarot.macartedetarot/.PythonActivity
```

### 4. Tester le flux d'achat

Dans l'app :
1. **Ouvrir l'écran premium** (bouton "Acheter Premium")
2. **Vérifier logs** : "ProductDetails Google récupérés: X,XX €"
3. **Cliquer "Acheter"**
4. **Dialogue Google Play** doit s'afficher avec prix
5. **Si compte de test** : bouton "Acheter" marqué "Test"
6. **Compléter achat** (carte test ou compte test gratuit)
7. **Vérifier callback** : `on_purchase_success(premium_features, google)`

**Logs attendus** :
```
I/python: ✅ Connexion Billing Google établie
I/python: ✅ ProductDetails Google récupérés: 4,99 €
I/python: 🔍 Lancement achat premium_features
I/python: ✅ Achat Google confirmé pour ['premium_features']
I/python: ✨ Premium activé ! (provider=google)
```

---

## 🎯 Si le problème persiste

### Vérifier dans Play Console après 48h

1. **Monétisation** → **Produits in-app** → `premium_features`
   - Status : Actif
   - Transactions : doit afficher des tests si achat effectué

2. **Configuration** → **API access**
   - Service account lié
   - Permissions Billing configurées

3. **Toutes les applications** → Votre app
   - Package name : `org.tarot.macartedetarot`
   - Dernière version publiée visible

### Tester avec ID de test Google

Remplacer temporairement dans `billing.py` :

```python
# Test avec ID officiel Google (toujours disponible)
GOOGLE_INAPP_PRODUCT_ID = "android.test.purchased"  # ID de test Google
```

Si ça fonctionne → problème de config Play Console pour `premium_features`  
Si ça ne fonctionne pas → problème de Billing setup général

---

## 📞 Support

- **Play Console Help** : https://support.google.com/googleplay/android-developer/answer/1153481
- **Billing Library Docs** : https://developer.android.com/google/play/billing
- **Test achats** : https://developer.android.com/google/play/billing/test

---

**Dernière mise à jour** : 11 novembre 2025
