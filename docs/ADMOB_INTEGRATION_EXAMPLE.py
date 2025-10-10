"""
EXEMPLE D'INTÉGRATION ADMOB DANS main.py
========================================

Ce fichier montre comment intégrer le système AdMob JSON dans ton main.py existant.
Tu peux copier/coller les sections pertinentes.
"""

# ============================================================================
# 1. IMPORTS (en haut de main.py)
# ============================================================================

# ... tes imports existants ...
from ads_manager import load_config, AdsManager, maybe_fetch_remote_config


# ============================================================================
# 2. CLASSE APP - Méthode build()
# ============================================================================

class TarotApp(App):
    def build(self):
        """Build l'application avec support AdMob"""
        
        # Charger la configuration JSON
        self.cfg = load_config()
        Logger.info(f"TarotApp: Config loaded - Test mode: {self.cfg.get('ads_test_mode')}")
        
        # Optionnel : récupérer config à distance
        maybe_fetch_remote_config(self.cfg)
        
        # Initialiser le gestionnaire de pubs
        self.ads = AdsManager(self.cfg)
        
        # ... ton code existant de build ...
        self.root = RootScreen()
        return self.root


# ============================================================================
# 3. ÉCRAN DE TIRAGE - CardScreen
# ============================================================================

class CardScreen(Screen):
    def draw_card(self, instance):
        """Tire une carte et gère la publicité"""
        
        # ... ton code de tirage existant ...
        drawn_card = random.choice(list(cards_signification.keys()))
        drawn_state = random.choice(["a l'endroit", "a l'envers"])
        
        print(f"Carte tirée: {drawn_card} - {drawn_state}")
        
        # ===== INTÉGRATION ADMOB =====
        # Option 1 : Laisser AdsManager gérer automatiquement
        app = App.get_running_app()
        if hasattr(app, 'ads'):
            app.ads.on_card_drawn()  # Affiche interstitiel selon fréquence config
        # =============================
        
        # Afficher l'écran de réponse
        if self.manager:
            response_screen = self.manager.get_screen("response_screen")
            response_screen.setup_card(drawn_card, drawn_state)
            self.manager.current = "response_screen"


# ============================================================================
# 4. ALTERNATIVE - Contrôle Manuel des Pubs
# ============================================================================

class CardScreen(Screen):
    def draw_card(self, instance):
        """Alternative avec contrôle manuel de la pub"""
        
        # ... ton code de tirage ...
        drawn_card = random.choice(list(cards_signification.keys()))
        drawn_state = random.choice(["a l'endroit", "a l'envers"])
        
        # ===== CONTRÔLE MANUEL =====
        app = App.get_running_app()
        
        # Incrémenter ton propre compteur si tu veux
        if not hasattr(self, '_draw_count'):
            self._draw_count = 0
        self._draw_count += 1
        
        # Afficher interstitiel tous les X tirages
        ads_frequency = app.cfg.get('ads_frequency', 3)
        if self._draw_count % ads_frequency == 0:
            if hasattr(app, 'ads'):
                app.ads.show_interstitial()
        # ===========================
        
        # Continue normalement
        if self.manager:
            response_screen = self.manager.get_screen("response_screen")
            response_screen.setup_card(drawn_card, drawn_state)
            self.manager.current = "response_screen"


# ============================================================================
# 5. BANNIÈRE - Afficher/Masquer (Optionnel)
# ============================================================================

class ResponseScreen(Screen):
    def on_enter(self):
        """Afficher la bannière quand on entre sur cet écran"""
        super().on_enter()
        
        app = App.get_running_app()
        if hasattr(app, 'ads'):
            app.ads.show_banner()
    
    def on_leave(self):
        """Masquer la bannière quand on quitte cet écran"""
        super().on_leave()
        
        app = App.get_running_app()
        if hasattr(app, 'ads'):
            app.ads.hide_banner()


