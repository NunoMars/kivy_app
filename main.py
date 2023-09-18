__version__ = "0.01"

import os
import random

from kivy.app import App, Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image

from signification import cards_signification

Builder.load_file("macartedetarotapp.kv")


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
        animated_card = Image(source="tarot_img/carte.gif", anim_delay=0.1)
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
            self.card_title.text = f"{self.drawn_card}\n{self.state}"
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
                self.card_image.source = image_path
                self.card_image.bind(
                    on_touch_down=self.on_image_click
                )  # Bind the touch event
            else:
                print("Image not found:", image_path)

            self.card_text.text = str(
                cards_signification[self.drawn_card][
                    f"signification {self.state}"
                ]
            )
        except Exception as e:
            # Handle any exceptions and print the error message
            print("Error loading card data:", e)

        self.loading_popup.dismiss()  # Close the loading popup

    def on_image_click(self, instance, touch):
        """Affiche l'image en plein écran si l'utilisateur clique dessus"""
        if self.card_image.collide_point(*touch.pos):
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
        self.icon = "tarot_img/icon.png"

        return RootScreen()


if __name__ == "__main__":
    MaCarteDeTarotApp().run()
