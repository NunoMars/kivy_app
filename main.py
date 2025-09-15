__version__ = "0.01"

import os
import random
import locale
from translations import MESSAGES

# Détecter la langue du système
def get_system_language():
    try:
        # Prend la variable d'environnement LANG si présente
        lang = os.environ.get("LANG", "")
        if lang.startswith("pt"):
            return "pt"
        elif lang.startswith("en"):
            return "en"
        else:
            return "fr"
    except:
        return "fr"

# Langue actuelle de l'application
CURRENT_LANG = get_system_language()
print(f"🌍 Langue détectée: {CURRENT_LANG}")

# Fonction helper pour obtenir les traductions
def tr(key, **kwargs):
    txt = MESSAGES[CURRENT_LANG].get(key, MESSAGES["fr"][key])
    if kwargs:
        try:
            return txt.format(**kwargs)
        except Exception:
            return txt
    return txt

# Configuration Kivy
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_NO_FILELOG'] = '1'

from kivy.config import Config
Config.set('graphics', 'width', '300')
Config.set('graphics', 'height', '600')
Config.set('kivy', 'log_level', 'warning')
Config.set('kivy', 'show_cursor', '1')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.animation import Animation
import random
import os

# Import des significations selon la langue détectée
try:
    if CURRENT_LANG == "en":
        from signification_en import get_cards_signification  # Maintenant correct !
        print("✓ Significations EN importées")
    elif CURRENT_LANG == "pt": 
        from signification_pt import get_cards_signification
        print("✓ Significations PT importées")
    else:
        from signification_fr import get_cards_signification
        print("✓ Significations FR importées")
except Exception as e:
    print(f"✗ Erreur significations: {e}")
    def get_cards_signification():
        return {"Le Mat": {"droite": "Nouveau départ", "a l'envers": "Imprudence"}}

try:
    from card_image_mapping import get_card_image_path
    print("✓ Mapping images importé")
except Exception as e:
    print(f"✗ Erreur mapping: {e}")
    def get_card_image_path(card, state):
        base_path = "tarot_img/MajorArcanaCards"
        if state == "a l'envers":
            return os.path.join(base_path, f"{card} a l'envers.jpg")
        return os.path.join(base_path, f"{card}.jpg")


try:
    from card_name_mapping import get_card_name_for_lang
    print("✓ Card name mapping importé")
except Exception as e:
    print(f"✗ Erreur card name mapping: {e}")
    def get_card_name_for_lang(french_name, target_lang):
        return french_name


# Système de compteur pour les publicités
READING_COUNT = 0
ADS_FREQUENCY = 3  # Afficher une pub toutes les 3 lectures

def should_show_ad():
    """Détermine s'il faut afficher une publicité"""
    global READING_COUNT
    READING_COUNT += 1
    return READING_COUNT % ADS_FREQUENCY == 0

def reset_reading_count():
    """Remet le compteur à zéro (pour les tests)"""
    global READING_COUNT
    READING_COUNT = 0

