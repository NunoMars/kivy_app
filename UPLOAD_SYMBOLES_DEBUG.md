# 📊 Upload des symboles de débogage - Play Console

## 🎯 Objectif

Faciliter le débogage des plantages et ANR en production en uploadant :
1. **Fichier de mapping ProGuard/R8** : désobscurcir le code Java/Kotlin
2. **Symboles natifs** : déboguer les bibliothèques natives (.so)

---

## 📁 Fichiers à uploader après chaque build

### 1. **Mapping ProGuard/R8** (désobscurcissement)

**Chemin après build** :
```
.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/macartedetarot/build/outputs/mapping/release/mapping.txt
```

**Où l'uploader** :
- Play Console → **Version** (celle de l'AAB uploadé) → **Téléchargements de l'App Bundle**
- Cliquer sur **"Importer un fichier de désobscurcissement"**
- Sélectionner `mapping.txt`

**Taille typique** : ~100-500 KB

---

### 2. **Symboles natifs** (bibliothèques .so)

**Chemin après build** :
```
.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/macartedetarot/build/outputs/native-debug-symbols/release/native-debug-symbols.zip
```

**Où l'uploader** :
- Play Console → **Version** → **Téléchargements de l'App Bundle**
- Cliquer sur **"Importer les symboles de débogage natifs"**
- Sélectionner `native-debug-symbols.zip`

**Taille typique** : ~10-50 MB (contient symboles pour arm64-v8a + armeabi-v7a)

---

## 🚀 Procédure complète après build v2.1

### Étape 1 : Build avec symboles activés ✅
```bash
buildozer android release
```

### Étape 2 : Récupérer les fichiers de débogage
```bash
# Créer un dossier pour cette version
mkdir -p debug_symbols/v2.1

# Copier le fichier de mapping ProGuard
cp .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/macartedetarot/build/outputs/mapping/release/mapping.txt debug_symbols/v2.1/

# Copier les symboles natifs
cp .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/macartedetarot/build/outputs/native-debug-symbols/release/native-debug-symbols.zip debug_symbols/v2.1/

# Copier aussi sur Windows desktop pour upload facile
cp debug_symbols/v2.1/* /mnt/c/Users/loupy/Desktop/debug_v2.1/
```

### Étape 3 : Upload sur Play Console

1. **Aller sur Play Console** : https://play.google.com/console
2. **Sélectionner l'app** : Ma Carte De Tarot
3. **Version** → Production → **Version 2.1**
4. **Téléchargements de l'App Bundle** :
   - Upload `macartedetarot-2.1-arm64-v8a_armeabi-v7a-release-signed.aab`
   - Upload `mapping.txt` (désobscurcissement)
   - Upload `native-debug-symbols.zip` (symboles natifs)

---

## ✅ Vérification

Après upload, vérifier dans Play Console :
- ✅ **Avertissement ProGuard** : disparu
- ✅ **Avertissement symboles natifs** : disparu
- ✅ **Stack traces** : maintenant lisibles avec noms de classes/méthodes réels

---

## 📝 Notes importantes

### Conserver les fichiers de mapping
- **TOUJOURS** garder `mapping.txt` pour chaque version publiée
- Sans lui, impossible de désobscurcir les stack traces de cette version
- Recommandation : commit dans git sous `debug_symbols/vX.Y/mapping.txt`

### Symboles natifs
- Nécessaires pour déboguer les crashes dans les bibliothèques natives (.so)
- Dans notre cas : SDL2, Python, bibliothèques de médiation (AppLovin, ironSource)
- Taille importante mais optionnel (R8/ProGuard est prioritaire)

### Configuration buildozer.spec
```ini
# Activer ProGuard/R8
android.enable_proguard = True
android.proguard_mapping = mapping.txt

# Activer symboles natifs
android.enable_ndk_debug_symbols = True

# Configuration Gradle pour niveau de symboles complet
android.gradle_app_options = """
android {
    buildTypes {
        release {
            ndk {
                debugSymbolLevel 'FULL'
            }
        }
    }
}
"""
```

---

## 🔧 Dépannage

### "mapping.txt introuvable"
```bash
# Vérifier que ProGuard est bien activé
grep "android.enable_proguard" buildozer.spec

# Si absent, ajouter dans buildozer.spec :
android.enable_proguard = True
android.proguard_mapping = mapping.txt

# Rebuild
buildozer android clean
buildozer android release
```

### "native-debug-symbols.zip introuvable"
```bash
# Vérifier la config gradle
grep "debugSymbolLevel" buildozer.spec

# Si absent, ajouter la config gradle_app_options (voir ci-dessus)

# Rebuild
buildozer android clean
buildozer android release
```

### Répertoires de build différents
Si les chemins sont différents, chercher :
```bash
find .buildozer -name "mapping.txt" -type f
find .buildozer -name "native-debug-symbols.zip" -type f
```

---

## 📚 Références

- [ProGuard/R8 sur Play Console](https://developer.android.com/studio/build/shrink-code)
- [Symboles de débogage natifs](https://developer.android.com/studio/build/gradle-tips#native-symbols)
- [Analyser les crashs](https://developer.android.com/topic/performance/vitals/crash)
