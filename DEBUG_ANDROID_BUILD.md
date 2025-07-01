# Guide de débogage Android - GitHub Actions

## Problèmes courrants et solutions

### 1. Erreur "sdkmanager not found" ou chemin SDK incorrect

**Symptôme :** 
```
sdkmanager: command not found
Cannot find sdkmanager at /usr/local/lib/android/sdk/tools/bin/sdkmanager
```

**Cause :** 
Sur les runners GitHub Actions récents, `sdkmanager` se trouve dans `/usr/local/lib/android/sdk/cmdline-tools/latest/bin/` mais buildozer le cherche dans l'ancien chemin `/usr/local/lib/android/sdk/tools/bin/`.

**Solution :**
Les workflows créent automatiquement un lien symbolique :
```bash
sudo mkdir -p $ANDROID_HOME/tools/bin
sudo ln -sf $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager $ANDROID_HOME/tools/bin/sdkmanager
```

### 2. Erreur "Pillow installation failed"

**Symptôme :**
```
ERROR: Building wheel for Pillow failed
```

**Solution :**
Pillow a été supprimé des requirements car il n'est pas nécessaire pour cette app et cause des problèmes de build. Le script `update_buildozer.py` le supprime automatiquement.

### 3. Erreur libffi ou autotools

**Symptôme :**
```
libffi.pc not found
autotools: command not found
```

**Solution :**
Les workflows installent tous les outils système nécessaires :
```bash
sudo apt-get install -y libtool autoconf automake pkg-config libffi-dev libssl-dev
```

### 4. Problème de signature AAB

**Symptôme :**
```
AAPT2 aapt2-4.2.2-7147631-linux Daemon #0: Unexpected error during link
```

**Solution :**
Vérifier que les secrets de signature sont configurés dans GitHub :
- `ANDROID_KEYSTORE_BASE64`
- `KEYSTORE_PASSWORD`
- `KEY_ALIAS`
- `KEY_PASSWORD`

### 5. Erreur de version NDK

**Symptôme :**
```
NDK r25c is not supported by this version of buildozer
```

**Solution :**
Forcer la version NDK dans buildozer.spec :
```ini
android.ndk = 27.2.12479018
android.ndk_path = /usr/local/lib/android/sdk/ndk/27.2.12479018
```

## Scripts de diagnostic

### fix_sdk_paths.py
Script qui vérifie et corrige automatiquement les chemins SDK :
```bash
python3 .github/scripts/fix_sdk_paths.py
```

Ce script :
- Vérifie l'existence des répertoires SDK/NDK
- Teste le fonctionnement de sdkmanager
- Crée les liens symboliques nécessaires
- Accepte les licences Android

### configure_buildozer_sdk.py
Script qui force l'utilisation des SDK/NDK système :
```bash
python3 .github/scripts/configure_buildozer_sdk.py
```

Ce script :
- Met à jour buildozer.spec avec les bons chemins
- Supprime Pillow des requirements
- Configure les versions API appropriées

## Variables d'environnement importantes

```bash
export ANDROID_HOME=/usr/local/lib/android/sdk
export ANDROID_NDK_HOME=/usr/local/lib/android/sdk/ndk/27.2.12479018
export JAVA_HOME=/usr/lib/jvm/temurin-17-jdk-amd64
export PATH=$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH
export PKG_CONFIG_PATH=/usr/lib/x86_64-linux-gnu/pkgconfig:/usr/lib/pkgconfig:/usr/share/pkgconfig
```

## Configuration buildozer.spec finale

```ini
# SDK/NDK forcés pour GitHub Actions
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/27.2.12479018
android.ndk = 27.2.12479018

# API versions
android.api = 33
android.minapi = 21
android.ndk_api = 21

# Build artifacts
android.release_artifact = aab
android.debug_artifact = aab

# Permissions et configuration
android.accept_sdk_license = True
android.skip_update = False
```

## Commandes de diagnostic utiles

```bash
# Vérifier l'environnement
echo "ANDROID_HOME: $ANDROID_HOME"
echo "ANDROID_NDK_HOME: $ANDROID_NDK_HOME"
echo "JAVA_HOME: $JAVA_HOME"

# Tester sdkmanager
$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --version
$ANDROID_HOME/tools/bin/sdkmanager --version

# Lister les SDK installés
$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --list

# Vérifier buildozer
buildozer android debug --verbose
```

## Workflow de débogage

1. **Vérifier l'environnement** avec `fix_sdk_paths.py`
2. **Configurer buildozer** avec `configure_buildozer_sdk.py`
3. **Nettoyer le cache** : `rm -rf .buildozer ~/.buildozer`
4. **Tenter le build** : `buildozer android debug --verbose`
5. **Analyser les logs** en cas d'erreur

## Contact et support

En cas de problème persistant :
1. Vérifier les logs GitHub Actions
2. Comparer avec la configuration de référence
3. Tester localement avec Docker Ubuntu 22.04
