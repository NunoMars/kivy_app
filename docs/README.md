# 🌐 Configuration GitHub Pages pour Ma Carte de Tarot

## 📋 Vue d'ensemble

Ce setup GitHub Pages crée automatiquement un site web de support pour votre application Tarot, incluant :
- 🏠 **Page d'accueil** : Présentation de l'app
- 🔒 **Politique de confidentialité** : Document obligatoire pour Google Play
- 📞 **Page de support** : Contact et FAQ

## 🚀 Activation GitHub Pages

### 1️⃣ Activer GitHub Pages dans votre repo
1. Aller dans **Settings** > **Pages**
2. Source : **GitHub Actions**
3. Le workflow `deploy-pages.yml` se chargera du reste

### 2️⃣ URLs générées automatiquement
Après déploiement, votre site sera accessible à :
```
https://VOTRE-USERNAME.github.io/kivy_app/
```

#### Pages spécifiques :
- **Accueil** : `https://VOTRE-USERNAME.github.io/kivy_app/`
- **Politique confidentialité** : `https://VOTRE-USERNAME.github.io/kivy_app/privacy-policy.html`

## 📱 Utilisation pour Google Play Store

### 🔗 URLs à utiliser dans Google Play Console

1. **Site web de l'app** :
   ```
   https://VOTRE-USERNAME.github.io/kivy_app/
   ```

2. **Politique de confidentialité** :
   ```
   https://VOTRE-USERNAME.github.io/kivy_app/privacy-policy.html
   ```

3. **Email de support** :
   ```
   tarot.support@gmail.com
   ```

## 🛠️ Structure des fichiers

```
docs/
├── index.html              # Page d'accueil du site
├── privacy-policy.html     # Politique de confidentialité
└── README.md              # Ce fichier

.github/workflows/
└── deploy-pages.yml       # Workflow de déploiement automatique
```

## 🔄 Mise à jour automatique

Le site se met à jour automatiquement quand vous :
1. **Modifiez** un fichier dans le dossier `docs/`
2. **Committez** et **poussez** sur la branche `main`
3. **GitHub Actions** déploie automatiquement les changements

## 🎨 Personnalisation

### Modifier la page d'accueil
Éditez `docs/index.html` pour :
- Changer les couleurs
- Ajouter des fonctionnalités
- Modifier les textes

### Modifier la politique de confidentialité
Éditez `docs/privacy-policy.html` pour :
- Adapter à votre email
- Modifier les conditions
- Ajouter des clauses spécifiques

## ✅ Checklist avant publication Google Play

- [ ] **GitHub Pages activé** et site accessible
- [ ] **URL politique confidentialité** testée et fonctionnelle
- [ ] **Email de support** configuré et fonctionnel
- [ ] **Liens** dans Google Play Console mis à jour
- [ ] **Site web** professionnel et complet

## 🚀 Workflow de déploiement

Le fichier `.github/workflows/deploy-pages.yml` :

1. **Se déclenche** sur push dans `docs/` ou manuellement
2. **Copie** les fichiers HTML
3. **Génère** la page d'accueil automatiquement
4. **Déploie** sur GitHub Pages
5. **Notifie** le succès/échec

## 🎯 Avantages de cette approche

### ✅ Pour Google Play
- **URLs officielles** et stables
- **Politique conforme** aux exigences
- **Site professionnel** qui inspire confiance

### ✅ Pour les utilisateurs
- **Support centralisé** facilement accessible
- **Informations** claires sur l'app
- **Contact** simple et direct

### ✅ Pour vous
- **Gratuit** (GitHub Pages)
- **Automatique** (pas de maintenance)
- **Professionnel** (URLs propres)

## 📧 Configuration email

Pour `tarot.support@gmail.com` :
1. **Créer** le compte Gmail
2. **Configurer** la signature automatique
3. **Mettre en place** les réponses automatiques
4. **Surveiller** les messages régulièrement

---

**🎯 Résultat : Site web professionnel prêt pour Google Play Store en 5 minutes !**
