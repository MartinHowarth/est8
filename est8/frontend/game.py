from est8.backend.player import Player
from est8.backend.definitions import GameDefinition
from est8.backend.neighbourhood import Neighbourhood
from est8.frontend.input_handler import InputHandler
from est8.frontend.neighbourhood import NeighbourhoodDisplay
from est8.frontend.deck import FreeChoiceDeckDisplay, RandomDeckDisplay
from est8.frontend.score_displays import ParkDisplay

from shimmer.display.components.box import Box


class GameDisplay(Box):
    def __init__(self, game_definition: GameDefinition, debug_mode: bool = False):
        super(GameDisplay, self).__init__()
        player = Player.new(game_definition)
        input_handler = InputHandler(game_definition)
        if debug_mode:
            deck_display = FreeChoiceDeckDisplay(input_handler)
        else:
            deck_display = RandomDeckDisplay(game_definition, input_handler)

        # neighbourhood = Neighbourhood.new(game_definition.neighbourhood)
        neighbourhood_display = NeighbourhoodDisplay(player, input_handler)
        neighbourhood_display.position = 50, 50

        input_handler.draw_new_cards()

        self.add(neighbourhood_display)
        self.add(deck_display)
        deck_display.position = (
            50,
            neighbourhood_display.bounding_rect_of_children().height + 100,
        )
