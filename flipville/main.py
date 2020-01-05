import cocos
import sys

from flipville.backend.player import Player
from flipville.backend.definitions import GameDefinition
from flipville.backend.neighbourhood import Neighbourhood
from flipville.frontend.input_handler import InputHandler
from flipville.frontend.neighbourhood import NeighbourhoodDisplay
from flipville.frontend.deck import FreeChoiceDeckDisplay, RandomDeckDisplay


def main():
    director = cocos.director.director
    director.init(width=1400, height=800)
    director.window.position = 100, 100
    game_definition = GameDefinition.default()
    player = Player.new(game_definition)
    input_handler = InputHandler(game_definition)
    # deck_display = FreeChoiceDeckDisplay(input_handler)
    deck_display = RandomDeckDisplay(game_definition, input_handler)
    deck_display.position = 100, 500

    neighbourhood = Neighbourhood.new(game_definition.neighbourhood)
    neighbourhood_display = NeighbourhoodDisplay(neighbourhood, input_handler)
    neighbourhood_display.position = 100, 50

    input_handler.draw_new_cards()

    director.run(cocos.scene.Scene(neighbourhood_display, deck_display))


if __name__ == "__main__":
    sys.exit(main())
