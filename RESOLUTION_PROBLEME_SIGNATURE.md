# 🔐 Guide de résolution des problèmes de signature Android

## 🚨 Problème actuel

Le pipeline GitHub Actions échoue à l'étape de signature avec l'erreur :
```
keystore password was incorrect
```

## 🔍 Diagnostic

Le fichier `googleplay.keystore` existe mais le mot de passe configuré dans les secrets GitHub est incorrect.

## 🛠️ Solution étape par étape

### 1. 🔐 Trouver le bon mot de passe du keystore

**Exécutez le script interactif :**
```bash
python configure_keystore_secrets.py
```

Ce script vous aidera à :
- Encoder le keystore en base64
- Tester différents mots de passe
- Identifier les aliases disponibles
- Générer les commandes pour configurer les secrets

### 2. 📝 Mots de passe courants à essayer

Si vous ne vous souvenez pas du mot de passe, essayez :
- `macartedetarot`
- `tarot`
- `android`
- `googleplay`
- Votre nom ou pseudonyme
- Une combinaison avec des chiffres (2023, 2024, etc.)
- Un mot de passe que vous utilisez habituellement

### 3. 🔧 Configuration manuelle des secrets

Si le script ne fonctionne pas, vous pouvez configurer manuellement :

1. **Encodez le keystore en base64 :**
```bash
# Linux/Mac
base64 -w 0 googleplay.keystore > keystore_base64.txt

# Windows PowerShell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("googleplay.keystore")) | Out-File -FilePath "keystore_base64.txt" -Encoding ASCII
```

2. **Configurez les secrets GitHub :**
```bash
# Remplacez <MOT_DE_PASSE> par le vrai mot de passe
gh secret set ANDROID_KEYSTORE --body "$(cat keystore_base64.txt)"
gh secret set ANDROID_KEYSTORE_PASSWORD --body "<MOT_DE_PASSE>"
gh secret set ANDROID_KEY_ALIAS --body "upload"
gh secret set ANDROID_KEY_PASSWORD --body "<MOT_DE_PASSE>"
```

### 4. 🔍 Vérification du keystore

Pour vérifier que votre mot de passe est correct :
```bash
keytool -list -keystore googleplay.keystore -storepass <MOT_DE_PASSE> -v
```

### 5. 🚀 Déclenchement du pipeline

Une fois les secrets configurés :
```bash
# Créer un nouveau tag
git tag v1.3.1
git push origin v1.3.1

# Ou déclencher manuellement sur GitHub Actions
```

## 📋 Secrets GitHub requis

| Secret | Description | Exemple |
|--------|-------------|---------|
| `ANDROID_KEYSTORE` | Keystore encodé en base64 | `MIIKsgIBAzCCCm4GCSqGSIb3DQEHAa...` |
| `ANDROID_KEYSTORE_PASSWORD` | Mot de passe du keystore | `monmotdepasse123` |
| `ANDROID_KEY_ALIAS` | Alias de la clé | `upload` ou `key0` |
| `ANDROID_KEY_PASSWORD` | Mot de passe de la clé | Souvent identique au keystore |

## 🆘 En cas de problème persistant

### Option 1 : Créer un nouveau keystore
```bash
# Créer un nouveau keystore
keytool -genkey -v -keystore new-googleplay.keystore -alias upload -keyalg RSA -keysize 2048 -validity 10000

# Puis l'encoder et configurer les secrets
```

### Option 2 : Utiliser la signature automatique Google Play

1. Uploadez un AAB non signé sur Google Play Console
2. Laissez Google Play gérer la signature
3. Configurez le workflow pour générer des AAB non signés

## 🔧 Commandes de dépannage

```bash
# Vérifier les secrets configurés
gh secret list

# Voir les logs du pipeline
gh run list --workflow=publish-android.yml
gh run view <RUN_ID> --log

# Relancer le pipeline
gh workflow run publish-android.yml
```

## 📱 Vérification finale

Après résolution, le pipeline devrait :
1. ✅ Construire l'AAB avec succès
2. ✅ Signer l'AAB avec la clé de production
3. ✅ Créer une release GitHub
4. ✅ Uploader sur Google Play Console (optionnel)

## 🎯 Prochaines étapes

1. **Résolvez le problème de mot de passe** avec le script `configure_keystore_secrets.py`
2. **Configurez les secrets GitHub** avec les bonnes valeurs
3. **Testez le pipeline** en poussant un nouveau tag
4. **Vérifiez la signature** de l'AAB généré

---

💡 **Astuce :** Notez quelque part le mot de passe une fois trouvé pour éviter ce problème à l'avenir !
