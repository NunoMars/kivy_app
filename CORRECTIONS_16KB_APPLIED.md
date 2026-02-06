# 🔧 CORRECTIONS APPLIQUÉES — Conformité Google Play 16KB

## ✅ Fichiers créés/modifiés

### 1. Recettes p4a patchées (alignement 16KB forcé)

- **p4a_recipes/python3/__init__.py** ✅
  - Override `get_recipe_env()` pour injecter flags 16KB dans LDFLAGS, LINKFORSHARED, BLDSHARED
  - Corrige: `libpython3.11.so` (0x1000 → 0x4000)

- **p4a_recipes/openssl/__init__.py** ✅ (nouveau)
  - Override `get_recipe_env()` pour OpenSSL Configure
  - Corrige: `libcrypto1.1.so`, `libssl1.1.so` (0x1000 → 0x4000)

- **p4a_recipes/sqlite3/__init__.py** ✅ (nouveau)
  - Override `get_recipe_env()` pour SQLite configure
  - Corrige: `libsqlite3.so` (0x1000 → 0x4000)

- **p4a_recipes/libffi/__init__.py** ✅ (nouveau)
  - Override `get_recipe_env()` pour libffi configure
  - Corrige: `libffi.so` (mixte 0x1000+0x4000 → pure 0x4000)

### 2. Scripts d'automatisation

- **verify_16kb_compliance.sh** ✅
  - Extraction AAB + analyse readelf de toutes les .so
  - Tableau couleur avec statut conformité
  - Exit code 0 si conforme, 1 si échec

- **fix_and_rebuild_16kb.sh** ✅
  - Clean des recettes non conformes
  - Export flags 16KB dans environnement
  - Rebuild complet + vérification automatique

---

## 🚀 PROCHAINES ÉTAPES

### Étape 1: Rebuild complet (OBLIGATOIRE)

```bash
cd /home/loupy/kivy_app
./fix_and_rebuild_16kb.sh
```

**Durée estimée**: 20-30 minutes (recompilation Python + OpenSSL complète)

**Logs à surveiller**:
```
[PYTHON3-16KB] ✅ LDFLAGS=... -Wl,-z,max-page-size=16384 ...
[OPENSSL-16KB] ✅ LDFLAGS=... -Wl,-z,max-page-size=16384 ...
[SQLITE3-16KB] ✅ LDFLAGS=... -Wl,-z,max-page-size=16384 ...
[LIBFFI-16KB] ✅ LDFLAGS=... -Wl,-z,max-page-size=16384 ...
```

---

### Étape 2: Vérification post-build

Le script `fix_and_rebuild_16kb.sh` lance automatiquement la vérification.

**Si succès attendu**:
```
✅ Conformes 16KB:      11 / 11
❌ Non conformes (4KB): 0 / 11
⚠️  Mixtes (4K+16K):    0 / 11

✅ ✅ ✅ CONFORMITÉ GOOGLE PLAY: OK ✅ ✅ ✅
```

**Si échec partiel**: Rerunner vérification manuelle:
```bash
./verify_16kb_compliance.sh bin/macartedetarot-2.XX-arm64-v8a-release.aab
```

---

### Étape 3: Tests pré-soumission

#### A. Test émulateur Android 15 (16KB activé)

```bash
# Créer émulateur Android 15 avec Pixel 9 config
avdmanager create avd -n test_16kb -k "system-images;android-35;google_apis;arm64-v8a" -d "pixel_9_pro"

# Démarrer avec 16KB pagesize
emulator -avd test_16kb -feature -Vulkan &

# Dans un autre terminal:
adb wait-for-device
adb shell setprop debug.pixelExperience.android.is16kbPageSizeDevice true
adb reboot

# Installer AAB (extraire APK universal d'abord)
bundletool build-apks --bundle=bin/macartedetarot-2.XX.aab --output=app.apks --mode=universal
unzip app.apks universal.apk
adb install universal.apk

# Lancer et vérifier logs
adb logcat | grep -E "dlopen|alignment|page|ELF"
```

**Succès attendu**: App démarre sans erreur `dlopen failed`

---

#### B. Soumission test interne Google Play

1. **Upload AAB** dans Play Console → "Testing" → "Internal testing"
2. **Attendre Pre-Launch Report** (15-30 min)
3. **Vérifier**:
   - ✅ Aucun crash sur Pixel 9 Pro
   - ✅ Section "Native code" → "No issues found"
   - ✅ Aucune alerte "16KB alignment"

**Red flags à surveiller**:
```
❌ "Your app contains native code libraries that are not aligned to 16KB"
❌ "dlopen failed: ELF load command alignment not page-aligned"
❌ Crash sur Pixel 9/10 dans pre-launch report
```

