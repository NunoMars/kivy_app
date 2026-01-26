# Points Clés - Maintenance et Évolution

## 🎯 Architecture

### Séparation des responsabilités
```
daily_ritual.py      → Logique métier (streak, intention, verrouillage)
screens.py           → Interface utilisateur (CardScreen, IntentionScreen, ResponseScreen)
main.py              → Initialisation et coordination
i18n/lang/*.json     → Traductions
```

### Flux de données
```
TarotApp.__init__()
  ↓
DailyRitualManager (daily_ritual.json)
  ↓
CardScreen.draw_card() → vérifie can_draw_today()
  ↓
IntentionScreen → enregistre set_intention()
  ↓
CardScreen.perform_card_draw() → enregistre record_draw()
  ↓
ResponseScreen → personnalise message via get_intention()
```

---

## 🔧 Paramètres modifiables

### Durées d'animation
**Fichier** : `screens.py`

```python
# CardScreen._transition_to_intention_screen()
Animation(opacity=0, duration=0.7)  # Modifier ici pour ajuster

# IntentionScreen._on_validate()
Clock.schedule_once(self._perform_draw, 0.8)  # Délai avant tirage

# ResponseScreen (via perform_card_draw)
Animation(opacity=1, duration=0.8)  # Fade in de la carte
```

**Recommandation** : Garder entre 600ms et 900ms pour l'ambiance rituelle.

---

### Heure de notification
**Fichier** : `main.py`

```python
def _seconds_until_today_11(self):
    target = now.replace(hour=11, minute=0, second=0, microsecond=0)
    # Modifier l'heure ici (actuellement 11h)
```

**Note** : Ajouter une option dans les paramètres utilisateur pour personnalisation future.

---

### Messages de notification
**Fichier** : `i18n/lang/*.json`

```json
"daily_reminder": "Une carte vous attend aujourd'hui ✨"
```

**Personnalisation** : Créer des variations aléatoires pour éviter la monotonie :
```python
reminders = [
    "Une carte vous attend aujourd'hui ✨",
    "Votre guidance quotidienne est prête 🌙",
    "Le tarot a un message pour vous 🔮"
]
body = random.choice(reminders)
```

---

## 📊 Métriques à surveiller

### KPIs de rétention
```python
# Ajouter dans daily_ritual.py si besoin d'analytics

def get_retention_metrics(self) -> dict:
    """Retourne des métriques pour analytics."""
    return {
        "current_streak": self.get_streak(),
        "best_streak": self.get_best_streak(),
        "total_draws": self.get_total_draws(),
        "days_since_first_draw": ...,  # À calculer
        "average_draws_per_week": ...,  # À calculer
    }
```

### Intentions les plus choisies
```python
# Dans daily_ritual.py, ajouter un compteur

self.data["intention_stats"] = {
    "love": 15,
    "work": 8,
    "inner": 12,
    "custom": 5
}

def record_draw(self, card_name: Optional[str] = None) -> None:
    # ... code existant ...
    intention = self.data.get("today_intention")
    if intention:
        stats = self.data.get("intention_stats", {})
        stats[intention] = stats.get(intention, 0) + 1
        self.data["intention_stats"] = stats
```

---

## 🎨 Personnalisation visuelle

### Couleurs des badges
**Fichier** : `screens.py` → `CardScreen._update_daily_badge()`

```python
# Badge avant tirage (or)
self.daily_badge.color = [1, 0.85, 0.2, 1]

# Badge après tirage (vert)
self.daily_badge.color = [0.2, 1, 0.4, 1]
```

**Suggestions** :
- Violet mystique : `[0.6, 0.3, 0.8, 1]`
- Or profond : `[0.8, 0.6, 0.1, 1]`
- Bleu nuit : `[0.2, 0.4, 0.8, 1]`

---

### Emojis des intentions
**Fichier** : `i18n/lang/*.json`

```json
"intention_love": "💕 Amour & Relations",
"intention_work": "💼 Travail & Carrière",
"intention_inner": "🌟 Développement intérieur",
"intention_custom": "✍️ Question personnelle"
```

**Alternatives** :
- Love : 💖, ❤️, 💝
- Work : 💻, 📈, 🎯
- Inner : 🧘, 🕉️, ☯️
- Custom : 📝, 💭, 🔍

---

## 🚀 Évolutions possibles

### 1. Historique des tirages
```python
# Dans daily_ritual.py

self.data["history"] = [
    {
        "date": "2026-01-26",
        "card": "major_00",
        "intention": "love",
        "intention_text": None
    },
    # ...
]

def add_to_history(self, card_name: str):
    history = self.data.get("history", [])
    history.append({
        "date": self._today_str(),
        "card": card_name,
        "intention": self.data.get("today_intention"),
        "intention_text": self.data.get("today_intention_text")
    })
    # Limiter à 30 derniers jours
    self.data["history"] = history[-30:]
```

