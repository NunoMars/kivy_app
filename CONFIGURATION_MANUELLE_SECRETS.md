# Guide de configuration manuelle des secrets GitHub

## 📋 Secrets à configurer

Allez sur GitHub > Settings > Secrets and Variables > Actions et configurez :

### 1. ANDROID_KEYSTORE
```
Nom: ANDROID_KEYSTORE
Valeur: (contenu du fichier keystore_base64.txt)
```

### 2. ANDROID_KEYSTORE_PASSWORD
```
Nom: ANDROID_KEYSTORE_PASSWORD
Valeur: macartedetarot2024
```

### 3. ANDROID_KEY_ALIAS
```
Nom: ANDROID_KEY_ALIAS
Valeur: upload
```

### 4. ANDROID_KEY_PASSWORD
```
Nom: ANDROID_KEY_PASSWORD
Valeur: macartedetarot2024
```

## 🔐 Contenu du keystore (à copier dans ANDROID_KEYSTORE)

Le contenu est dans le fichier `keystore_base64.txt` qui a été créé.

## 🚀 Après configuration

1. Commitez les changements
2. Créez le tag v1.4.0
3. Poussez vers GitHub
4. Le pipeline se déclenchera automatiquement

## 📝 Commandes Git

```bash
git add .
git commit -m "feat: nouvelle clé de signature v1.4"
git tag v1.4.0
git push origin main
git push origin v1.4.0
```