# Classe pour la publicité
class AdPopup(Popup):
    """Popup de publicité"""
    
    def __init__(self, **kwargs):
        super(AdPopup, self).__init__(**kwargs)
        self.title = ""
        self.size_hint = (0.9, 0.7)
        self.auto_dismiss = False
        self.separator_height = 0
        
        layout = BoxLayout(orientation="vertical", spacing=20, padding=[20, 20, 20, 20])
        
        # Background
        with layout.canvas.before:
            Color(0.1, 0.15, 0.3, 0.95)
            self.bg_rect = RoundedRectangle(
                pos=layout.pos, 
                size=layout.size,
                radius=[15, 15, 15, 15]
            )
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Titre publicité
        ad_title = Label(
            text=tr("support_app"),  # "Soutenez l'application"
            font_size="20sp",
            color=[0.9, 0.7, 0.3, 1],
            size_hint_y=0.2,
            bold=True,
            halign='center'
        )
        layout.add_widget(ad_title)
        
        # Message
        ad_message = Label(
            text=tr("ad_message"),  # Message de soutien
            font_size="16sp",
            color=[1, 1, 1, 1],
            size_hint_y=0.4,
            halign='center',
            valign='center',
            text_size=(None, None)
        )
        layout.add_widget(ad_message)
        
        # Zone boutons
        button_layout = BoxLayout(orientation="horizontal", spacing=20, size_hint_y=0.4)
        
        # Bouton "Plus tard"
        later_btn = Button(
            text=tr("later"),  # "Plus tard"
            size_hint=(0.5, 1),
            font_size="16sp",
            background_normal='',
            background_color=[0.5, 0.5, 0.5, 0.8],
            color=[1, 1, 1, 1]
        )
        later_btn.bind(on_press=self.close_ad)
        
        # Bouton "Soutenir"
        support_btn = Button(
            text=tr("support"),  # "Soutenir"
            size_hint=(0.5, 1),
            font_size="16sp",
            background_normal='',
            background_color=[0.2, 0.7, 0.2, 1],
            color=[1, 1, 1, 1],
            bold=True
        )
        support_btn.bind(on_press=self.open_support)
        
        button_layout.add_widget(later_btn)
        button_layout.add_widget(support_btn)
        layout.add_widget(button_layout)
        
        self.content = layout
        
        # Animation d'entrée
        self.opacity = 0
        entrance_anim = Animation(opacity=1, duration=0.3)
        entrance_anim.start(self)
        
        # Auto-fermeture après 10 secondes
        Clock.schedule_once(self.auto_close, 10)
    
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def close_ad(self, instance):
        print("🎯 Publicité fermée")
        exit_anim = Animation(opacity=0, duration=0.2)
        exit_anim.bind(on_complete=lambda *args: self.dismiss())
        exit_anim.start(self)
    
    def open_support(self, instance):
        print("💝 Ouverture page de soutien")
        # Ici vous pouvez ajouter le lien vers votre page de soutien
        self.close_ad(instance)
    
    def auto_close(self, dt):
        print("⏰ Auto-fermeture publicité")
        self.close_ad(None)