**Nouvelle screen** : `HistoryScreen` pour afficher les cartes passées.

---

### 2. Heure de notification personnalisée
```python
# Dans daily_ritual.py

self.data["notification_hour"] = 11  # Par défaut

def set_notification_hour(self, hour: int):
    """Permet à l'utilisateur de choisir l'heure."""
    self.data["notification_hour"] = max(0, min(23, hour))
    self._save_data()
```

**UI** : Ajouter un slider dans AboutScreen ou nouveau SettingsScreen.

---

### 3. Badges de récompense
```python
# Dans daily_ritual.py

MILESTONES = {
    7: {"name": "Semaine de guidance", "emoji": "🌟"},
    30: {"name": "Mois de sagesse", "emoji": "🌙"},
    100: {"name": "Cent jours de lumière", "emoji": "✨"},
}

def check_milestones(self) -> Optional[dict]:
    """Retourne le badge si milestone atteint."""
    streak = self.get_streak()
    if streak in MILESTONES:
        return MILESTONES[streak]
    return None
```

**Popup** : Afficher une célébration quand milestone atteint.

---

### 4. Journal de réflexion
```python
# Dans daily_ritual.py

def add_reflection(self, date: str, text: str):
    """Permet d'ajouter une note personnelle."""
    reflections = self.data.get("reflections", {})
    reflections[date] = text
    self.data["reflections"] = reflections
    self._save_data()
```

**UI** : Ajouter un bouton "✍️ Note" sur ResponseScreen.

---

### 5. Mode sombre
```python
# Dans main.py, ajouter un paramètre

self.dark_mode = self.cfg.get("dark_mode", False)

# Dans screens.py, adapter les couleurs
if app.dark_mode:
    bg_color = [0.1, 0.1, 0.15, 1]
else:
    bg_color = [0.2, 0.1, 0.3, 1]
```

---

## 🔒 Sécurité et confidentialité

### Données stockées localement
- ✅ Aucun envoi au serveur
- ✅ Pas d'identifiants personnels
- ✅ Questions personnalisées stockées localement uniquement

### RGPD
- ✅ Pas de collecte de données personnelles
- ✅ Pas de tracking comportemental
- ✅ Notifications optionnelles (permissions Android)

### Suppression des données
**Pour l'utilisateur** :
```bash
# Supprimer toutes les données du rituel
rm ~/.kivy/app_data/daily_ritual.json
```

**Futur bouton** : Ajouter "Réinitialiser le rituel" dans AboutScreen.

---

## 🐛 Débogage

### Activer les logs détaillés
```python
# Dans daily_ritual.py

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Utiliser dans les méthodes
logger.debug(f"Tirage enregistré: {card_name}, streak={self.get_streak()}")
```

### Tester sans attendre 24h
```python
# Mode debug : simuler changement de jour

def _today_str_debug(self) -> str:
    """Version debug pour tester."""
    import os
    override = os.environ.get("DEBUG_DATE")
    if override:
        return override
    return datetime.date.today().isoformat()

# Utiliser :
# export DEBUG_DATE="2026-01-27"
# python main.py
```

---

## 📚 Ressources

### Documentation Kivy
- Animations : https://kivy.org/doc/stable/api-kivy.animation.html
- Screen Manager : https://kivy.org/doc/stable/api-kivy.uix.screenmanager.html
- Properties : https://kivy.org/doc/stable/api-kivy.properties.html

### Patterns utilisés
- **Singleton** : `DailyRitualManager` (une seule instance via `App.ritual_manager`)
- **Observer** : `fbind()` pour réactivité des fonts et traductions
- **State Machine** : Transitions d'écrans via `ScreenManager`

---

## ⚠️ Points d'attention

### Performance
- ✅ Animations légères (opacity uniquement)
- ✅ Pas de calculs lourds dans les transitions
- ✅ JSON simple et petit (<1 KB)

### Compatibilité
- ✅ Android 5.0+ (API 21+)
- ✅ iOS non testé mais code compatible
- ✅ Desktop (Windows/Linux/macOS) fonctionnel

### Maintenance
- ✅ Code commenté en français
- ✅ Nommage explicite
- ✅ Structure modulaire
- ✅ Pas de dépendances externes supplémentaires

---

*Document créé le 26 janvier 2026*
*Pour toute question : consulter RITUAL_QUOTIDIEN_IMPLEMENTATION.md*
