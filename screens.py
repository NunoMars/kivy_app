# -*- coding: utf-8 -*-
"""
Module des écrans pour l'application Kivy.
Contient les classes d'écrans (RootScreen, CardScreen, ResponseScreen) et leurs dépendances.
"""

from __future__ import annotations

import os
import json
import random

# Kivy imports
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation

# Local modules
from i18n_loader import tr, get_system_language
from i18n_loader import get_cards_signification  # get_cards_signification(lang: str) -> dict

# Popups
from popups import LoadingPopup, FullScreenCardPopup, MmeTChatPopup, AdsPopup

# Billing
try:
    from billing import InAppPurchaseManager
except ImportError:
    InAppPurchaseManager = None

# Constants and globals
READING_COUNT = 0

# Use the central language detection from translations.py (imported above)
CURRENT_LANG = get_system_language()

# Platform detection
try:
    import platform
    platform_name = platform.system().lower()
except Exception:
    platform_name = "unknown"

# Mme T constants
DEFAULT_MME_T_SPACE = "https://loupy222-mme-t.hf.space"
MME_T_BACKEND_URL = os.environ.get("MME_T_BACKEND_URL", DEFAULT_MME_T_SPACE)
MME_T_DEFAULT_MODEL = os.environ.get("MME_T_DEFAULT_MODEL", "gpt-3.5-turbo")


# -------------------------
# Lang resolution utilities
# -------------------------
def _normalize_lang(code: str) -> str:
    if not code:
        return "en"
    code = code.lower().replace("_", "-")
    # map common variants to our filenames (fr, en, pt, es, etc.)
    if code.startswith("fr"):
        return "fr"
    if code.startswith("en"):
        return "en"
    if code.startswith("pt"):
        return "pt"
    if code.startswith("es"):
        return "es"
    # fallback
    return code[:2] if len(code) >= 2 else "en"


def resolve_lang() -> str:
    """
    Ordre de priorité:
    1) App.cfg['force_lang'] (si présent),
    2) ENV APP_LANG,
    3) get_system_language(),
    4) 'en'
    """
    lang_forced = None
    try:
        app = App.get_running_app()
        if hasattr(app, "cfg"):
            lang_forced = app.cfg.get("force_lang") or app.cfg.get("language")
    except Exception:
        pass
    env_lang = os.environ.get("APP_LANG")

    chosen = lang_forced or env_lang or get_system_language() or "en"
    return _normalize_lang(chosen)


def should_show_ad():
    """Détermine si une publicité doit être affichée selon la fréquence configurée."""
    try:
        app = App.get_running_app()
        if not hasattr(app, 'cfg'):
            return False

        cfg = app.cfg
        if not cfg.get('ads_enabled', False):
            return False

        frequency = cfg.get('ads_frequency', 5)  # Toutes les 5 lectures par défaut
        global READING_COUNT
        READING_COUNT += 1
        return READING_COUNT % frequency == 0
    except Exception:
        return False


class RootScreen(ScreenManager):
    """Gestionnaire d'écrans"""

    def __init__(self, **kwargs):
        super(RootScreen, self).__init__(**kwargs)
        print("RootScreen initialisé")


