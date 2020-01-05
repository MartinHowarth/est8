import cocos
import sys

from flipville.backend.definitions import GameDefinition
from flipville.frontend.game import GameDisplay


def main():
    director = cocos.director.director
    director.init(width=1400, height=800)
    director.window.position = 100, 100
    game_definition = GameDefinition.default()

    game_display = GameDisplay(game_definition)

    director.run(cocos.scene.Scene(game_display))


if __name__ == "__main__":
    sys.exit(main())
