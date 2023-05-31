import os
import random
import kivy

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Rectangle

from kivy.uix.floatlayout import FloatLayout
from PIL import Image as PILImage
from signification import cards_signification


class MaCarteDeTarotApp(App):
    """Application principale"""

    def __init__(self, **kwargs):
        super(MaCarteDeTarotApp, self).__init__(**kwargs)
        self.path = "tarot_img/MajorArcanaCards"
        self.cards = list(
            cards_signification.keys()
        )  # Remplacez par vos cartes de tarot réelles

    def build(self):
        """Build the app"""
        self.theRoot = FloatLayout()
        # draw the background
        with self.theRoot.canvas:
            self.rect = Rectangle(
                source="tarot_img/bg.jpg",
                size=self.theRoot.size,
                pos=self.theRoot.pos,
                keep_ratio=False,
                allow_stretch=True,
            )
        self.theRoot.bind(on_size=self.update)

        self.card_label = "Cliquez sur le bouton pour une carte de tarot aléatoire"
        self.label = Label(
            text=self.card_label,
            size_hint=(None, None),
            pos_hint={"center_x": 0.50, "center_y": 0.90},
            font_size="30sp",
        )
        self.theRoot.add_widget(self.label)

        self.states_label = ""
        self.label_states = Label(
            text=self.states_label,
            size_hint=(None, None),
            pos_hint={"center_x": 0.63, "center_y": 0.90},
            font_size="20sp",
        )
        self.label_states.text_size = (500, 200)
        self.label_states.multiline = True
        self.theRoot.add_widget(self.label_states)

        self.card_image = Image(
            source="tarot_img/Back.jpg",
            size_hint=(0.52, 0.52),
            pos_hint={"center_x": 0.15, "center_y": 0.60},
        )  # Image par défaut pour commencer

        self.theRoot.add_widget(self.card_image)

        self.text_label = ""
        self.text_label = Label(
            text=self.states_label,
            size_hint=(None, None),
            pos_hint={"center_x": 0.63, "center_y": 0.90},
            font_size="18sp",
        )
        self.text_label.text_size = (500, 600)
        self.text_label.multiline = True
        self.theRoot.add_widget(self.text_label)

        draw_button = Button(text="Tirer une carte")
        draw_button.bind(on_press=self.draw_card)
        draw_button.size_hint = (0.43, 0.10)
        draw_button.pos_hint = {"center_x": 0.5, "center_y": 0.10}
        draw_button.border_radius = (2, 2, 2, 2)

        self.theRoot.add_widget(draw_button)

        Clock.schedule_once(self.update, -1)

        return self.theRoot

    def draw_card(self, instance):
        """Tire une carte de tarot aléatoire et affiche l'image correspondante"""

        states = ["a l'endroit", "a l'envers"]
        drawn_card = random.choice(self.cards)
        state = random.choice(states)

        self.label.text = f"{drawn_card} {state}"

        self.label_states.text = str(cards_signification[drawn_card][state])
        self.text_label.text = str(cards_signification[drawn_card]["signification"])

        if state == "a l'envers":
            if f"{drawn_card} {state}.jpg" not in os.listdir(
                "tarot_img/MajorArcanaCards"
            ):
                img = PILImage.open(f"tarot_img/MajorArcanaCards/{drawn_card}.jpg")
                img.rotate(180, expand=True).save(
                    f"tarot_img/MajorArcanaCards/{drawn_card} {state}.jpg"
                )

            image_path = f"tarot_img/MajorArcanaCards/{drawn_card} {state}.jpg"
            self.card_image.source = image_path
        else:
            image_path = f"tarot_img/MajorArcanaCards/{drawn_card}.jpg"  # Chemin de l'image correspondante

            self.card_image.source = image_path

    def update(self, *args):
        # set the size and position of the background image
        self.rect.size = self.theRoot.size
        self.rect.pos = self.theRoot.pos


MaCarteDeTarotApp().run()
