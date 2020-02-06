from typing import Callable, List, Tuple

from shimmer.display.components.box import Box
from shimmer.display.components.box_layout import BoxRow
from shimmer.display.data_structures import Color
from shimmer.display.widgets.button import Button, ButtonDefinition
from shimmer.display.widgets.multiple_choice_buttons import (
    MultipleChoiceButtonsDefinition,
    MultipleChoiceButtons,
    MultipleChoiceQuestionDefinition,
)
from .card import CardPairDisplay
from .input_handler import InputHandler
from ..backend.definitions import ActionEnum, CardDefinition, CardPair, GameDefinition


class FreeChoiceDeckDisplay(Box):
    def __init__(self, input_handler: InputHandler):
        super(FreeChoiceDeckDisplay, self).__init__()
        self.input_handler: InputHandler = input_handler
        self.number_buttons = self.create_number_buttons()
        self.action_buttons = self.create_action_buttons()
        self._last_number = 1
        self._last_action = ActionEnum.invest

        self.number_buttons.position = 0, 50
        self.add(self.number_buttons)
        self.add(self.action_buttons)

    def create_number_buttons(self) -> BoxRow:
        buttons = []
        for number in range(1, 16):
            defn = ButtonDefinition(
                text=str(number),
                width=30,
                height=30,
                on_press=self._make_on_number_click_callback(number),
            )
            buttons.append(Button(defn))
        layout = BoxRow(buttons)
        return layout

    def create_action_buttons(self) -> BoxRow:
        buttons = []
        for index, action in enumerate(ActionEnum):
            defn = ButtonDefinition(
                dynamic_size=True,
                text=str(action),
                on_press=self._make_on_action_click_callback(action),
            )
            buttons.append(Button(defn))
        layout = BoxRow(buttons)
        return layout

    def _make_on_number_click_callback(self, number: int) -> Callable[[], bool]:
        def inner(*_, **__):
            return self.on_number_click(number)

        return inner

    def _make_on_action_click_callback(self, action: ActionEnum) -> Callable[[], bool]:
        def inner(*_, **__):
            return self.on_action_click(action)

        return inner

    def on_number_click(self, number: int) -> bool:
        self._last_number = number
        self.input_handler.chosen_card_pair = CardPair(
            CardDefinition(self._last_number, action=self._last_action),
            CardDefinition(self._last_number, action=self._last_action),
        )
        return True

    def on_action_click(self, action: ActionEnum) -> bool:
        self._last_action = action
        self.input_handler.chosen_card_pair = CardPair(
            CardDefinition(self._last_number, action=self._last_action),
            CardDefinition(self._last_number, action=self._last_action),
        )
        return True


class RandomDeckDisplay(Box):
    def __init__(self, game_definition: GameDefinition, input_handler: InputHandler):
        super(RandomDeckDisplay, self).__init__()
        self.input_handler: InputHandler = input_handler
        self.input_handler.add_house_place_callback(self.deselect_cards)
        self.input_handler.add_draw_new_cards_callback(self.set_card_pairs)
        self.game_definition = game_definition

        self.card_displays = self._create_card_displays()
        card_displays_definition = MultipleChoiceButtonsDefinition(
            question=MultipleChoiceQuestionDefinition(
                text="", choices=self.card_displays, on_select=self.on_card_chosen,
            ),
            button=ButtonDefinition(
                base_color=Color(0, 0, 0, 0),
                hover_color=Color(0, 0, 200, 200),
                depressed_color=Color(0, 150, 0, 100),
                width=self.card_displays[0].rect.width,
                height=self.card_displays[0].rect.height,
            ),
        )
        self.card_display_layout = MultipleChoiceButtons(card_displays_definition)
        self.add(self.card_display_layout)

    def _create_card_displays(self) -> List[CardPairDisplay]:
        """Create the card displays for each card draw option."""
        displays = []
        for index in range(self.game_definition.num_cards_drawn_at_once):
            display = CardPairDisplay()
            # display.position = index * (display.rect.width + 20), 0
            # self.add(display)
            displays.append(display)
        return displays

    def on_card_chosen(
        self, _, card_display: CardPairDisplay, is_selected: bool
    ) -> None:
        if is_selected:
            self.input_handler.chosen_card_pair = card_display.card_pair

    def set_card_pairs(self, card_pairs: Tuple[CardPair, ...]) -> None:
        self.card_display_layout.set_to_defaults()
        for card_pair, card_display in zip(card_pairs, self.card_displays):
            card_display.set_card_pair(card_pair)

    def deselect_cards(self):
        self.card_display_layout.set_to_defaults()
