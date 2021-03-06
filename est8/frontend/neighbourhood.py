import logging

from dataclasses import replace
from typing import List, Optional

from shimmer.display.components.box import ActiveBox

from ..backend.errors import Est8Error
from ..backend.definitions import ActionEnum
from ..backend.player import Player
from ..backend.house import House
from ..backend.neighbourhood import Neighbourhood
from .street import StreetDisplay
from .input_handler import InputHandler
from .deck import RandomDeckDisplay


log = logging.getLogger(__name__)


class NeighbourhoodDisplay(ActiveBox):
    def __init__(self, player: Player, input_handler: InputHandler):
        super(NeighbourhoodDisplay, self).__init__()
        self.player = player
        self.input_handler: InputHandler = input_handler
        self.streets: List[StreetDisplay] = [
            StreetDisplay(street, index, self.on_plot_click)
            for index, street in enumerate(self.player.neighbourhood.streets)
        ]
        max_x = max(
            [street.bounding_rect_of_children().width for street in self.streets]
        )
        for index, street in enumerate(reversed(self.streets)):
            width = street.bounding_rect_of_children().width
            street.position = max_x - width, index * 200
            self.add(street)

    def make_chosen_house(self, street_index: int, plot_index: int) -> Optional[House]:
        if self.input_handler.is_building_roundabout:
            return House(is_roundabout=True)
        elif self.input_handler.is_building_bis:
            return House(is_bis=True)
        elif self.input_handler.chosen_card_pair is not None:
            action = self.input_handler.chosen_card_pair.action_card.action
            can_have_pool = self.player.neighbourhood.definition.can_have_pool_at(
                street_index, plot_index
            )
            return House(
                number=self.input_handler.chosen_card_pair.number_card.number,
                built_by_temps=action == ActionEnum.temp,
                has_park=action == ActionEnum.park,
                has_pool=(action == ActionEnum.pool and can_have_pool),
            )
        return None

    def on_plot_click(self, street_index: int, plot_index: int) -> Optional[bool]:
        house = self.make_chosen_house(street_index, plot_index)

        if house is None:
            return None

        try:
            self.player.place_house(street_index, plot_index, house)
            plot = self.streets[street_index].plots[plot_index]
            plot.definition = replace(plot.definition, text=str(house))
            plot.update_label()
            self.streets[street_index].update()
        except Est8Error:
            # If we didn't successfully place it, then keep player input state
            # so they can try a different plot.
            log.info(f"Cannot place house {house} at {street_index=}, {plot_index=})")
            return None

        # Successfully placed a house - reset inputs.
        # If we didn't successfully place it, then keep input so they can try a different plot.
        self.input_handler.on_house_place()
        log.info(f"Placed house {house} at {street_index=}, {plot_index=})")
        return True
