from enum import Enum, auto
from typing import Optional

from shimmer.display.data_structures import Color
from shimmer.display.alignment import (
    HorizontalAlignment,
    VerticalAlignment,
)
from shimmer.display.components.box import Box, BoxDefinition
from shimmer.display.widgets.text_box import TextBoxDefinition, TextBox, LabelDefinition

from ..backend.definitions import CardDefinition, CardPair


class CardDisplay(Box):

    size = 100, 60

    class CardFacingEnum(Enum):
        number = auto()
        action = auto()

    def __init__(self):
        super(CardDisplay, self).__init__(
            BoxDefinition(
                width=self.size[0],
                height=self.size[1],
                dynamic_size=False,
                background_color=Color(40, 40, 40),
            )
        )
        self.card: Optional[CardDefinition] = None
        self.text_box = TextBox(TextBoxDefinition(label=LabelDefinition("",),))
        self.text_box.set_position_in_alignment_with(
            self, HorizontalAlignment.center, VerticalAlignment.center
        )
        self.add(self.text_box)

    def set_card(self, card: CardDefinition, facing: CardFacingEnum) -> None:
        self.card = card
        if facing == self.CardFacingEnum.number:
            self.text_box.text = str(self.card.number)
        elif facing == self.CardFacingEnum.action:
            self.text_box.text = str(self.card.action.name)

        # And re-align the text within this Box.
        self.text_box.set_position_in_alignment_with(
            self, HorizontalAlignment.center, VerticalAlignment.center
        )


class CardPairDisplay(Box):
    def __init__(self):
        super(CardPairDisplay, self).__init__()

        self.card_pair: Optional[CardPair] = None

        self.number_card_display: CardDisplay = CardDisplay()
        self.number_card_display.position = 0, CardDisplay.size[1] + 10
        self.action_card_display: CardDisplay = CardDisplay()

        self.add(self.number_card_display, z=-1)
        self.add(self.action_card_display, z=-1)

        child_boundary_rect = self.bounding_rect_of_children()
        # TODO don't use set size
        self._set_size(
            width=child_boundary_rect.width, height=child_boundary_rect.height
        )

    def set_card_pair(self, card_pair: CardPair) -> None:
        self.card_pair = card_pair

        self.number_card_display.set_card(
            self.card_pair.number_card, facing=CardDisplay.CardFacingEnum.number
        )
        self.action_card_display.set_card(
            self.card_pair.action_card, facing=CardDisplay.CardFacingEnum.action
        )
