# Corrections Build v1.6.1

## 🔧 Problèmes identifiés et corrigés :

### 1. **Gradle Build Failure**
- **Cause** : Versions AndroidX trop récentes (1.7.1/1.6.2)
- **Solution** : Revenir aux versions compatibles (1.6.0/1.5.7)

### 2. **Orientation Landscape non désirée**
- **Cause** : Quand orientation commenté, buildozer utilise `landscape`
- **Solution** : Remettre `orientation = portrait` explicitement

### 3. **Conflits de dépendances**
- **Cause** : Mélange androidx + support-v4
- **Solution** : Retirer support-v4, garder seulement androidx

## ✅ Modifications appliquées :

```ini
# Revenir à portrait explicite
orientation = portrait

# Versions AndroidX compatibles
android.gradle_dependencies = androidx.annotation:annotation:1.6.0, androidx.fragment:fragment:1.5.7

# Version incrémentée
version = 1.6.1
```

## 🎯 Stratégie pour grands écrans :

Au lieu de forcer `orientation = all` (non supporté), on utilise :
- `android.allow_resize = True`
- `android.resizeableActivity = True`

Ces options permettent le redimensionnement sur tablettes/pliables tout en gardant portrait par défaut.

## 📱 Test recommandé :

1. Build réussi avec portrait
2. Test sur tablette pour vérifier redimensionnement
3. Si OK, peut augmenter versions AndroidX graduellement