# ============================================================================
# 6. REMPLACEMENT DE L'ANCIEN SYSTÈME DE PUB
# ============================================================================

# SI tu avais un ancien système de popup (AdsPopup), tu peux le remplacer :

# ANCIEN CODE (à supprimer) :
"""
if should_show_ad():
    popup = AdsPopup(on_close_callback=show_response_screen)
    popup.open()
else:
    show_response_screen()
"""

# NOUVEAU CODE (AdMob) :
"""
def draw_card(self, instance):
    # ... tirage ...
    
    # Notifier AdMob
    app = App.get_running_app()
    if hasattr(app, 'ads'):
        app.ads.on_card_drawn()
    
    # Afficher directement la réponse (AdMob gère l'interstitiel)
    show_response_screen()
"""


# ============================================================================
# 7. DEBUG - Vérifier la config chargée
# ============================================================================

class TarotApp(App):
    def build(self):
        self.cfg = load_config()
        
        # DEBUG : afficher la config
        import json
        print("=" * 60)
        print("📋 CONFIGURATION CHARGÉE:")
        print(json.dumps(self.cfg, indent=2, ensure_ascii=False))
        print("=" * 60)
        
        self.ads = AdsManager(self.cfg)
        
        # ... reste du code ...


# ============================================================================
# 8. EXEMPLE COMPLET MINIMAL
# ============================================================================

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from ads_manager import load_config, AdsManager, maybe_fetch_remote_config
import random

class CardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        self.label = Label(text="Appuyez pour tirer une carte")
        layout.add_widget(self.label)
        
        btn = Button(text="Tirer une carte", size_hint=(1, 0.2))
        btn.bind(on_press=self.draw_card)
        layout.add_widget(btn)
        
        self.add_widget(layout)
    
    def draw_card(self, instance):
        cards = ["Le Bateleur", "La Papesse", "L'Impératrice"]
        card = random.choice(cards)
        self.label.text = f"Carte tirée : {card}"
        
        # Notifier AdMob
        app = App.get_running_app()
        if hasattr(app, 'ads'):
            app.ads.on_card_drawn()


class TarotApp(App):
    def build(self):
        # Config AdMob
        self.cfg = load_config()
        self.ads = AdsManager(self.cfg)
        
        # UI
        sm = ScreenManager()
        sm.add_widget(CardScreen(name='card'))
        return sm


if __name__ == '__main__':
    TarotApp().run()


# ============================================================================
# 9. NOTES IMPORTANTES
# ============================================================================

"""
ORDRE D'EXÉCUTION :
1. load_config() charge config.default.json + config.json (si existe)
2. maybe_fetch_remote_config() télécharge config à distance (optionnel, async)
3. AdsManager initialise AdMob avec la config
4. on_card_drawn() ou show_interstitial() affiche les pubs

FICHIERS DE CONFIG :
- config.default.json : embarqué dans l'APK (ne change jamais sans rebuild)
- /data/data/org.tarot.macartedetarot/files/config.json : modifiable sans rebuild

PRIORITÉ :
config.json (user) > config.default.json (embarqué) > valeurs codées en dur

TEST vs PROD :
- Test : "ads_test_mode": true  → IDs Google de test
- Prod : "ads_test_mode": false → Tes vrais IDs AdMob

FRÉQUENCE RECOMMANDÉE :
- Trop agressif : 1-2 tirages (mauvaise UX)
- Acceptable : 3-4 tirages
- Optimal : 5-7 tirages (meilleure UX, moins de revenus)

BANNIÈRE vs INTERSTITIEL :
- Bannière : toujours visible (moins intrusif, moins de revenus)
- Interstitiel : plein écran entre actions (plus intrusif, plus de revenus)
- Recommandation : les deux, mais interstitiel peu fréquent

PLATEFORME :
AdMob fonctionne UNIQUEMENT sur Android.
Sur desktop/iOS, les pubs sont automatiquement désactivées.
"""
