from flipville.backend.player import Player
from flipville.backend.definitions import GameDefinition
from flipville.backend.neighbourhood import Neighbourhood
from flipville.frontend.input_handler import InputHandler
from flipville.frontend.neighbourhood import NeighbourhoodDisplay
from flipville.frontend.deck import FreeChoiceDeckDisplay, RandomDeckDisplay
from flipville.frontend.score_displays import ParkDisplay

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