class FullScreenCardPopup(Popup):
    """Popup plein écran pour afficher la carte"""
    
    def __init__(self, card_image_source, card_name, card_state, **kwargs):
        super(FullScreenCardPopup, self).__init__(**kwargs)
        
        self.title = ""
        self.size_hint = (1, 1)
        self.auto_dismiss = False
        self.separator_height = 0
        
        layout = BoxLayout(orientation="vertical", spacing=0)
        
        with layout.canvas.before:
            Color(0, 0, 0, 0.95)
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Header avec nom et état
        header = BoxLayout(orientation="vertical", size_hint_y=0.15, padding=[20, 10])
        
        title_label = Label(
            text=card_name,
            font_size="26sp",
            color=[0.9, 0.7, 0.3, 1],
            halign='center',
            bold=True
        )
        header.add_widget(title_label)
        
        state_label = Label(
            text=card_state,
            font_size="18sp",
            color=[0.8, 0.6, 0.4, 1],
            halign='center',
            bold=True
        )
        header.add_widget(state_label)
        layout.add_widget(header)
        
        # Zone carte cliquable
        card_container = FloatLayout(size_hint_y=0.7)
        
        self.fullscreen_image = Image(
            source=card_image_source,
            size_hint=(0.9, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            allow_stretch=True,
            keep_ratio=True
        )
        
        close_button = Button(
            text="",
            background_color=[0, 0, 0, 0],
            size_hint=(0.9, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        close_button.bind(on_press=self.close_fullscreen)
        
        card_container.add_widget(self.fullscreen_image)
        card_container.add_widget(close_button)
        layout.add_widget(card_container)
        
        # Footer
        footer = BoxLayout(size_hint_y=0.15, padding=[20, 10])
        instruction = Label(
            text=tr("tap_to_return"),  # Au lieu de "Touchez la carte pour revenir"
            font_size="16sp",
            color=[0.7, 0.7, 0.7, 1],
            halign='center',
            italic=True
        )
        footer.add_widget(instruction)
        layout.add_widget(footer)
        
        self.content = layout
        
        # Animation d'entrée
        self.opacity = 0
        entrance_anim = Animation(opacity=1, duration=0.3)
        entrance_anim.start(self)
    
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def close_fullscreen(self, instance):
        exit_anim = Animation(opacity=0, duration=0.2)
        exit_anim.bind(on_complete=lambda *args: self.dismiss())
        exit_anim.start(self)


class LoadingPopup(Popup):
    """Popup de chargement avec animation d'images de dos de cartes"""
    def __init__(self, **kwargs):
        super(LoadingPopup, self).__init__(**kwargs)
        self.title = ""
        self.size_hint = (0.7, 0.5)
        self.auto_dismiss = False
        self.separator_height = 0

        layout = BoxLayout(orientation="vertical", spacing=10, padding=[20, 20, 20, 20])

        # Label de chargement
        self.loading_label = Label(
            text=tr("concentrating"),
            font_size="18sp",
            color=[0.9, 0.7, 0.3, 1],
            halign='center'
        )
        layout.add_widget(self.loading_label)

        # Zone animation
        self.anim_zone = FloatLayout(size_hint_y=0.8)
        layout.add_widget(self.anim_zone)

        # Deux tas fixes
        self.left_stack = Image(
            source="tarot_img/Back.jpg",
            size_hint=(0.25, 0.7),
            pos_hint={'x': 0.05, 'center_y': 0.5},
            opacity=1
        )
        self.right_stack = Image(
            source="tarot_img/Back.jpg",
            size_hint=(0.25, 0.7),
            pos_hint={'x': 0.7, 'center_y': 0.5},
            opacity=1
        )
        self.anim_zone.add_widget(self.left_stack)
        self.anim_zone.add_widget(self.right_stack)

        # Carte animée (au départ sur le tas de gauche)
        self.animated_card = Image(
            source="tarot_img/Back.jpg",
            size_hint=(0.25, 0.7),
            pos_hint={'x': 0.05, 'center_y': 0.5},
            opacity=1
        )
        self.anim_zone.add_widget(self.animated_card)

        self.content = layout

        # Lance l'animation
        self.shuffle_direction = "right"
        self.shuffle_anim = None
        self.start_shuffle_animation()

        Clock.schedule_once(lambda dt: self.update_message(tr("preparing_arcana")), 1.5)
        Clock.schedule_once(lambda dt: self.update_message(tr("drawing_card")), 3)

    def start_shuffle_animation(self):
        # Animation de gauche à droite ou droite à gauche
        if self.shuffle_direction == "right":
            anim = Animation(pos_hint={'x': 0.7, 'center_y': 0.5}, duration=0.4)
            anim.bind(on_complete=lambda *a: self.switch_shuffle_direction())
            anim.start(self.animated_card)
        else:
            anim = Animation(pos_hint={'x': 0.05, 'center_y': 0.5}, duration=0.4)
            anim.bind(on_complete=lambda *a: self.switch_shuffle_direction())
            anim.start(self.animated_card)

    def switch_shuffle_direction(self):
        # Change de direction et relance l'animation
        self.shuffle_direction = "left" if self.shuffle_direction == "right" else "right"
        self.start_shuffle_animation()

    def update_message(self, message):
        self.loading_label.text = message

    def on_dismiss(self):
        # Stoppe l'animation si besoin (optionnel)
        if self.shuffle_anim:
            self.shuffle_anim.cancel_all(self.animated_card)


class RootScreen(ScreenManager):
    """Gestionnaire d'écrans"""
    
    def __init__(self, **kwargs):
        super(RootScreen, self).__init__(**kwargs)
        print("RootScreen initialisé")


class CardScreen(Screen):
    """Écran principal"""
    
    def __init__(self, **kwargs):
        super(CardScreen, self).__init__(**kwargs)
        print("CardScreen créé")
        
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        
        # Background
        with layout.canvas.before:
            Color(0.2, 0.1, 0.3, 1)
            self.bg = Rectangle(pos=layout.pos, size=layout.size)
            if os.path.exists("tarot_img/bg.jpg"):
                self.bg.source = "tarot_img/bg.jpg"
                print("Background chargé")
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Titre
        self.title_label = Label(
            text=tr("app_title"),
            font_size="24sp",
            color=[0.9, 0.7, 0.3, 1],
            size_hint_y=0.15,
            bold=True
        )
        layout.add_widget(self.title_label)
        
        # Zone carte
        card_container = FloatLayout(size_hint_y=0.7)
        
        self.card_image = Image(
            source="tarot_img/Back.jpg",
            size_hint=(0.8, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        self.draw_button = Button(
            text="",
            background_color=[0, 0, 0, 0],
            size_hint=(0.8, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.draw_button.bind(on_press=self.draw_card)
        
        card_container.add_widget(self.card_image)
        card_container.add_widget(self.draw_button)
        layout.add_widget(card_container)
        
        # Instructions
        self.instructions_label = Label(
            text=tr("draw_instruction"),
            font_size="18sp",
            color=[0.7, 0.5, 0.3, 1],
            size_hint_y=0.15,
            halign='center'
        )
        layout.add_widget(self.instructions_label)
        
        # Bannière pub (cachée par défaut)
        self.ad_banner = Label(
            text=tr("crystals_ad"),  # ou une autre pub de ton choix
            font_size="16sp",
            color=[1, 0.8, 0.2, 1],
            size_hint_y=0.08,
            halign='center',
            valign='middle'
        )
        self.ad_banner.opacity = 0
        layout.add_widget(self.ad_banner)
        
        self.add_widget(layout)
    
    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size
    
    def draw_card(self, instance):
        print("=== NOUVEAU TIRAGE ===")
        
        # Animation
        click_anim = Animation(opacity=0.3, duration=0.1)
        click_anim += Animation(opacity=1, duration=0.1)
        click_anim.start(self.draw_button)
        
        # Popup de chargement
        self.loading_popup = LoadingPopup()
        self.loading_popup.open()
        
        # Tirage après 4 secondes
        Clock.schedule_once(self.perform_card_draw, 4)
    
    def perform_card_draw(self, dt):
        try:
            cards_signification = get_cards_signification()
            cards = list(cards_signification.keys())
            drawn_card = random.choice(cards)
            drawn_state = random.choice(["droite", "a l'envers"])

            print(f"Carte tirée: {drawn_card} - {drawn_state}")
            print(f"📊 Lecture #{READING_COUNT + 1}")

            if hasattr(self, 'loading_popup'):
                self.loading_popup.dismiss()

            def show_response_screen():
                if self.manager:
                    response_screen = self.manager.get_screen("response_screen")
                    response_screen.setup_card(drawn_card, drawn_state)
                    self.manager.current = "response_screen"

            # Afficher la popup pub si besoin
            if should_show_ad():
                print("Affichage écran pub maximisé")
                popup = AdsPopup(on_close_callback=show_response_screen)
                popup.open()
            else:
                show_response_screen()

        except Exception as e:
            print(f"Erreur tirage: {e}")
            if hasattr(self, 'loading_popup'):
                self.loading_popup.dismiss()
    
    def on_enter(self, *args):
        print("Entrée sur CardScreen")


class ResponseScreen(Screen):
    """Écran de réponse avec image cliquable"""
    
    def __init__(self, **kwargs):
        super(ResponseScreen, self).__init__(**kwargs)
        
        self.current_card_name = ""
        self.current_card_state = ""
        
        self.typewriter_event = None
        self.typewriter_full_text = ""
        self.typewriter_index = 0

        from kivy.uix.scrollview import ScrollView
        
        main_layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        
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
            text="Votre carte",
            font_size="22sp",
            color=[0.9, 0.7, 0.3, 1],
            size_hint_y=0.1,
            bold=True
        )
        main_layout.add_widget(self.card_name_label)
        
        # État
        self.card_state_label = Label(
            text="",
            font_size="18sp",
            color=[0.8, 0.6, 0.4, 1],
            size_hint_y=0.05,
            bold=True
        )
        main_layout.add_widget(self.card_state_label)
        
        # Mots-clés
        self.keywords_label = Label(
            text="",
            font_size="14sp",
            color=[0.7, 0.7, 0.9, 1],
            size_hint_y=0.05,
            italic=True
        )
        main_layout.add_widget(self.keywords_label)
        
        # Container image CLIQUABLE
        image_container = FloatLayout(size_hint_y=0.25)
        
        self.card_image = Image(
            source="tarot_img/Back.jpg",
            size_hint=(0.8, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            allow_stretch=True,
            keep_ratio=True
        )
        
        # Bouton invisible sur l'image
        self.image_button = Button(
            text="",
            background_color=[0, 0, 0, 0],
            size_hint=(0.8, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.image_button.bind(on_press=self.show_fullscreen_card)
        
        # Indication
        overlay_label = Label(
            text="🔍 Touchez pour agrandir",
            font_size="12sp",
            color=[1, 1, 1, 0.7],
            size_hint=(0.8, 0.15),
            pos_hint={'center_x': 0.5, 'bottom': 1},
            halign='center'
        )
        
        image_container.add_widget(self.card_image)
        image_container.add_widget(self.image_button)
        image_container.add_widget(overlay_label)
        main_layout.add_widget(image_container)
        
        # Signification avec scroll
        scroll = ScrollView(size_hint_y=0.4)
        self.signification_label = Label(
            text="Chargement...",
            font_size="16sp",
            color=[1, 1, 1, 1],
            halign='center',
            valign='top',
            size_hint_y=None,
            text_size=(self.width * 0.9, None)
        )
        self.signification_label.bind(
            texture_size=lambda instance, value: setattr(instance, 'height', value[1])
        )
        scroll.add_widget(self.signification_label)
        main_layout.add_widget(scroll)
        
        # Bouton retour
        self.back_btn = Button(
            text=tr("new_reading"),
            size_hint=(0.7, 0.15),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="18sp",
            bold=True
        )
        
        with self.back_btn.canvas.before:
            Color(0.6, 0.4, 0.2, 1.0)
            self.back_btn_bg = RoundedRectangle(
                pos=self.back_btn.pos,
                size=self.back_btn.size,
                radius=[25, 25, 25, 25]
            )
        
        self.back_btn.bind(pos=self.update_button_canvas, size=self.update_button_canvas)
        self.back_btn.bind(on_press=self.go_back)
        main_layout.add_widget(self.back_btn)
        
        # Bannière pub (cachée par défaut)
        self.ad_banner = Label(
            text=tr("crystals_ad"),  # ou une autre pub de ton choix
            font_size="16sp",
            color=[1, 0.8, 0.2, 1],
            size_hint_y=0.08,
            halign='center',
            valign='middle'
        )
        self.ad_banner.opacity = 0
        main_layout.add_widget(self.ad_banner)
        
        self.add_widget(main_layout)
    
    def show_fullscreen_card(self, instance):
        """NOUVELLE FONCTIONNALITÉ: Affiche la carte en plein écran"""
        print(f"Affichage plein écran: {self.current_card_name}")
        
        # Animation click
        click_anim = Animation(opacity=0.7, duration=0.1)
        click_anim += Animation(opacity=1, duration=0.1)
        click_anim.start(self.card_image)
        
        # Popup plein écran
        fullscreen_popup = FullScreenCardPopup(
            card_image_source=self.card_image.source,
            card_name=self.current_card_name,
            card_state=self.card_state_label.text
        )
        fullscreen_popup.open()
    
    def setup_card(self, card_name, state):
        print(f"=== SETUP CARTE: {card_name} - {state} ===")
        
        # Sauvegarder pour le plein écran
        self.current_card_name = card_name
        self.current_card_state = state
        
        # Convertir le nom selon la langue détectée
        display_card_name = get_card_name_for_lang(card_name, CURRENT_LANG)
        print(f"Nom affiché: {display_card_name}")
        
        # Nom affiché
        self.card_name_label.text = display_card_name
        
        # État traduit avec conversion pour l'anglais
        if state == "a l'envers":
            self.card_state_label.text = tr("reversed")
            lookup_state = "reversed"
        else:
            self.card_state_label.text = tr("upright") 
            lookup_state = "upright"
        
        # Image (garder le nom français pour les fichiers)
        try:
            image_path = get_card_image_path(card_name, state)
            if os.path.exists(image_path):
                self.card_image.source = image_path
                print(f"✓ Image chargée: {image_path}")
            else:
                print(f"✗ Image non trouvée: {image_path}")
        except Exception as e:
            print(f"✗ Erreur image: {e}")
        
        # Signification avec le bon nom de carte selon la langue
        try:
            cards_signification = get_cards_signification()
            lookup_name = display_card_name if CURRENT_LANG == "en" else card_name
            print(f"Recherche signification pour: {lookup_name}")
            
            if lookup_name in cards_signification:
                card_data = cards_signification[lookup_name]
                print(f"Clés disponibles: {list(card_data.keys())}")
                
                # Mots-clés
                if lookup_state in card_data:
                    self.keywords_label.text = f"💫 {card_data[lookup_state].upper()} 💫"
                
                # Signification détaillée
                from signification_pt import get_card_state, get_signification_key  # Importer ici pour éviter les erreurs globales
                lookup_state = get_card_state(state)  # <-- utilise la fonction du module PT
                signif_key = get_signification_key(lookup_state)
                if signif_key in card_data:
                    signification = str(card_data[signif_key])
                    self.start_typewriter(signification)
                    print(f"✓ Signification trouvée avec clé: {signif_key}")
                else:
                    # Fallback sur les mots-clés si pas de signification détaillée
                    if lookup_state in card_data:
                        self.start_typewriter(f"Keywords: {card_data[lookup_state]}")
                    else:
                        self.start_typewriter("No description available")
                
                Clock.schedule_once(self.setup_text_wrapping, 0.1)
            else:
                self.signification_label.text = f"Card '{lookup_name}' not found"
                print(f"✗ Carte '{lookup_name}' non trouvée dans: {list(cards_signification.keys())[:5]}...")
                
        except Exception as e:
            print(f"✗ Erreur signification: {e}")
            self.signification_label.text = "Error loading signification"
    
    def setup_text_wrapping(self, dt):
        if self.signification_label and self.parent:
            self.signification_label.text_size = (self.width * 0.9, None)
            self.signification_label.height = self.signification_label.texture_size[1]
    
    def update_button_canvas(self, instance, value):
        self.back_btn_bg.pos = instance.pos
        self.back_btn_bg.size = instance.size
    
    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size
    
    def go_back(self, instance):
        if self.manager:
            self.manager.current = "main_screen"
    
    def show_ad_banner(self):
        self.ad_banner.opacity = 1

    def hide_ad_banner(self):
        self.ad_banner.opacity = 0

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
            return False  # Stop le schedule


class AdsPopup(Popup):
    def __init__(self, on_close_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = ""
        self.size_hint = (0.95, 0.95)
        self.auto_dismiss = False
        self.separator_height = 0
        self.on_close_callback = on_close_callback

        layout = BoxLayout(orientation="vertical", spacing=20, padding=20)

        ads = [
            "💎 Crystals & Minerals Shop - Free shipping 💎",
            "💕 Find Love with Astrology+ 💕",
            "🔮 Professional Tarot Course 🔮"
        ]
        for ad_text in ads:
            ad_label = Label(
                text=ad_text,
                font_size="16sp",
                color=[1, 0.8, 0.2, 1],
                halign='center',
                valign='middle',
                size_hint_x=1,
                size_hint_y=None,
                height=80,
                text_size=(int(0.95 * 300), None),
                shorten=False
            )
            layout.add_widget(ad_label)

        self.countdown_seconds = 7
        self.next_btn = Button(
            text=f"✨ New reading ({self.countdown_seconds}s) ✨",
            size_hint=(0.7, 0.15),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="18sp",
            bold=True,
            disabled=True
        )
        with self.next_btn.canvas.before:
            Color(0.6, 0.4, 0.2, 1.0)
            self.btn_bg = RoundedRectangle(
                pos=self.next_btn.pos,
                size=self.next_btn.size,
                radius=[25, 25, 25, 25]
            )
        self.next_btn.bind(pos=self.update_btn_canvas, size=self.update_btn_canvas)
        self.next_btn.bind(on_press=self.close_popup)
        layout.add_widget(self.next_btn)

        self.content = layout
        self.countdown_event = Clock.schedule_interval(self.update_countdown, 1)

    def update_btn_canvas(self, instance, value):
        self.btn_bg.pos = instance.pos
        self.btn_bg.size = instance.size

    def update_countdown(self, dt):
        self.countdown_seconds -= 1
        if self.countdown_seconds > 0:
            self.next_btn.text = f"✨ New reading ({self.countdown_seconds}s) ✨"
        else:
            self.next_btn.text = "✨ New reading"
            self.next_btn.disabled = False
            if self.countdown_event:
                self.countdown_event.cancel()

    def close_popup(self, instance):
        self.dismiss()
        if self.on_close_callback:
            self.on_close_callback()


class TarotApp(App):
    def build(self):
        print("=== CONSTRUCTION APP TAROT ===")
        self.title = tr("app_title")
        
        sm = RootScreen()
        sm.add_widget(CardScreen(name="main_screen"))
        sm.add_widget(ResponseScreen(name="response_screen"))
        sm.current = "main_screen"
        
        return sm
    
    def on_start(self):
        print("=== APP TAROT DÉMARRÉE ===")


if __name__ == "__main__":
    TarotApp().run()