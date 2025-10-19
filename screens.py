from __future__ import annotations
# -*- coding: utf-8 -*-
"""
Module des écrans pour l'application Kivy.
Contient les classes d'écrans (RootScreen, CardScreen, ResponseScreen) et leurs dépendances.
"""
# -*- coding: utf-8 -*-
"""Écrans principaux de l'application Kivy: CardScreen et ResponseScreen.

Cette version est une reconstruction propre adaptée à la nouvelle API i18n
(utilisation de tr("messages.*") et get_cards_signification).
"""

import os
import random
import json
from typing import Optional, List, Tuple

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
from kivy.uix.scrollview import ScrollView
from kivy.animation import Animation

# Local i18n helpers provided by main.py


# Popups
from popups import LoadingPopup, FullScreenCardPopup, MmeTChatPopup, AdPopup, AdsPopup


READING_COUNT = 0


def _normalize_lang(code: Optional[str]) -> str:
    if not code:
        return "en"
    code = code.lower().replace("_", "-")
    if code.startswith("fr"):
        return "fr"
    if code.startswith("en"):
        return "en"
    if code.startswith("pt"):
        return "pt"
    if code.startswith("es"):
        return "es"
    return code[:2]


def resolve_lang() -> str:
    try:
        app = App.get_running_app()
        cfg = getattr(app, "cfg", None)
        if cfg:
            forced = cfg.get("force_lang") or cfg.get("language")
            if forced:
                return _normalize_lang(forced)
    except Exception:
        pass
    env = os.environ.get("APP_LANG")
    if env:
        return _normalize_lang(env)
    # Récupère la langue depuis App (chargée dans main.py)
    try:
        app = App.get_running_app()
        app_lang = getattr(app, "lang", None)
        if app_lang:
            return _normalize_lang(app_lang)
    except Exception:
        pass
    return "fr"


def should_show_ad() -> bool:
    global READING_COUNT
    READING_COUNT += 1
    return READING_COUNT % 3 == 0


class RootScreen(ScreenManager):
    pass


