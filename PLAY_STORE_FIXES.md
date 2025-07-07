# Corrections Play Store - Version 1.6

## ✅ Corrections appliquées automatiquement :

### 1. **SDK AndroidX mis à jour**
- `androidx.annotation:annotation` : 1.0.0 → 1.7.1
- `androidx.fragment:fragment` : 1.0.0 → 1.6.2
- Supprime les avertissements de versions obsolètes

### 2. **Support des écrans larges**
- Orientation changée de `portrait` → `all`
- Permet l'utilisation sur tablettes et pliables
- Prépare pour Android 16+ (ignore les restrictions)

### 3. **Version incrémentée**
- Version 1.5 → 1.6
- Code version : 1021105 → 1021106

## ⚠️ À surveiller (pas bloquant) :

### **Alignement bibliothèques natives 16ko**
- Problème lié à python-for-android/Kivy
- Solution : attendre mise à jour upstream
- Impact : appareils Android 14+ très récents uniquement

## 🚀 Prochaines étapes :

1. Commit et push ces changements
2. Attendre build GitHub Actions
3. Tester la nouvelle version
4. Publier mise à jour sur Play Store

## 📱 Tests recommandés :

- Rotation écran (portrait/paysage)
- Test sur tablette/grand écran
- Vérifier UI dans toutes orientations
