# 📱 Guide de Publication Google Play Store

## 🎯 Statut Actuel

✅ **AAB (App Bundle) configuré** - Format requis par Google Play  
✅ **Build automatique fonctionnel** - Génère des AAB à chaque tag  
✅ **Descriptions Store prêtes** - Textes optimisés ASO  
⚠️ **Signature manquante** - Nécessaire pour publication  
⚠️ **Compte développeur requis** - 25$ d'inscription unique  

## 🔑 Étape 1 : Générer la Clé de Signature

### Sur votre machine locale :

```bash
# Rendre le script exécutable
chmod +x generate_signing_key.sh

# Exécuter le générateur
./generate_signing_key.sh
```

### Informations à fournir :
- **Nom complet** : Votre nom ou nom de l'organisation
- **Organisation** : Nom de votre studio/entreprise  
- **Ville** : Votre ville
- **Région** : Votre région/département
- **Pays** : FR
- **Mot de passe keystore** : Complexe et sécurisé
- **Mot de passe clé** : Peut être identique au keystore

## 🔒 Étape 2 : Configurer les Secrets GitHub

Allez dans **Settings > Secrets and variables > Actions** de votre repo :

### Secrets requis :

1. **ANDROID_KEYSTORE_BASE64**
   ```bash
   base64 -w 0 release.keystore
   ```
   Copiez tout le résultat

2. **KEYSTORE_PASSWORD**  
   Le mot de passe du keystore

3. **KEY_ALIAS**  
   `tarot_release` (ou le nom choisi)

4. **KEY_PASSWORD**  
   Le mot de passe de la clé

5. **GOOGLE_PLAY_SERVICE_ACCOUNT** *(optionnel pour l'auto-publication)*  
   JSON du compte de service Google Play Console

## 🏪 Étape 3 : Créer le Compte Développeur Google Play

1. **Inscription** : https://play.google.com/console/signup
2. **Frais** : 25$ USD (paiement unique)
3. **Vérification** : Peut prendre 1-3 jours
4. **Politique** : Accepter les conditions

## 📱 Étape 4 : Créer l'Application sur Play Console

### 4.1 Informations de base
- **Nom** : Ma Carte de Tarot
- **Description courte** : `🔮 Tirage de Tarot de Marseille authentique - Guidance spirituelle`
- **Description longue** : Voir `store_descriptions.md`
- **Catégorie** : Divertissement
- **Âge** : Tout public

### 4.2 Assets graphiques
- **Icône** : `store_assets/app_icon_512x512.png`
- **Bannière** : `store_assets/feature_graphic_1024x500.png`
- **Captures d'écran** : 2-8 images de l'app en action

### 4.3 Paramètres avancés
- **Package name** : `org.tarot.macartedetarot`
- **Version initiale** : 1 (0.1.0)
- **Target SDK** : 33 (Android 13)
- **Min SDK** : 21 (Android 5.0)

## 🚀 Étape 5 : Publication Automatique

### Créer un tag pour déclencher le build :

```bash
# Committer tous les changements
git add .
git commit -m "feat: configure AAB build for Google Play Store"

# Créer un tag de version
git tag v0.1.1
git push origin v0.1.1
```

### Le workflow va automatiquement :
1. ✅ Builder l'AAB
2. ✅ Signer avec votre clé (si configurée)
3. ✅ Uploader les artefacts
4. ✅ Créer une release GitHub
5. ⚠️ Publier sur Play Store (si compte service configuré)

## 📋 Étape 6 : Publication Manuelle (première fois)

1. **Télécharger l'AAB** depuis GitHub Actions artifacts
2. **Uploader sur Play Console** > Production > Créer une version
3. **Remplir les informations** : notes de version, etc.
4. **Examiner et publier** : Google va examiner (1-3 jours)

## 🔄 Mises à Jour Automatiques (futures versions)

Pour les versions suivantes :

```bash
# Faire vos modifications
git add .
git commit -m "feat: nouvelle fonctionnalité"

# Increment version dans buildozer.spec
# version = 0.2

# Créer nouveau tag
git tag v0.2.0
git push origin v0.2.0
```

L'AAB sera automatiquement généré et disponible !

## 🛡️ Sécurité et Bonnes Pratiques

### ✅ À faire :
- Sauvegarder le keystore en lieu très sûr
- Utiliser des mots de passe complexes
- Tester l'AAB avant publication
- Versionner correctement (semantic versioning)

### ❌ À éviter :
- Partager le keystore publiquement
- Commit le keystore dans le repo
- Oublier de sauvegarder (perte = fin de l'app)
- Changer de clé (impossible de mettre à jour)

## 📊 Suivi Post-Publication

### Métriques importantes :
- **Installations** : Nombre de téléchargements
- **Évaluations** : Note moyenne et commentaires
- **Crashs** : Rapports d'erreur automatiques
- **Performance** : Temps de lancement, ANR

### Optimisations continues :
- Analyser les retours utilisateurs
- Corriger les bugs rapportés
- Améliorer les descriptions selon les recherches
- Ajouter des fonctionnalités demandées

## 🎯 Checklist Finale

Avant publication, vérifier :

- [ ] AAB se build sans erreur
- [ ] App testé sur appareil physique
- [ ] Clé de signature configurée
- [ ] Descriptions store optimisées
- [ ] Assets graphiques de qualité
- [ ] Politique de confidentialité accessible
- [ ] Compte développeur validé
- [ ] Version incrémentée correctement

🔮 **Votre app Tarot est prête pour conquérir le monde spirituel !**

---

*Besoin d'aide ? Consultez la [documentation officielle](https://developer.android.com/guide/app-bundle) ou créez une issue GitHub.*