class CardScreen(Screen):
    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size
    def __init__(self, **kwargs):
        super(CardScreen, self).__init__(**kwargs)
        app = App.get_running_app()
        self.tr = getattr(app, 'tr', lambda k: k)
        self.lang = getattr(app, 'lang', 'fr')
        self.loading_popup = None

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        with layout.canvas.before:
            if os.path.exists("tarot_img/bg.jpg"):
                self.bg = Rectangle(pos=layout.pos, size=layout.size, source="tarot_img/bg.jpg")
            else:
                Color(0.2, 0.1, 0.3, 1)
                self.bg = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)

        self.title_label = Label(
            text=self.tr("messages.app_title"),
            font_size="22sp",
            color=[0.9, 0.7, 0.3, 1],
            size_hint_y=0.15,
            bold=True,
            halign='center',
            valign='middle',
            font_name="Body"
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
            text=self.tr("messages.draw_instruction"),
            font_size="18sp",
            color=[0.7, 0.5, 0.3, 1],
            size_hint_y=0.15,
            halign='center',
            valign='middle',
            font_name="Body"
        )
        self.instructions_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        layout.add_widget(self.instructions_label)

        self.ad_banner = Label(
            text=self.tr("messages.crystals_ad"),
            font_size="16sp",
            color=[1, 0.8, 0.2, 1],
            size_hint_y=0.08,
            halign='center',
            valign='middle',
            font_name="Body"
        )
        self.ad_banner.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        self.ad_banner.opacity = 0
        layout.add_widget(self.ad_banner)

        self.add_widget(layout)

    def _update_bg(self, instance, value):
        try:
            self.bg.pos = instance.pos
            self.bg.size = instance.size
        except Exception:
            pass

    def draw_card(self, _instance):
        Animation(opacity=0.3, duration=0.08) + Animation(opacity=1, duration=0.08)
        self.loading_popup = LoadingPopup()
        self.loading_popup.open()
        Clock.schedule_once(self.perform_card_draw, 5.0)

    def refresh_translations(self):
        self.title_label.text = self.tr("messages.app_title")
        self.instructions_label.text = self.tr("messages.draw_instruction")
        self.ad_banner.text = self.tr("messages.crystals_ad")

    def perform_card_draw(self, _dt):
        try:
            # Tirage basé directement sur les clés fournies par la langue courante
            # get_cards_signification() doit retourner le dict "significations" de la langue active
            app = App.get_running_app()
            if app and hasattr(app, 'get_cards_signification'):
                cards_signification = app.get_cards_signification() or {}
            else:
                cards_signification = {}
            cards = list(cards_signification.keys()) if isinstance(cards_signification, dict) else []

            # Si la langue actuelle ne contient pas de clés, fallback vers le fichier français
            if not cards:
                try:
                    fr_path = os.path.join(os.path.dirname(__file__), "i18n", "lang", "fr.json")
                    with open(fr_path, "r", encoding="utf-8") as f:
                        fr_data = json.load(f)
                    cards = list(fr_data.get("significations", {}).keys())
                    print(f"🌍 Fallback tirage FR avec {len(cards)} cartes")
                except Exception:
                    cards = []

            if not cards:
                if self.loading_popup:
                    try:
                        self.loading_popup.dismiss()
                    except Exception:
                        pass
                return

            try:
                count = int(os.environ.get("TAROT_DRAW_COUNT", "3"))
            except Exception:
                count = 3
            count = max(1, min(4, count))

            drawn: List[Tuple[str, str]] = []
            pool = list(cards)
            for _ in range(count):
                if not pool:
                    pool = list(cards)
                pick = random.choice(pool)
                pool.remove(pick)
                state = random.choice(["upright", "reversed"])
                drawn.append((pick, state))

            try:
                app = App.get_running_app()
                app.last_drawn_cards = drawn
            except Exception:
                pass

            if self.loading_popup:
                try:
                    self.loading_popup.dismiss()
                except Exception:
                    pass

            def _show():
                if self.manager:
                    resp = self.manager.get_screen("response_screen")
                    resp.setup_card(drawn[0][0], drawn[0][1])
                    if hasattr(resp, "set_full_draw"):
                        try:
                            resp.set_full_draw(drawn)
                        except Exception:
                            pass
                    self.manager.current = "response_screen"

            if should_show_ad():
                popup = AdsPopup(on_close_callback=lambda *a: _show(), tr=self.tr)
                popup.open()
            else:
                _show()
        except Exception as exc:
            print(f"Erreur perform_card_draw: {exc}")
            if self.loading_popup:
                try:
                    self.loading_popup.dismiss()
                except Exception:
                    pass


class ResponseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        self.tr = getattr(app, 'tr', lambda k: k)
        self.lang = getattr(app, 'lang', 'fr')
        self.current_card_name = ""
        self.current_card_state = ""
        self.current_card_image_path = "tarot_img/Back.jpg"

        self.typewriter_event = None
        self.typewriter_full_text = ""
        self.typewriter_index = 0
        self.chat_popup = None

        main_layout = BoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(15), dp(20), dp(15)],
            spacing=dp(6),
        )
        with main_layout.canvas.before:
            Color(0.12, 0.07, 0.18, 1)
            self.bg = Rectangle(pos=main_layout.pos, size=main_layout.size)
            if os.path.exists("tarot_img/bg.jpg"):
                self.bg.source = "tarot_img/bg.jpg"
        main_layout.bind(pos=self.update_bg, size=self.update_bg)

        # Nom de la carte
        self.card_name_label = Label(
            text="",
            font_size="32sp",
            color=[0.9, 0.7, 0.3, 1],
            size_hint_y=None,
            height=dp(48),
            bold=True,
            halign='center',
            valign='middle',
            font_name="Body"
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
            font_name="Body"
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
            font_name="Body"
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
            text=self.tr("messages.touch_to_enlarge"),
            font_size="14sp",
            color=[1, 1, 1, 0.7],
            size_hint=(1, None),
            height=dp(22),
            pos_hint={'center_x': 0.5, 'bottom': 1},
            halign='center',
            valign='middle',
            font_name="Body"
        )
        overlay_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))

        image_container.add_widget(self.card_image)
        image_container.add_widget(self.image_button)
        image_container.add_widget(overlay_label)
        main_layout.add_widget(image_container)

        # Espace
        main_layout.add_widget(Label(size_hint_y=None, height=dp(50)))

        # Signification avec scroll
        scroll = ScrollView(size_hint_y=1)
        self.signification_label = Label(
            text=self.tr("messages.loading"),
            font_size="20sp",
            color=[1, 1, 1, 1],
            halign='left',
            valign='top',
            size_hint_y=None,
            padding=[dp(10), dp(5)],
            font_name="Body"
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
            text=self.tr("messages.premium_button_base"),
            size_hint=(0.7, None),
            height=dp(40),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="12sp",
            bold=True,
            font_name="Body"
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
            text=self.tr("messages.store_preparing"),
            font_size="9sp",
            color=[0.9, 0.8, 0.95, 1],
            size_hint_y=None,
            height=dp(12),
            halign='center',
            valign='middle',
            font_name="Body"
        )
        self.premium_status_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        bottom_container.add_widget(self.premium_status_label)

        # Bouton retour
        self.back_btn = Button(
            text=self.tr("messages.new_reading"),
            size_hint=(0.7, None),
            height=dp(40),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="14sp",
            bold=True,
            font_name="Body"
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
            text=self.tr("messages.crystals_ad"),
            font_size="16sp",
            color=[1, 0.8, 0.2, 1],
            size_hint_y=None,
            height=dp(40),
            halign='center',
            valign='middle',
            font_name="Body"
        )
        self.ad_banner.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        self.ad_banner.opacity = 0
        main_layout.add_widget(self.ad_banner)

        self.add_widget(main_layout)

    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def _update_bg(self, instance, value):
        try:
            self.bg.pos = instance.pos
            self.bg.size = instance.size
        except Exception:
            pass

    def show_fullscreen_card(self, *_):
        # Récupérer le nom localisé depuis les données de la carte
        try:
            app = App.get_running_app()
            if app and hasattr(app, 'get_cards_signification'):
                cards = app.get_cards_signification() or {}
            else:
                cards = {}
            info = cards.get(self.current_card_name, {}) if isinstance(cards, dict) else {}
            display_name = info.get("name", self.current_card_name)
        except Exception as e:
            display_name = self.current_card_name

        # Utiliser l'état déjà traduit affiché dans le label si possible
        card_state_text = (self.card_state_label.text or "").strip()

        popup = FullScreenCardPopup(
            card_image_source=self.current_card_image_path or self.card_image.source,
            card_name=display_name,
            card_state=card_state_text,
            tr=self.tr
        )
        popup.open()

    def setup_card(self, card_name: str, state: str):
        self.current_card_name = card_name or ""
        self.current_card_state = state or "upright"
        
        # Récupérer les données de la carte
        try:
            app = App.get_running_app()
            if app and hasattr(app, 'get_cards_signification'):
                cards = app.get_cards_signification() or {}
            else:
                cards = {}
        except Exception:
            cards = {}

        info = cards.get(card_name, {}) if isinstance(cards, dict) else {}

        # Utiliser le nom localisé pour l'affichage
        display_name = info.get("name", card_name)
        self.card_name_label.text = display_name
        self.card_state_label.text = self.tr("messages.reversed") if self.current_card_state == "reversed" else self.tr("messages.upright")

        image_path = info.get("image_reversed") if self.current_card_state == "reversed" else info.get("image")
        self.current_card_image_path = image_path or "tarot_img/Back.jpg"
        self.card_image.source = self.current_card_image_path
        try:
            self.card_image.reload()
        except Exception:
            pass

        keywords = info.get("upright") if self.current_card_state == "upright" else info.get("reversed")
        detail = info.get(f"signification upright") if self.current_card_state == "upright" else info.get(f"signification reversed")

        self.keywords_label.text = f"💫 {str(keywords).upper()} 💫" if keywords else ""
        if detail:
            self.start_typewriter(str(detail))
        else:
            self.signification_label.text = self.tr("messages.no_description")

        # Ajuste le wrapping après un petit délai pour que les layouts soient évalués
        try:
            Clock.schedule_once(self.setup_text_wrapping, 0.05)
        except Exception:
            pass

    def start_typewriter(self, text: str, speed: float = 0.02):
        if self.typewriter_event:
            try:
                self.typewriter_event.cancel()
            except Exception:
                pass
        self.typewriter_full_text = text
        self.typewriter_index = 0
        self.signification_label.text = ""
        self.typewriter_event = Clock.schedule_interval(lambda dt: self.typewriter_step(speed), speed)

    def typewriter_step(self, speed: float):
        if self.typewriter_index < len(self.typewriter_full_text):
            self.signification_label.text += self.typewriter_full_text[self.typewriter_index]
            self.typewriter_index += 1
            if self.signification_label.parent:
                try:
                    self.signification_label.parent.scroll_y = 1
                except Exception:
                    pass
            return True
        else:
            if self.typewriter_event:
                try:
                    self.typewriter_event.cancel()
                except Exception:
                    pass
                self.typewriter_event = None
            return False

    def go_back(self, *_):
        if self.manager:
            self.manager.current = "main_screen"

    def purchase_chat_luna(self, *_):
        app = App.get_running_app()
        billing = getattr(app, 'billing', None)
        import sys
        if not hasattr(sys, 'getandroidapilevel'):
            try:
                app.on_purchase_success("premium_chat_luna", "simulation")
            except Exception:
                pass
            return
        if not billing:
            self._open_purchase_popup(self.tr("messages.purchase_error_title"), self.tr("messages.store_unavailable_platform"))
            return
        if not billing.is_ready():
            self._open_purchase_popup(self.tr("messages.purchase_error_title"), self.tr("messages.store_preparing_retry"))
            return
        billing.start_premium_purchase()

    def _open_purchase_popup(self, title: str, message: str):
        layout = BoxLayout(orientation='vertical', padding=16, spacing=12)
        lbl = Label(text=message)
        btn = Button(text=self.tr("messages.close"), size_hint_y=None, height=dp(40))
        popup = Popup(title=title, content=layout, size_hint=(0.9, 0.5))
        btn.bind(on_release=popup.dismiss)
        layout.add_widget(lbl)
        layout.add_widget(btn)
        popup.open()

    def update_back_btn_canvas(self, instance, value):
        try:
            if hasattr(self, 'back_btn_bg'):
                self.back_btn_bg.pos = instance.pos
                self.back_btn_bg.size = instance.size
        except Exception:
            pass

    def update_premium_btn_canvas(self, instance, value):
        try:
            if hasattr(self, 'premium_btn_bg'):
                self.premium_btn_bg.pos = instance.pos
                self.premium_btn_bg.size = instance.size
        except Exception:
            pass

    def show_fullscreen_card(self, *_):
        try:
            app = App.get_running_app()
            if app and hasattr(app, 'get_cards_signification'):
                cards = app.get_cards_signification() or {}
            else:
                cards = {}
            info = cards.get(self.current_card_name, {}) if isinstance(cards, dict) else {}
            display_name = info.get("name", self.current_card_name)
        except Exception:
            display_name = self.current_card_name

        popup = FullScreenCardPopup(
            card_image_source=self.current_card_image_path or self.card_image.source,
            card_name=display_name,
        )
        popup.open()

    def update_premium_button(self, available, price_text, mode):
        self.mode = mode  # Stocker le mode pour simulation
        # Restaurer le comportement attendu depuis l'ancien screens.py mais avec self.tr
        button_text = self.tr("messages.chat_mme_t") if self.tr else "Chat Mme T"
        if price_text:
            button_text += f" ({price_text})"

        try:
            self.premium_btn.text = button_text
            self.premium_btn.disabled = not bool(available)
            self.premium_btn.opacity = 1 if available else 0.5
            if hasattr(self, 'premium_btn_color'):
                active_color = (0.45, 0.25, 0.65, 1)
                inactive_color = (0.25, 0.15, 0.35, 1)
                self.premium_btn_color.rgba = active_color if available else inactive_color

            if available:
                if hasattr(self, 'premium_status_label'):
                    self.premium_status_label.text = ""
                    self.premium_status_label.opacity = 0
                    self.premium_status_label.height = 0
            else:
                if hasattr(self, 'premium_status_label'):
                    self.premium_status_label.opacity = 1
                    self.premium_status_label.height = dp(20)
                    if mode in ("disabled", "simulation"):
                        self.premium_status_label.text = self.tr("messages.store_mobile_only") if self.tr else "Mobile only"
                    else:
                        self.premium_status_label.text = self.tr("messages.store_preparing") if self.tr else "Preparing store"
        except Exception:
            pass

    def show_purchase_success(self, provider="google", price_text=None):
        # Si pas de backend Mme T configuré, afficher un message remerciant le soutien
        try:
            if not getattr(__import__("main"), 'MME_T_BACKEND_URL', None):
                provider_label = self.tr("messages.provider_google") if provider == "google" else (self.tr("messages.provider_amazon") if provider == "amazon" else "")
                message = self.tr("messages.thanks_for_support")
                if provider_label:
                    message = self.tr("messages.thanks_for_support_via", provider=provider_label)
                message += "\n" + self.tr("messages.configure_backend_hint")
                self._open_purchase_popup(self.tr("messages.thanks_title"), message)
                return
        except Exception:
            pass
        self.open_mme_t_chat(provider=provider, price_text=price_text)

    def show_purchase_error(self, message):
        self._open_purchase_popup(self.tr("messages.purchase_error_title"), message)

    def open_mme_t_chat(self, provider="google", price_text=None):
        # Ouvre le popup MmeTChat avec jusqu'à 3 cartes
        try:
            if self.chat_popup and getattr(self.chat_popup, 'parent', None):
                self.chat_popup.dismiss()
        except Exception:
            pass
        try:
            app = App.get_running_app()
            drawn = getattr(app, 'last_drawn_cards', None) or []
        except Exception:
            drawn = []
        drawn_three = list(drawn)[:3]
        while len(drawn_three) < 3:
            drawn_three.append((None, None))

        self.chat_popup = MmeTChatPopup(
            language=self.lang,
            provider=provider,
            price_text=price_text,
            context_text=self._build_mme_t_context(),
            drawn_cards=drawn_three,
            on_session_complete=self._on_chat_complete,
            tr=self.tr,
        )
        try:
            self.chat_popup.bind(on_dismiss=lambda *_: setattr(self, 'chat_popup', None))
            self.chat_popup.open()
        except Exception:
            pass

    def _build_mme_t_context(self):
        parts = []
        parts.append(f"Langue de réponse: {self.lang}")
        try:
            app = App.get_running_app()
            drawn = getattr(app, 'last_drawn_cards', None)
            if drawn and isinstance(drawn, (list, tuple)) and len(drawn) > 0:
                def fmt(c, s):
                    display = c if c else self.tr('messages.your_card')
                    state_label = self.tr('messages.upright') if s == 'upright' else self.tr('messages.reversed')
                    return f"{display} ({state_label})"
                drawn_summary = " | ".join(fmt(c, s) for c, s in drawn)
                parts.append(f"{self.tr('messages.draw_card')} ({len(drawn)}): {drawn_summary}")
        except Exception:
            pass
        card_title = (self.card_name_label.text or "").strip()
        if card_title:
            parts.append(f"{self.tr('messages.your_card')}: {card_title}")
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

    def _open_purchase_popup(self, title: str, message: str):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        label = Label(text=message)
        btn = Button(text=self.tr('messages.close'))
        popup = Popup(title=title, content=layout, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        layout.add_widget(label)
        layout.add_widget(btn)
        popup.open()

    def show_ad_banner(self):
        try:
            self.ad_banner.opacity = 1
        except Exception:
            pass

    def hide_ad_banner(self):
        try:
            self.ad_banner.opacity = 0
        except Exception:
            pass

    def on_enter(self, *args):
        super().on_enter(*args)
        try:
            app = App.get_running_app()
            if hasattr(app, 'ads') and hasattr(app.ads, 'show_banner'):
                app.ads.show_banner()
        except Exception:
            pass

    def on_leave(self, *args):
        super().on_leave(*args)
        try:
            app = App.get_running_app()
            if hasattr(app, 'ads') and hasattr(app.ads, 'hide_banner'):
                app.ads.hide_banner()
        except Exception:
            pass

    def setup_text_wrapping(self, dt):
        try:
            if self.signification_label and self.parent:
                self.signification_label.text_size = (self.width * 0.9, None)
                self.signification_label.height = self.signification_label.texture_size[1]
        except Exception:
            pass
