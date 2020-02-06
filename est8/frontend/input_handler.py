from typing import Optional, List, Callable, Tuple

from est8.backend.definitions import CardPair, GameDefinition


class InputHandler:
    def __init__(self, game_definition: GameDefinition):
        self.game_definition = game_definition
        self.deck_generator = game_definition.generate_card_pairs()

        # Reference to the currently chosen card pair.
        self.chosen_card_pair: Optional[CardPair] = None
        self.is_building_roundabout: bool = False
        self.is_building_bis: bool = False

        self.on_house_place_callbacks: List[Callable[[], None]] = []
        self.on_draw_new_cards_callbacks: List[
            Callable[[Tuple[CardPair, ...]], None]
        ] = []

    def add_house_place_callback(self, callback: Callable[[], None]) -> None:
        self.on_house_place_callbacks.append(callback)

    def add_draw_new_cards_callback(
        self, callback: Callable[[Tuple[CardPair, ...]], None]
    ) -> None:
        self.on_draw_new_cards_callbacks.append(callback)

    def on_house_place(self) -> None:
        self.chosen_card_pair = None
        self.is_building_roundabout = False
        self.is_building_bis = False

        for func in self.on_house_place_callbacks:
            func()

        self.draw_new_cards()

    def draw_new_cards(self) -> None:
        next_cards = next(self.deck_generator)

        for callback in self.on_draw_new_cards_callbacks:
            callback(next_cards)