class CardScreen(Screen):
    """Écran principal responsable du tirage."""

    def __init__(self, **kwargs):
        super(CardScreen, self).__init__(**kwargs)
        print("CardScreen créé")

        self.loading_popup = None

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        with layout.canvas.before:
            Color(0.2, 0.1, 0.3, 1)
            self.bg = Rectangle(pos=layout.pos, size=layout.size)
            if os.path.exists("tarot_img/bg.jpg"):
                self.bg.source = "tarot_img/bg.jpg"
        layout.bind(pos=self.update_bg, size=self.update_bg)

        self.title_label = Label(
            text=tr("app_title"),
            font_size="22sp",
            color=[0.9, 0.7, 0.3, 1],
            size_hint_y=0.15,
            bold=True,
            halign='center',
            valign='middle',
        )
        self.title_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.92, None)))
        layout.add_widget(self.title_label)

        card_container = FloatLayout(size_hint_y=0.7)
        self.card_image = Image(
            source="tarot_img/Back.jpg",
            size_hint=(0.8, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
        )
        self.draw_button = Button(
            text="",
            background_color=[0, 0, 0, 0],
            size_hint=(0.8, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
        )
        self.draw_button.bind(on_press=self.draw_card)
        card_container.add_widget(self.card_image)
        card_container.add_widget(self.draw_button)
        layout.add_widget(card_container)

        self.instructions_label = Label(
            text=tr("draw_instruction"),
            font_size="18sp",
            color=[0.7, 0.5, 0.3, 1],
            size_hint_y=0.15,
            halign='center',
            valign='middle',
        )
        self.instructions_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        layout.add_widget(self.instructions_label)

        self.ad_banner = Label(
            text=tr("crystals_ad"),
            font_size="16sp",
            color=[1, 0.8, 0.2, 1],
            size_hint_y=0.08,
            halign='center',
            valign='middle',
        )
        self.ad_banner.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        self.ad_banner.opacity = 0
        layout.add_widget(self.ad_banner)

        self.add_widget(layout)

    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def draw_card(self, _instance):
        print("=== NOUVEAU TIRAGE ===")

        click_anim = Animation(opacity=0.3, duration=0.1)
        click_anim += Animation(opacity=1, duration=0.1)
        click_anim.start(self.draw_button)

        self.loading_popup = LoadingPopup()
        self.loading_popup.open()

        Clock.schedule_once(self.perform_card_draw, 4)

    def perform_card_draw(self, _dt):
        try:
            # Charge le bundle de la langue active (avec fallback interne du loader)
            lang = resolve_lang()
            try:
                cards_signification = get_cards_signification(lang) or {}
            except Exception as e:
                print(f"⚠️ get_cards_signification failed for '{lang}': {e}")
                # ultime fallback: tente EN
                try:
                    cards_signification = get_cards_signification("en") or {}
                except Exception:
                    cards_signification = {}

            try:
                cards = list(cards_signification.keys()) if isinstance(cards_signification, dict) else []
            except Exception:
                cards = []
            print(f"DEBUG LANG: {lang}")
            print(f"DEBUG: signification keys count = {len(cards)} | first keys: {cards[:5]}")

            # Fallback vers les fichiers si nécessaire
            if not cards:
                try:
                    maj_dir = os.path.join(os.path.dirname(__file__), "tarot_img", "MajorArcanaCards")
                    if not os.path.exists(maj_dir):
                        maj_dir = os.path.join(os.path.dirname(__file__), "tarot_img")
                    files = [f for f in os.listdir(maj_dir) if os.path.isfile(os.path.join(maj_dir, f))]
                    cards = [os.path.splitext(f)[0] for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
                    print(f"⚠️ Fallback cards from files: {len(cards)} found")
                except Exception as e:
                    print(f"⚠️ Impossible de lister MajorArcanaCards: {e}")
                    cards = []

            if not cards:
                print("✗ Aucun nom de carte disponible pour le tirage (cards vide). Annulation.")
                if self.loading_popup:
                    try:
                        self.loading_popup.dismiss()
                    except Exception:
                        pass
                return

            # Nombre de cartes à tirer (env)
            try:
                count = int(os.environ.get("TAROT_DRAW_COUNT", "3"))
            except Exception:
                count = 3
            count = max(1, min(4, count))

            drawn_cards = []
            remaining = list(cards)
            for _ in range(count):
                if not remaining:
                    remaining = list(cards)
                card = random.choice(remaining)
                remaining.remove(card)
                state = random.choice(["droite", "a l'envers"])
                state_json = "upright" if state in ["droite", "right"] else "reversed"
                drawn_cards.append((card, state_json))

            print(f"Disponibles pour tirage: {len(cards)} cartes")
            if not drawn_cards:
                print("✗ Aucune carte tirée — annulation du tirage")
                if self.loading_popup:
                    try:
                        self.loading_popup.dismiss()
                    except Exception:
                        pass
                return

            drawn_card, drawn_state = drawn_cards[0]

            # Stocker le tirage complet sur l'app
            try:
                app = App.get_running_app()
                app.last_drawn_cards = drawn_cards
            except Exception:
                pass

            print(f"Cartes tirées: {drawn_cards}")
            # Note: should_show_ad() incrémente READING_COUNT. On loggue le compteur courant.
            print(f"📊 Lecture #{READING_COUNT}")

            if self.loading_popup:
                self.loading_popup.dismiss()

            app = App.get_running_app()
            if hasattr(app, "ads"):
                app.ads.on_card_drawn()

            def _show_response_screen(*_args):
                if self.manager:
                    response_screen = self.manager.get_screen("response_screen")
                    response_screen.setup_card(drawn_card, drawn_state)
                    if hasattr(response_screen, "set_full_draw"):
                        try:
                            response_screen.set_full_draw(drawn_cards)
                        except Exception:
                            pass
                    self.manager.current = "response_screen"

            if should_show_ad():
                print("🎯 Affichage d'une grande publicité interstitielle maison")
                self.ads_popup = AdsPopup(on_close_callback=_show_response_screen)
                self.ads_popup.bind(on_dismiss=lambda *_: setattr(self, "ads_popup", None))
                self.ads_popup.open()
            else:
                _show_response_screen()

        except Exception as exc:
            print(f"Erreur tirage: {exc}")
            if self.loading_popup:
                self.loading_popup.dismiss()

    def on_enter(self, *args):
        print("Entrée sur CardScreen")


class ResponseScreen(Screen):
    """Écran de réponse avec image cliquable"""

    def __init__(self, **kwargs):
        super(ResponseScreen, self).__init__(**kwargs)

        self.current_card_name = ""
        self.current_card_state = ""
        self.current_card_image_path = "tarot_img/Back.jpg"

        self.typewriter_event = None
        self.typewriter_full_text = ""
        self.typewriter_index = 0
        self.chat_popup = None

        from kivy.uix.scrollview import ScrollView

        main_layout = BoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(15), dp(20), dp(15)],
            spacing=dp(6),
        )

        # Background
        with main_layout.canvas.before:
            Color(0.2, 0.1, 0.3, 1)
            self.bg = Rectangle(pos=main_layout.pos, size=main_layout.size)
            if os.path.exists("tarot_img/bg.jpg"):
                self.bg.source = "tarot_img/bg.jpg"
                print("Background chargé")
        main_layout.bind(pos=self.update_bg, size=self.update_bg)

        # Nom de la carte
        self.card_name_label = Label(
            text=tr("your_card"),
            font_size="32sp",
            color=[0.9, 0.7, 0.3, 1],
            size_hint_y=None,
            height=dp(48),
            bold=True,
            halign='center',
            valign='middle',
        )
        self.card_name_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        main_layout.add_widget(self.card_name_label)

        # Espace
        main_layout.add_widget(Label(size_hint_y=None, height=dp(6)))

        self.card_state_label = Label(
            text="",
            font_size="22sp",
            color=[0.8, 0.6, 0.4, 1],
            size_hint_y=None,
            height=dp(32),
            bold=True,
            halign='center',
            valign='middle',
        )
        self.card_state_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        main_layout.add_widget(self.card_state_label)

        # Espace
        main_layout.add_widget(Label(size_hint_y=None, height=dp(4)))

        self.keywords_label = Label(
            text="",
            font_size="18sp",
            color=[0.7, 0.7, 0.9, 1],
            size_hint_y=None,
            height=dp(28),
            halign='center',
            valign='middle',
        )
        self.keywords_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        main_layout.add_widget(self.keywords_label)

        # Espace sous-titre
        main_layout.add_widget(Label(size_hint_y=None, height=dp(50)))

        # Container image cliquable
        image_container = FloatLayout(size_hint_y=None, height=dp(320))

        self.card_image = Image(
            source="tarot_img/Back.jpg",
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            allow_stretch=True,
            keep_ratio=True
        )

        self.image_button = Button(
            text="",
            background_color=[0, 0, 0, 0],
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.image_button.bind(on_press=self.show_fullscreen_card)

        overlay_label = Label(
            text=tr("touch_to_enlarge"),
            font_size="14sp",
            color=[1, 1, 1, 0.7],
            size_hint=(1, None),
            height=dp(22),
            pos_hint={'center_x': 0.5, 'bottom': 1},
            halign='center',
            valign='middle',
        )
        overlay_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))

        image_container.add_widget(self.card_image)
        image_container.add_widget(self.image_button)
        image_container.add_widget(overlay_label)
        main_layout.add_widget(image_container)

        # Espace
        main_layout.add_widget(Label(size_hint_y=None, height=dp(50)))

        # Signification avec scroll
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(size_hint_y=1)
        self.signification_label = Label(
            text=tr("loading"),
            font_size="20sp",
            color=[1, 1, 1, 1],
            halign='left',
            valign='top',
            size_hint_y=None,
            padding=[dp(10), dp(5)],
        )
        self.signification_label.bind(
            width=lambda inst, val: setattr(inst, 'text_size', (val * 0.92, None))
        )
        self.signification_label.bind(
            texture_size=lambda instance, value: setattr(instance, 'height', value[1] + dp(10))
        )
        scroll.add_widget(self.signification_label)
        main_layout.add_widget(scroll)

        # Bas
        bottom_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[0, dp(6), 0, 0],
            spacing=dp(6),
        )
        bottom_container.bind(minimum_height=bottom_container.setter('height'))

        # Bouton premium
        self.premium_btn = Button(
            text=tr("premium_button_base").replace(" Premium", ""),
            size_hint=(0.7, None),
            height=dp(40),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="12sp",
            bold=True,
            disabled=True,
        )
        with self.premium_btn.canvas.before:
            self.premium_btn_color = Color(0.35, 0.15, 0.55, 1)
            self.premium_btn_bg = RoundedRectangle(
                pos=self.premium_btn.pos,
                size=self.premium_btn.size,
                radius=[20, 20, 20, 20]
            )
        self.premium_btn.opacity = 0.5
        self.premium_btn.bind(on_press=self.purchase_chat_luna)
        self.premium_btn.bind(pos=self.update_premium_btn_canvas, size=self.update_premium_btn_canvas)
        bottom_container.add_widget(self.premium_btn)

        self.premium_status_label = Label(
            text=tr("store_preparing"),
            font_size="9sp",
            color=[0.9, 0.8, 0.95, 1],
            size_hint_y=None,
            height=dp(12),
            halign='center',
            valign='middle',
        )
        self.premium_status_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        bottom_container.add_widget(self.premium_status_label)

        # Bouton retour
        self.back_btn = Button(
            text=tr("new_reading"),
            size_hint=(0.7, None),
            height=dp(40),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="14sp",
            bold=True
        )

        with self.back_btn.canvas.before:
            Color(0.6, 0.4, 0.2, 1.0)
            self.back_btn_bg = RoundedRectangle(
                pos=self.back_btn.pos,
                size=self.back_btn.size,
                radius=[20, 20, 20, 20]
            )

        self.back_btn.bind(pos=self.update_back_btn_canvas, size=self.update_back_btn_canvas)
        self.back_btn.bind(on_press=self.go_back)
        bottom_container.add_widget(self.back_btn)

        # Ajouter le conteneur bas
        main_layout.add_widget(bottom_container)

        # Bannière pub (cachée)
        self.ad_banner = Label(
            text=tr("crystals_ad"),
            font_size="16sp",
            color=[1, 0.8, 0.2, 1],
            size_hint_y=None,
            height=dp(40),
            halign='center',
            valign='middle'
        )
        self.ad_banner.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        self.ad_banner.opacity = 0
        main_layout.add_widget(self.ad_banner)

        self.add_widget(main_layout)

    def show_fullscreen_card(self, instance):
        """Affiche la carte en plein écran"""
        print(f"Affichage plein écran: {self.current_card_name}")

        # Animation click
        click_anim = Animation(opacity=0.7, duration=0.1)
        click_anim += Animation(opacity=1, duration=0.1)
        click_anim.start(self.card_image)

        # Popup plein écran
        fullscreen_popup = FullScreenCardPopup(
            card_image_source=self.current_card_image_path or self.card_image.source,
            card_name=self.current_card_name,
            card_state=self.card_state_label.text
        )
        fullscreen_popup.open()

    def setup_card(self, card_name, state):
        print(f"=== SETUP CARTE (NOUVEAU): {card_name} - {state} ===")
        self.current_card_name = card_name
        self.current_card_state = state

        # langue courante (force/auto)
        lang = resolve_lang()
        try:
            cards_signification = get_cards_signification(lang) or {}
        except Exception as e:
            print(f"⚠️ get_cards_signification failed for '{lang}': {e}")
            try:
                cards_signification = get_cards_signification("en") or {}
            except Exception:
                cards_signification = {}

        print(f"DEBUG: signification keys count = {len(cards_signification)} | first keys: {list(cards_signification.keys())[:5]}")
        card_info = cards_signification.get(card_name, {}) or {}

        # Nom de la carte
        self.card_name_label.text = card_name
        self.card_name_label.font_size = "38sp"
        self.card_name_label.height = dp(56)

        # État (upright/reversed) traduit
        state_norm = (state or "").strip().lower()
        lookup_state = "reversed" if state_norm in ["a l'envers", "à l'envers", "envers", "reversed", "invertida"] else "upright"
        self.card_state_label.text = tr("reversed") if lookup_state == "reversed" else tr("upright")
        self.card_state_label.font_size = "28sp"
        self.card_state_label.height = dp(40)
        self.keywords_label.font_size = "22sp"
        self.keywords_label.height = dp(34)

        # Image (image / image_reversed)
        try:
            self.card_image.size_hint = (1.1, 1.1)
            image_path = card_info.get("image_reversed") if lookup_state == "reversed" else card_info.get("image")
            self.current_card_image_path = image_path or "tarot_img/Back.jpg"
            self.card_image.source = self.current_card_image_path
            self.card_image.reload()
            if image_path and os.path.exists(image_path):
                print(f"✓ Image chargée: {image_path}")
            else:
                print(f"✗ Image non trouvée (fallback utilisé): {self.current_card_image_path}")
        except Exception as e:
            print(f"✗ Erreur image: {e}")
            self.current_card_image_path = "tarot_img/Back.jpg"
            self.card_image.source = self.current_card_image_path
            self.card_image.reload()

        # Mots-clés et signification
        try:
            # keywords: 'upright' | 'reversed'
            keywords = card_info.get(lookup_state)

            # texte long: 'signification upright' | 'signification reversed'
            detail = card_info.get(f"signification {lookup_state}")

            if keywords:
                self.keywords_label.text = f"💫 {str(keywords).upper()} 💫"
            else:
                self.keywords_label.text = ""

            if detail:
                self.start_typewriter(str(detail))
                print(f"✓ Signification trouvée pour {card_name} [{lookup_state}]")
            else:
                self.start_typewriter(tr("no_description"))

            Clock.schedule_once(self.setup_text_wrapping, 0.1)
        except Exception as e:
            print(f"✗ Erreur signification: {e}")
            self.signification_label.text = tr("signification_error")

    def setup_text_wrapping(self, dt):
        if self.signification_label and self.parent:
            self.signification_label.text_size = (self.width * 0.9, None)
            self.signification_label.height = self.signification_label.texture_size[1]

    def update_back_btn_canvas(self, instance, value):
        if hasattr(self, "back_btn_bg"):
            self.back_btn_bg.pos = instance.pos
            self.back_btn_bg.size = instance.size

    def update_premium_btn_canvas(self, instance, value):
        if hasattr(self, "premium_btn_bg"):
            self.premium_btn_bg.pos = instance.pos
            self.premium_btn_bg.size = instance.size

    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def go_back(self, instance):
        if self.manager:
            # adapte si ton écran principal s'appelle "card_screen"
            self.manager.current = "main_screen"

    def purchase_chat_luna(self, *_args):
        app = App.get_running_app()
        billing = getattr(app, "billing", None)
        import sys
        if not hasattr(sys, 'getandroidapilevel'):
            # Simulation desktop : achat toujours réussi
            app.on_purchase_success("premium_chat_luna", "simulation")
            return
        if not billing:
            self.show_purchase_error(tr("store_unavailable_platform"))
            return
        if not billing.is_ready():
            self.show_purchase_error(tr("store_preparing_retry"))
            return
        billing.start_premium_purchase()

    def update_premium_button(self, available, price_text, mode):
        button_text = tr("chat_mme_t")
        if price_text:
            button_text += f" ({price_text})"

        self.premium_btn.text = button_text
        self.premium_btn.disabled = not available
        self.premium_btn.opacity = 1 if available else 0.5
        if hasattr(self, "premium_btn_color"):
            active_color = (0.45, 0.25, 0.65, 1)
            inactive_color = (0.25, 0.15, 0.35, 1)
            self.premium_btn_color.rgba = active_color if available else inactive_color

        if available:
            self.premium_status_label.text = ""
            self.premium_status_label.opacity = 0
            self.premium_status_label.height = 0
        else:
            self.premium_status_label.opacity = 1
            self.premium_status_label.height = dp(20)
            if mode in ("disabled", "simulation") and platform_name != "android":
                self.premium_status_label.text = tr("store_mobile_only")
            else:
                self.premium_status_label.text = tr("store_preparing")

    def show_purchase_success(self, provider="google", price_text=None):
        if not MME_T_BACKEND_URL:
            provider_label = tr("provider_google") if provider == "google" else tr("provider_amazon") if provider == "amazon" else ""
            message = tr("thanks_for_support")
            if provider_label:
                message = tr("thanks_for_support_via", provider=provider_label)
            message += "\n" + tr("configure_backend_hint")
            self._open_purchase_popup(tr("thanks_title"), message)
            return

        self.open_mme_t_chat(provider=provider, price_text=price_text)

    def show_purchase_error(self, message):
        self._open_purchase_popup(tr("purchase_error_title"), message)

    def open_mme_t_chat(self, provider="google", price_text=None):
        if self.chat_popup and self.chat_popup.parent:
            self.chat_popup.dismiss()
        # Fournir jusqu'à 3 cartes tirées
        try:
            app = App.get_running_app()
            drawn = getattr(app, 'last_drawn_cards', None) or []
        except Exception:
            drawn = []
        drawn_three = list(drawn)[:3]
        while len(drawn_three) < 3:
            drawn_three.append((None, None))

        self.chat_popup = MmeTChatPopup(
            language=resolve_lang(),
            provider=provider,
            price_text=price_text,
            context_text=self._build_mme_t_context(),
            drawn_cards=drawn_three,
            on_session_complete=self._on_chat_complete,
        )
        self.chat_popup.bind(on_dismiss=lambda *_: setattr(self, "chat_popup", None))
        self.chat_popup.open()

    def _build_mme_t_context(self):
        parts = []
        # Ajoute la liste des trois cartes tirées en tout début
        try:
            app = App.get_running_app()
            drawn = getattr(app, "last_drawn_cards", None)
            if drawn and isinstance(drawn, (list, tuple)) and len(drawn) > 0:
                def fmt(c, s):
                    display = c if c else tr('your_card')
                    state_label = tr('upright') if s == 'upright' else tr('reversed')
                    return f"{display} ({state_label})"
                drawn_summary = " | ".join(fmt(c, s) for c, s in drawn)
                parts.append(f"{tr('draw_card')} ({len(drawn)}): {drawn_summary}")
        except Exception:
            pass
        # Ajoute ensuite le reste du contexte
        card_title = (self.card_name_label.text or "").strip()
        if card_title:
            parts.append(f"{tr('your_card')}: {card_title}")
        card_state = (self.card_state_label.text or "").strip()
        if card_state:
            parts.append(f"Position: {card_state}")
        keywords = (self.keywords_label.text or "").strip()
        if keywords:
            clean_keywords = keywords.replace("💫", "").strip()
            if clean_keywords:
                parts.append(f"Keywords: {clean_keywords}")
        return " | ".join(parts)

    def _on_chat_complete(self):
        if not self.manager:
            return
        def _switch(_dt):
            self.manager.current = "main_screen"
        Clock.schedule_once(_switch, 0)

    def _open_purchase_popup(self, title, message):
        popup_layout = BoxLayout(orientation="vertical", padding=20, spacing=20)
        popup_label = Label(
            text=message,
            color=[1, 1, 1, 1],
            halign="center",
            valign="middle",
        )
        popup_label.bind(
            size=lambda inst, val: setattr(inst, "text_size", val)
        )
        close_btn = Button(
            text="Fermer",
            size_hint_y=None,
            height=40,
            background_normal='',
            background_color=[0.6, 0.3, 0.3, 1],
            color=[1, 1, 1, 1],
        )
        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        close_btn.bind(on_release=popup.dismiss)
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(close_btn)
        popup.open()

    def show_ad_banner(self):
        self.ad_banner.opacity = 1

    def hide_ad_banner(self):
        self.ad_banner.opacity = 0

    def on_enter(self, *args):
        """Afficher la bannière AdMob quand on entre sur cet écran"""
        super().on_enter(*args)
        print("📱 ResponseScreen: on_enter - Affichage bannière AdMob")

        app = App.get_running_app()
        if hasattr(app, 'ads') and hasattr(app.ads, 'show_banner'):
            app.ads.show_banner()

    def on_leave(self, *args):
        """Masquer la bannière AdMob quand on quitte cet écran"""
        super().on_leave(*args)
        print("📱 ResponseScreen: on_leave - Masquage bannière AdMob")

        app = App.get_running_app()
        if hasattr(app, 'ads') and hasattr(app.ads, 'hide_banner'):
            app.ads.hide_banner()

    def start_typewriter(self, text, speed=0.02):
        """Affiche le texte lettre par lettre (effet machine à écrire)"""
        if self.typewriter_event:
            self.typewriter_event.cancel()
        self.typewriter_full_text = text
        self.typewriter_index = 0
        self.signification_label.text = ""
        self.typewriter_event = Clock.schedule_interval(lambda dt: self.typewriter_step(speed), speed)

    def typewriter_step(self, speed):
        if self.typewriter_index < len(self.typewriter_full_text):
            self.signification_label.text += self.typewriter_full_text[self.typewriter_index]
            self.typewriter_index += 1
            # Scroll automatique si besoin
            if self.signification_label.parent:
                self.signification_label.parent.scroll_y = 1
        else:
            if self.typewriter_event:
                self.typewriter_event.cancel()
            return False
