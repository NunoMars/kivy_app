# Résolution des avertissements Google Play Console

**Date**: 6 février 2026  
**AAB**: macartedetarot-2.41-arm64-v8a-release-16KB-signed.aab  

## Avertissements reçus lors de l'upload

### 1. ⚠️ Fichier de désobscurcissement manquant (ProGuard/R8)

**Message**:  
> Aucun fichier de désobscurcissement n'est associé à cet App Bundle. Si vous utilisez du code obscurci (R8/ProGuard), le fait d'importer un fichier de désobscurcissement simplifiera l'analyse et le débogage des plantages et des ANR.

**Statut**: ⚠️ **Optionnel mais recommandé**

### 2. ⚠️ Symboles de débogage natifs manquants

**Message**:  
> Cet App Bundle contient du code natif, et vous n'avez pas importé de symboles de débogage. Nous vous recommandons d'importer un fichier de symboles afin de faciliter l'analyse et le débogage des plantages et des erreurs ANR.

**Statut**: ⚠️ **Optionnel mais recommandé**

## Impact et recommandations

### Ces avertissements sont-ils bloquants ?

**NON** ❌ - Votre AAB peut être uploadé et publié sans ces fichiers.

### Pourquoi ces fichiers sont-ils importants ?

| Fichier | Utilité | Impact si absent |
|---------|---------|------------------|
| **mapping.txt** (ProGuard) | Permet de désobscurquer les stack traces Java | Stack traces difficiles à lire avec noms de classes obscurcis |
| **Symboles natifs** (.so debug) | Symbole les bibliothèques natives (C/C++) | Crashs natifs difficiles à debugger |

### Recommandation

Pour **cette version 2.41** (déjà uploadée) :
- ✅ **Publier comme ça** - L'AAB est fonctionnel et conforme (16KB ✅)
- 📊 **Surveiller les crashs** dans les premiers jours
- 🔍 **Si taux de crash élevé** → Générer les symboles pour la prochaine version

Pour **les prochaines versions** :
- 🔧 **Configuration modifiée** pour générer automatiquement ces fichiers
- 📤 **Uploader systématiquement** les fichiers de debug avec chaque AAB

## Solution 1: Pour l'AAB actuel (version 2.41)

### Option A: Publier sans les symboles (RECOMMANDÉ pour cette version)

**Raison**: Les symboles nécessitent un rebuild complet (20-30 minutes), et votre application :
- ✅ A déjà été testée et fonctionne
- ✅ Est conforme aux exigences 16KB
- ✅ Est signée correctement
- ⚠️ Les crashs natifs sont rares dans les apps Kivy bien testées

**Action**: Cliquer sur "Continuer" dans Google Play Console

### Option B: Générer les symboles après upload (si crashs détectés)

Si vous voyez beaucoup de crashs natifs dans les rapports :

1. Extraire les bibliothèques avec debug info de votre build local
2. Créer un ZIP avec les .so unstripped
3. Uploader via Google Play Console

**Commandes**:
```bash
cd /home/loupy/kivy_app
mkdir -p native-debug-symbols/lib/arm64-v8a

# Copier les .so avec symboles (avant stripping)
cp .buildozer/android/platform/build-arm64-v8a/build/libs_collections/macartedetarot/arm64-v8a/*.so \
   native-debug-symbols/lib/arm64-v8a/

# Créer le ZIP
cd native-debug-symbols
zip -r ../native-debug-symbols-2.41.zip lib/
cd ..

# Copier sur le bureau Windows
cp native-debug-symbols-2.41.zip /mnt/c/Users/loupy/Desktop/
```

Puis dans Google Play Console : Production → Version 2.41 → Symboles de débogage natifs → Uploader

## Solution 2: Configuration pour les futures versions

### Modifications à apporter dans buildozer.spec

Le fichier [buildozer.spec](buildozer.spec) a déjà été modifié avec :

```ini
# Enable R8 minification and resource shrinking for release builds
android.gradle_app_settings = 
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
            ndk {
                debugSymbolLevel 'FULL'
            }
        }
    }
```

### Script de build automatique pour futures versions

Un script [build_with_symbols.sh](build_with_symbols.sh) a été créé pour :
1. Builder l'AAB avec les configurations correctes
2. Extraire automatiquement les symboles natifs
3. Extraire le mapping ProGuard
4. Copier tout sur le bureau Windows

**Utilisation pour la prochaine version**:
```bash
cd /home/loupy/kivy_app
./build_with_symbols.sh
```

Le script copiera sur votre bureau :
- ✅ AAB signé
- ✅ `native-debug-symbols-X.XX.zip`
- ✅ `mapping-X.XX.txt`

### Limites actuelles

