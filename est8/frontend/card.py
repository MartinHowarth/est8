from enum import Enum, auto
from typing import Optional

from shimmer.display.components.box import Box, BoxDefinition
from shimmer.display.data_structures import Color
from shimmer.display.widgets.text_box import TextBoxDefinition, TextBox
from ..backend.definitions import CardDefinition, CardPair


class CardFacingEnum(Enum):
    number = auto()
    action = auto()


class CardDisplay(Box):

    size = 100, 60

    def __init__(self):
        super(CardDisplay, self).__init__(
            BoxDefinition(
                width=self.size[0],
                height=self.size[1],
                background_color=Color(40, 40, 40),
            )
        )
        self.card: Optional[CardDefinition] = None
        self.text_box = TextBox(TextBoxDefinition())
        self.add(self.text_box)

    def set_card(self, card: CardDefinition, facing: CardFacingEnum) -> None:
        self.card = card
        if facing == CardFacingEnum.number:
            self.text_box.text = str(self.card.number)
        elif facing == CardFacingEnum.action:
            self.text_box.text = str(self.card.action.name)

        # And align the text within this Box.
        self.text_box.align_anchor_with_other_anchor(self)


class CardPairDisplay(Box):
    def __init__(self):
        super(CardPairDisplay, self).__init__()

        self.card_pair: Optional[CardPair] = None

        self.number_card_display: CardDisplay = CardDisplay()
        self.number_card_display.position = 0, CardDisplay.size[1] + 10
        self.action_card_display: CardDisplay = CardDisplay()

        self.add(self.number_card_display)
        self.add(self.action_card_display)

    def set_card_pair(self, card_pair: CardPair) -> None:
        self.card_pair = card_pair

        self.number_card_display.set_card(
            self.card_pair.number_card, facing=CardFacingEnum.number
        )
        self.action_card_display.set_card(
            self.card_pair.action_card, facing=CardFacingEnum.action
        )
