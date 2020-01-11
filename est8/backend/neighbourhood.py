from dataclasses import dataclass
from itertools import chain
from typing import List

from est8.backend.errors import HousePlacementError, FencePlacementError
from est8.backend.definitions import NeighbourhoodDefinition
from est8.backend.house import House
from est8.backend.street import Street


@dataclass
class Neighbourhood:
    definition: NeighbourhoodDefinition
    streets: List[Street]

    @classmethod
    def new(cls, definition: NeighbourhoodDefinition) -> "Neighbourhood":
        return cls(
            definition=definition,
            streets=[
                Street.new(street_definition)
                for street_definition in definition.streets
            ],
        )

    def assert_place_house_is_valid(self, street_no: int) -> None:
        if street_no < 0 or street_no >= len(self.streets):
            raise HousePlacementError("Street number is not valid.")

    def place_house(self, street_no: int, plot_no: int, house: House) -> None:
        self.assert_place_house_is_valid(street_no)
        self.streets[street_no].place_house(plot_no, house)

    def assert_place_fence_is_valid(self, street_no: int) -> None:
        if street_no < 0 or street_no >= len(self.streets):
            raise FencePlacementError("Street number is not valid.")

    def place_fence(self, street_no: int, fence_index: int) -> None:
        self.assert_place_fence_is_valid(street_no)
        self.streets[street_no].place_fence(fence_index)

    def get_all_estates(self) -> List[int]:
        return list(chain(*(street.get_complete_estates() for street in self.streets)))