⚠️ **Note importante**: La génération complète des symboles avec Gradle peut ne pas fonctionner parfaitement avec Buildozer car :
- Buildozer génère le build.gradle dynamiquement
- Le `debugSymbolLevel 'FULL'` peut être écrasé par p4a
- Les symboles sont parfois strippés avant d'être sauvegardés

**Alternative fonctionnelle**: Copier les .so avant le stripping (voir Option B ci-dessus)

## Étapes pour uploader les fichiers (si générés)

### Dans Google Play Console

1. **Accéder à la version**
   - Production → Artefacts → Version 2.41

2. **Uploader les symboles natifs**
   - Section "Symboles de débogage natifs"
   - Cliquer sur "Uploader"
   - Sélectionner `native-debug-symbols-2.41.zip`
   - ✅ Doit contenir: `lib/arm64-v8a/*.so`

3. **Uploader le mapping ProGuard**
   - Section "Fichiers de désobscurcissement"
   - Cliquer sur "Uploader le fichier ProGuard"
   - Sélectionner `mapping-2.41.txt`
   - ✅ Format standard ProGuard mapping

## Vérification post-upload

### Avec symboles
Après upload des symboles, dans la Console :
- ✅ Badge vert "Symboles de débogage disponibles"
- ✅ Badge vert "Mapping ProGuard uploadé"
- ✅ Stack traces lisibles dans les rapports de crash

### Sans symboles (situation actuelle)
- ⚠️  Avertissements présents mais non-bloquants
- ✅ Application publiable et fonctionnelle
- ⚠️  Stack traces natives obscurcies si crash

## Monitoring post-publication

### Premières 48h après publication

**Surveiller** dans Google Play Console → Qualité → Android Vitals :

1. **Taux de crash** (ANR + crashes)
   - ✅ Cible: < 0.5%
   - ⚠️  Si > 1%: Analyser les rapports

2. **Crashs natifs spécifiquement**
   - Filtrer par "Native crashes"
   - Vérifier si stack traces lisibles

3. **Distribution des crashes**
   - Par appareil (chercher pattern 16KB)
   - Par version Android

### Si problèmes détectés

**Action immédiate**:
1. Suspendre le rollout à 5-10%
2. Analyser les logs
3. Si crash natif non debuggable → Générer et uploader symboles

**Pour prochaine version**:
- Activer symboles de débogage avant build
- Inclure logging supplémentaire
- Tests sur plus d'appareils différents

## Récapitulatif

### Pour version 2.41 actuelle

| Action | Statut | Priorité |
|--------|--------|----------|
| Publier l'AAB | ✅ Prêt | **Immédiat** |
| Surveiller crashs 48h | 📊 Planifié | **Haute** |
| Uploader symboles si besoin | ⏸️  En attente | **Si nécessaire** |

### Pour futures versions

| Action | Statut | Priorité |
|--------|--------|----------|
| Utiliser `build_with_symbols.sh` | 🔧 Configuré | **Systématique** |
| Uploader symboles + mapping | 📤 Automatisé | **Systématique** |
| Tester avant publication | ✅ Process établi | **Critique** |

## Ressources

### Documentation Google
- [Symboles de débogage natifs](https://support.google.com/googleplay/android-developer/answer/9848633)
- [Désobfurcissement ProGuard](https://support.google.com/googleplay/android-developer/answer/9848633)

### Fichiers du projet
- [buildozer.spec](buildozer.spec) - Configuration modifiée
- [build_with_symbols.sh](build_with_symbols.sh) - Script automatique
- [proguard-rules.pro](proguard-rules.pro) - Règles R8/ProGuard

### Commandes utiles

```bash
# Vérifier si AAB contient symboles de debug
unzip -l macartedetarot-2.41-arm64-v8a-release-16KB-signed.aab | grep -E "DWARF|debug"

# Lister les .so dans l'AAB
unzip -l macartedetarot-2.41-arm64-v8a-release-16KB-signed.aab | grep "\.so$"

# Vérifier taille des .so (avec debug = plus gros)
unzip -q macartedetarot-2.41-arm64-v8a-release-16KB-signed.aab
ls -lh base/lib/arm64-v8a/*.so
```

---

## ✅ Conclusion

**Pour cette version 2.41**:
- Publier l'AAB tel quel ✅
- Avertissements = informatifs, non-bloquants ✅
- Conformité 16KB confirmée ✅
- Signature validée ✅

**Monitoring**: Surveiller crashs 48h après publication

**Prochaines versions**: Utiliser `build_with_symbols.sh` pour générer automatiquement tous les fichiers nécessaires.

---

**Mise à jour**: 6 février 2026  
**AAB prêt**: ✅ Sur le bureau Windows  
**Action**: Uploader sur Google Play Console
