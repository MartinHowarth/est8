from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Optional

from flipville.backend.errors import (
    InvestmentError,
    RoundaboutPlacementError,
)
from flipville.backend.definitions import GameDefinition
from flipville.backend.neighbourhood import Neighbourhood
from flipville.backend.house import House


@dataclass
class Player:
    game_definition: GameDefinition
    neighbourhood: Neighbourhood
    investments: Dict[int, int]
    num_biss: int = 0
    num_permit_refusals: int = 0
    num_pools: int = 0
    num_roundabouts: int = 0
    num_temp_agencies: int = 0
    plans_completed: List[Optional[int]] = field(default_factory=list)

    @classmethod
    def new(cls, definition: GameDefinition) -> "Player":
        investments = {
            estate_size: 0 for estate_size in definition.scoring.invest.map.keys()
        }
        return cls(
            game_definition=definition,
            neighbourhood=Neighbourhood.new(definition.neighbourhood),
            investments=investments,
            plans_completed=[None for _ in definition.plans],
        )

    def assert_place_house_is_valid(self, house: House) -> None:
        if house.is_roundabout:
            self.assert_roundabout_placement_is_valid()

    def place_house(self, street_no: int, plot_no: int, house: House) -> None:
        self.assert_place_house_is_valid(house)
        self.neighbourhood.place_house(street_no, plot_no, house)
        if house.is_bis:
            self.num_biss += 1
        if house.has_pool:
            self.num_pools += 1
        if house.is_roundabout:
            self.num_roundabouts += 1
        if house.built_by_temps:
            self.num_temp_agencies += 1

    def place_fence(self, street_no: int, fence_index: int) -> None:
        self.neighbourhood.place_fence(street_no, fence_index)

    def assert_make_investment_is_valid(self, estate_size: int) -> None:
        if estate_size not in self.investments.keys():
            raise InvestmentError(f"Cannot invest in estates of size {estate_size}.")

        if self.investments[
            estate_size
        ] >= self.game_definition.max_investments_in_estate_size(estate_size):
            raise InvestmentError(
                f"Already fully invested in estates of size {estate_size}."
            )

    def make_investment(self, estate_size: int) -> None:
        self.assert_make_investment_is_valid(estate_size)
        self.investments[estate_size] += 1

    def assert_roundabout_placement_is_valid(self):
        if self.num_roundabouts >= self.game_definition.max_roundabouts:
            raise RoundaboutPlacementError(
                "Maximum number of roundabouts have been placed."
            )

    def get_score(self, other_player_temps: Tuple[int]) -> int:
        all_player_temps = other_player_temps + (self.num_temp_agencies,)

        scoring = self.game_definition.scoring
        return sum(
            (
                scoring.bis_score(self.num_biss),
                scoring.investment_score(
                    self.neighbourhood.get_all_estates(), self.investments
                ),
                scoring.pool_score(self.num_pools),
                scoring.roundabouts_score(self.num_roundabouts),
                scoring.temp_agency_score(all_player_temps, self.num_temp_agencies),
                scoring.permit_refusal_score(self.num_permit_refusals),
                sum((street.get_park_score() for street in self.neighbourhood.streets)),
            )
        )
