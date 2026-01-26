# ⚡ Quick Reference - Rituel Quotidien

## 📦 Fichiers Créés
- `daily_ritual.py` - Logique métier
- `RITUAL_QUOTIDIEN_IMPLEMENTATION.md` - Doc complète
- `GUIDE_TEST_RITUEL.md` - Tests
- `MAINTENANCE_RITUEL.md` - Maintenance
- `README_RITUEL.md` - Résumé
- `ARCHITECTURE_RITUEL.md` - Diagrammes
- `CHANGELOG_RITUEL.md` - Historique
- `QUICK_REFERENCE_RITUEL.md` - Ce fichier

## 🔧 Fichiers Modifiés
- `main.py` - Init ritual_manager + IntentionScreen
- `screens.py` - CardScreen, IntentionScreen, ResponseScreen
- `i18n/lang/fr.json` - +18 clés
- `i18n/lang/en.json` - +18 clés
- `i18n/lang/es.json` - +18 clés
- `i18n/lang/pt.json` - +18 clés

## ⚙️ Configuration Rapide

### Changer l'heure de notification
`main.py:510` → `hour=11` (modifier 11)

### Modifier durée animations
`screens.py:285` → `duration=0.7` (CardScreen → Intention)
`screens.py:1762` → `0.8` (délai avant tirage)
`screens.py:423` → `duration=0.8` (fade ResponseScreen)

### Changer couleurs badge
`screens.py:329` → `[1, 0.85, 0.2, 1]` (or avant tirage)
`screens.py:333` → `[0.2, 1, 0.4, 1]` (vert après tirage)

## 🧪 Test Express (2 min)
```bash
# 1. Lancer
python main.py

# 2. Tirer une carte (intention → attendre → voir révélation)

# 3. Vérifier badge "Jour 1 de guidance"

# 4. Tenter second tirage → popup bloquant

# 5. Vérifier JSON
cat ~/.kivy/app_data/daily_ritual.json
```

## 🐛 Debug Rapide

### Badge ne s'affiche pas
Vérifier `on_enter()` ligne 338 de screens.py

### Streak incorrect
Vérifier `reset_today_if_needed()` ligne 227 de main.py

### Notifications absentes
Vérifier permissions Android POST_NOTIFICATIONS

### Réinitialiser
```bash
rm ~/.kivy/app_data/daily_ritual.json
```

## 📍 Points d'Entrée Code

```python
# Vérifier verrouillage
CardScreen.draw_card() # screens.py:217

# Enregistrer intention
IntentionScreen._on_validate() # screens.py:1754

# Enregistrer tirage
CardScreen.perform_card_draw() # screens.py:390

# Calculer streak
DailyRitualManager.record_draw() # daily_ritual.py:134
```

## 📊 Structure JSON
```json
{
  "last_draw_date": "2026-01-26",
  "current_streak": 5,
  "best_streak": 12,
  "total_draws": 47,
  "today_intention": "love",
  "today_intention_text": null,
  "today_card": "major_00",
  "draw_completed": true,
  "last_notification_date": "2026-01-26"
}
```

## ✅ Checklist Validation

- [ ] Badge visible et changement couleur OK
- [ ] Tirage bloqué après premier du jour
- [ ] Popup explicatif avec streak
- [ ] IntentionScreen obligatoire
- [ ] Message personnalisé selon intention
- [ ] Transitions fluides (700-800ms)
- [ ] Streak +1 si jour consécutif
- [ ] Streak reset si jour manqué
- [ ] Notification max 1/jour
- [ ] Traductions FR/EN/ES/PT OK
- [ ] Aucune régression AdMob
- [ ] daily_ritual.json créé
- [ ] Persistance après redémarrage

## 🔗 Documentation

| Fichier | Contenu |
|---------|---------|
| README_RITUEL.md | Résumé exécutif |
| IMPLEMENTATION.md | Doc technique complète |
| GUIDE_TEST.md | 10 scénarios de test |
| MAINTENANCE.md | Évolutions futures |
| ARCHITECTURE.md | Diagrammes |
| CHANGELOG.md | Historique |

## 🚀 Commandes Utiles

```bash
# Afficher JSON formaté
cat ~/.kivy/app_data/daily_ritual.json | python -m json.tool

# Simuler jour spécifique
# Éditer manually le JSON: "last_draw_date": "2026-01-20"

# Compter lignes de code ajoutées
wc -l daily_ritual.py

# Rechercher TODOs
grep -r "TODO" *.py *.md
```

## 📞 Support

**Erreur ?** → Voir GUIDE_TEST_RITUEL.md section "Problèmes connus"
**Évolution ?** → Voir MAINTENANCE_RITUEL.md section "Évolutions possibles"
**Architecture ?** → Voir ARCHITECTURE_RITUEL.md

---

*v2.x - 26 janvier 2026*