---

### Étape 4: Publication production

Une fois les tests OK:

```bash
# Signer AAB (si pas déjà signé)
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
  -keystore googleplay.keystore \
  -storepass nunotheboss \
  bin/macartedetarot-2.XX-arm64-v8a-release.aab upload

# Vérifier signature
jarsigner -verify -verbose bin/macartedetarot-2.XX-arm64-v8a-release.aab

# Upload via Play Console ou API
```

---

## 📋 CHECKLIST FINALE

- [ ] **Recettes patchées créées** (python3, openssl, sqlite3, libffi)
- [ ] **Build lancé**: `./fix_and_rebuild_16kb.sh`
- [ ] **Vérification OK**: Toutes les .so à 0x4000
- [ ] **Test émulateur Android 15**: App démarre sans crash
- [ ] **Pre-launch report**: Aucune erreur
- [ ] **AAB signé**: Prêt pour production
- [ ] **Upload Play Console**: Version publiée

---

## 🔄 Rebuild manuel si nécessaire

Si le script automatique échoue:

```bash
# 1. Clean complet
rm -rf .buildozer/android/platform/build-arm64-v8a/build/other_builds/{python3,openssl,sqlite3,libffi}*

# 2. Export flags
export LDFLAGS="-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384"
export CFLAGS="-Wl,-z,max-page-size=16384"
export CXXFLAGS="-Wl,-z,max-page-size=16384"

# 3. Build
buildozer android release

# 4. Vérifier
./verify_16kb_compliance.sh
```

---

## 📊 Résultat attendu final

```
═══════════════════════════════════════════════════════════════════
Bibliothèque                    Alignements    Statut
═══════════════════════════════════════════════════════════════════
libSDL2.so                      0x4000         ✅ CONFORME 16KB
libSDL2_image.so                0x4000         ✅ CONFORME 16KB
libSDL2_mixer.so                0x4000         ✅ CONFORME 16KB
libSDL2_ttf.so                  0x4000         ✅ CONFORME 16KB
libcrypto1.1.so                 0x4000         ✅ CONFORME 16KB  ← CORRIGÉ
libffi.so                       0x4000         ✅ CONFORME 16KB  ← CORRIGÉ
libmain.so                      0x4000         ✅ CONFORME 16KB
libpybundle.so                  N/A            ⚠️  NO LOAD (OK)
libpython3.11.so                0x4000         ✅ CONFORME 16KB  ← CORRIGÉ
libsqlite3.so                   0x4000         ✅ CONFORME 16KB  ← CORRIGÉ
libssl1.1.so                    0x4000         ✅ CONFORME 16KB  ← CORRIGÉ

✅ Conformes 16KB:      10 / 11 (91%)
❌ Non conformes:       0 / 11
⚠️  Mixtes:             0 / 11
⚠️  Sans LOAD:          1 / 11 (libpybundle - non exécuté, OK)

✅ ✅ ✅ CONFORMITÉ GOOGLE PLAY: OK ✅ ✅ ✅
```

---

## ⚠️ Troubleshooting

### Problème: Recettes non prises en compte

**Symptôme**: Après rebuild, les .so sont toujours à 0x1000

**Solution**:
```bash
# Vérifier que p4a utilise les recettes locales
ls -la p4a_recipes/python3/__init__.py
cat buildozer.spec | grep "p4a.local_recipes"

# Doit afficher:
# p4a.local_recipes = p4a_recipes

# Si absent, ajouter dans buildozer.spec:
# p4a.local_recipes = p4a_recipes

# Rebuild
rm -rf .buildozer
./fix_and_rebuild_16kb.sh
```

### Problème: Build échoue avec erreur linking

**Symptôme**: 
```
ld: error: unknown argument: -Wl,-z,max-page-size=16384
```

**Solution**: NDK trop ancien, mettre à jour:
```ini
# buildozer.spec
android.ndk = 26c  # ou plus récent
```

---

## 📞 Support

Si problèmes persistent après rebuild:

1. **Vérifier logs build**: Chercher `[PYTHON3-16KB]`, `[OPENSSL-16KB]` etc.
2. **Inspecter .so manuellement**:
   ```bash
   readelf -lW .buildozer/.../libs/arm64-v8a/libpython3.11.so | grep LOAD
   ```
3. **Vérifier versions NDK/SDK**: NDK 26c minimum requis

---

**Date des modifications**: 2026-02-06  
**Version buildozer.spec**: 2.41  
**Statut**: ✅ Corrections appliquées, rebuild requis
