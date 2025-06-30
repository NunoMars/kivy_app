__version__ = "0.01"

import os
import random

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image

from signification import cards_signification


class RootScreen(ScreenManager):
    pass


class CardScreen(Screen):
    """Ecran principal de l'application"""

    def __init__(self, **kwargs):
        super(CardScreen, self).__init__(**kwargs)


class LoadingPopup(Popup):
    def __init__(self, **kwargs):
        super(LoadingPopup, self).__init__(**kwargs)
        self.title = "JE TIRE UNE CARTE..."
        # self.background = ""
        self.background = "tarot_img/bg.jpg"
        content_layout = BoxLayout(orientation="vertical")
        # Maintenant que Pillow est installé, essayons le GIF original
        gif_path = os.path.join(os.path.dirname(__file__), "tarot_img", "carte-unscreen.gif")
        animated_card = Image(source=gif_path, anim_delay=0.1)
        content_layout.add_widget(animated_card)
        self.content = content_layout


class FullScreenImagePopup(BoxLayout):
    def __init__(self, image_path, **kwargs):
        super(FullScreenImagePopup, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.image = Image(source=image_path, size_hint=(1, 1))
        self.add_widget(self.image)


class CardResponseScreen(Screen):
    """Ecran de réponse de l'application"""

    def __init__(self, **kwargs):
        super(CardResponseScreen, self).__init__(**kwargs)
        self.path = "tarot_img/MajorArcanaCards"
        self.cards = list(cards_signification.keys())
        self.states = ["a l'endroit", "a l'envers"]
        self.card_title = None
        self.states_label = None
        self.card_text = None
        self.card_image = None

    def on_kv_post(self, base_widget):
        # Link Python attributes to widgets defined in the .kv file by their ids
        self.card_title = self.ids.get("card_title")
        self.states_label = self.ids.get("states_label")
        self.card_text = self.ids.get("card_text")
        self.card_image = self.ids.get("card_image")

    def on_enter(self, *args):
        self.show_loading_popup()  # Affiche la fenêtre modale d'attente

    def show_loading_popup(self):
        self.loading_popup = LoadingPopup()
        self.loading_popup.open()
        Clock.schedule_once(
            self.load_card_data, 3
        )  # Appeler load_card_data après un court délai

    def load_card_data(self, dt):
        """Charge les données de la carte après un court délai simulé (0.1 seconde)"""
        try:
            self.drawn_card = random.choice(self.cards)
            self.state = random.choice(self.states)
            if self.card_title is not None:
                self.card_title.text = f"{self.drawn_card}\n{self.state}"
            if self.states_label is not None:
                self.states_label.text = str(
                    cards_signification[self.drawn_card][self.state]
                )

            if self.state == "a l'envers":
                image_file_name = f"{self.drawn_card} {self.state}.jpg"
            else:
                image_file_name = f"{self.drawn_card}.jpg"
            image_path = os.path.join(
                self.path, image_file_name
            )  # Construct full path

            # Print the image path for debugging
            # print("Image Path:", image_path)

            if os.path.exists(image_path):
                if self.card_image is not None:
                    self.card_image.source = image_path
                    self.card_image.bind(
                        on_touch_down=self.on_image_click
                    )  # Bind the touch event
                else:
                    print("card_image is None, cannot set source.")
            else:
                print("Image not found:", image_path)

            if self.card_text is not None:
                self.card_text.text = str(
                    cards_signification[self.drawn_card][
                        f"signification {self.state}"
                    ]
                )
        except Exception as e:
            # Handle any exceptions and print the error message
            print("Error loading card data:", e)

        self.loading_popup.dismiss()  # Close the loading popup

    def reset(self):
        """Réinitialise l'écran de réponse pour un nouveau tirage"""
        if self.card_title is not None:
            self.card_title.text = ""
        if self.states_label is not None:
            self.states_label.text = ""
        if self.card_text is not None:
            self.card_text.text = ""
        if self.card_image is not None:
            self.card_image.source = "tarot_img/Back.jpg"
        if hasattr(self, "full_screen_popup"):
            self.remove_widget(self.full_screen_popup)
            del self.full_screen_popup

    def on_image_click(self, instance, touch):
        """Affiche l'image en plein écran si l'utilisateur clique dessus"""
        if self.card_image is not None and self.card_image.collide_point(*touch.pos):
            if hasattr(self, "full_screen_popup"):
                self.remove_widget(self.full_screen_popup)
                del self.full_screen_popup
            else:
                if self.state == "a l'envers":
                    image_path = f"tarot_img/MajorArcanaCards/{self.drawn_card} {self.state}.jpg"
                else:
                    image_path = (
                        f"tarot_img/MajorArcanaCards/{self.drawn_card}.jpg"
                    )

                # Create a full-screen popup with the image
                self.full_screen_popup = FullScreenImagePopup(image_path)
                self.add_widget(self.full_screen_popup)


class MaCarteDeTarotApp(App):
    """Application principale"""

    def __init__(self, **kwargs):
        super(MaCarteDeTarotApp, self).__init__(**kwargs)

    def build(self):
        """Build the app"""
        self.title = "Ma Carte de Tarot"
        self.icon = "tarot_img/tapis.ico"

        return RootScreen()


if __name__ == "__main__":
    MaCarteDeTarotApp().run()
