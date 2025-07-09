# GitHub Actions depuis WSL2/Ubuntu

Ce guide vous permet de déclencher et surveiller vos builds GitHub Actions directement depuis WSL2/Ubuntu.

## 🚀 Installation rapide

1. **Ouvrez WSL2/Ubuntu** et naviguez vers votre projet :
   ```bash
   cd /mnt/e/programmes/projects/kivy_app
   ```

2. **Exécutez le script d'installation** :
   ```bash
   chmod +x scripts/setup-wsl2.sh
   ./scripts/setup-wsl2.sh
   ```

3. **Configurez votre token GitHub** :
   ```bash
   ~/kivy_app_scripts/setup-github-token.sh
   ```

4. **Rechargez votre terminal** :
   ```bash
   source ~/.bashrc
   ```

## 🔑 Configuration du token GitHub

### Créer un token GitHub :
1. Allez sur : https://github.com/settings/tokens
2. Cliquez "Generate new token (classic)"
3. Sélectionnez les permissions :
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
4. Copiez le token généré
5. Exécutez : `~/kivy_app_scripts/setup-github-token.sh`

## 📱 Utilisation

### Commandes rapides (après installation) :
```bash
# Build APK + AAB avec surveillance en temps réel
kivy-build

# Build APK seulement
kivy-apk

# Build AAB seulement  
kivy-aab

# Vérifier le statut des builds
kivy-status
```

### Commandes avancées :
```bash
# Script principal avec toutes les options
trigger-github-build.sh --help

# Déclencher et surveiller
trigger-github-build.sh --watch both

# Vérifier seulement le statut
trigger-github-build.sh --status

# Build sur une branche spécifique
trigger-github-build.sh --branch develop aab
```

## 📊 Surveillance des builds

Le script peut surveiller vos builds en temps réel :

```bash
# Surveillance automatique
kivy-build

# Surveillance manuelle
trigger-github-build.sh --watch
```

Affichage en temps réel :
```
=== Surveillance des builds GitHub Actions ===
Repo: NunoMars/kivy_app
Mis à jour: Wed Jul  9 15:30:45 2025

ID           Status              Conclusion          Created              URL
----         ------              ----------          -------              ---
12345678     🔄 in_progress      running             07/09 15:28          https://github.com/...
12345677     ✅ completed        success             07/09 14:45          https://github.com/...
12345676     ❌ completed        failure             07/09 13:22          https://github.com/...
```

## 🛠️ Dépannage

### Problème : "Token GitHub non trouvé"
```bash
# Solution 1 : Reconfigurer le token
~/kivy_app_scripts/setup-github-token.sh

# Solution 2 : Exporter manuellement
export GITHUB_TOKEN="your_token_here"

# Solution 3 : Passer en paramètre
trigger-github-build.sh -t your_token_here
```

### Problème : "Impossible d'accéder au repo"
```bash
# Vérifiez votre token et permissions
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/repos/NunoMars/kivy_app
```

### Problème : "Commande non trouvée"
```bash
# Rechargez votre terminal
source ~/.bashrc

# Ou utilisez le chemin complet
~/kivy_app_scripts/trigger-github-build.sh --status
```

### Problème : "curl ou jq non installé"
```bash
# Réexécutez l'installation
./scripts/setup-wsl2.sh
```

## 📋 Structure des scripts

Après installation, vous aurez :

```
~/kivy_app_scripts/
├── trigger-github-build.sh    # Script principal
├── setup-github-token.sh      # Configuration du token
└── kivy-build.sh              # Raccourcis de build
```

## 🔗 Liens utiles

- **Actions du repo** : https://github.com/NunoMars/kivy_app/actions
- **Workflow Android** : https://github.com/NunoMars/kivy_app/actions/workflows/build-android.yml
- **Tokens GitHub** : https://github.com/settings/tokens
- **Documentation API** : https://docs.github.com/en/rest/actions

## ⚡ Tips et astuces

### 1. Surveillance en arrière-plan
```bash
# Lancer la surveillance en arrière-plan
nohup trigger-github-build.sh --watch > build.log 2>&1 &

# Voir les logs en temps réel
tail -f build.log
```

### 2. Notifications desktop (si X11 configuré)
```bash
# Ajouter à votre .bashrc
kivy-build-notify() {
    kivy-build "$@"
    notify-send "Build terminé" "Vérifiez le statut"
}
```

### 3. Script personnalisé
```bash
# Créer votre propre script
cat > ~/my-build.sh << 'EOF'
#!/bin/bash
echo "🚀 Mon build personnalisé..."
trigger-github-build.sh --watch both
echo "✅ Build terminé!"
EOF
chmod +x ~/my-build.sh
```

### 4. Intégration avec VS Code
Si vous utilisez VS Code avec WSL2 :
```bash
# Ouvrir le terminal WSL2 dans VS Code
code --remote wsl+Ubuntu-22.04
```

Puis utilisez les commandes directement dans le terminal intégré.

## 🚨 Sécurité

- ⚠️ **Ne jamais** commiter votre token GitHub
- ✅ Utilisez les variables d'environnement
- ✅ Régénérez votre token régulièrement
- ✅ Limitez les permissions au minimum nécessaire

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez les prérequis : WSL2, Ubuntu, accès internet
2. Relancez l'installation : `./scripts/setup-wsl2.sh`
3. Vérifiez votre token : `echo $GITHUB_TOKEN`
4. Testez l'API : `trigger-github-build.sh --status`

---

**Prêt à builder ? 🚀**
```bash
kivy-build
```
