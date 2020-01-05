from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple, Dict, Iterable


class ActionEnum(Enum):
    """Enum of possible card actions."""

    bis = auto()
    fence = auto()
    park = auto()
    invest = auto()
    pool = auto()
    temp_agency = auto()


@dataclass(frozen=True)
class CardDefinition:
    number: int
    action: ActionEnum


@dataclass(frozen=True)
class DeckDefinition:
    bis_numbers: Tuple[int, ...]
    fence_numbers: Tuple[int, ...]
    park_numbers: Tuple[int, ...]
    invest_numbers: Tuple[int, ...]
    pool_numbers: Tuple[int, ...]
    temp_agency_numbers: Tuple[int, ...]

    @classmethod
    def default(cls) -> "DeckDefinition":
        return cls(
            bis_numbers=(3, 4, 6, 7, 8, 9, 10, 12, 13),
            fence_numbers=(1, 2, 3, 5, 5, 6, 6, 7, 8, 8, 9, 10, 10, 11, 11, 13, 14, 15),
            park_numbers=(1, 2, 4, 5, 5, 6, 7, 7, 8, 8, 9, 9, 10, 11, 11, 12, 14, 15),
            invest_numbers=(1, 2, 4, 5, 5, 6, 7, 7, 8, 8, 9, 9, 10, 11, 11, 12, 14, 15),
            pool_numbers=(3, 4, 6, 7, 8, 9, 10, 12, 13),
            temp_agency_numbers=(3, 4, 6, 7, 8, 8, 9, 10, 12, 13),
        )


@dataclass(frozen=True)
class StreetDefinition:
    num_houses: int
    pool_locations: Tuple[int, ...]
    num_parks: int
    park_scoring: Tuple[int, ...]

    def can_have_pool_at(self, plot_no: int) -> bool:
        return plot_no in self.pool_locations

    def park_score(self, num_parks_built: int) -> int:
        return self.park_scoring[min(num_parks_built, len(self.park_scoring) - 1)]


@dataclass(frozen=True)
class NeighbourhoodDefinition:
    streets: Tuple[StreetDefinition, ...]

    @classmethod
    def default(cls) -> "NeighbourhoodDefinition":
        return cls(
            streets=(
                StreetDefinition(
                    num_houses=10,
                    pool_locations=(2, 6, 7),
                    num_parks=3,
                    park_scoring=(0, 2, 4, 10),
                ),
                StreetDefinition(
                    num_houses=11,
                    pool_locations=(0, 3, 7),
                    num_parks=4,
                    park_scoring=(0, 2, 4, 6, 14),
                ),
                StreetDefinition(
                    num_houses=12,
                    pool_locations=(1, 6, 10),
                    num_parks=5,
                    park_scoring=(0, 2, 4, 6, 8, 18),
                ),
            )
        )

    def can_have_pool_at(self, street_no: int, plot_no: int) -> bool:
        if street_no >= len(self.streets) or street_no < 0:
            return False
        return self.streets[street_no].can_have_pool_at(plot_no)


@dataclass(frozen=True)
class InvestDefinition:
    map: Dict[int, Tuple[int, ...]]

    @classmethod
    def default(cls) -> "InvestDefinition":
        return cls(
            map={
                1: (1, 3),
                2: (2, 3, 4),
                3: (3, 4, 5, 6),
                4: (4, 5, 6, 7, 8),
                5: (5, 6, 7, 8, 10),
                6: (6, 7, 8, 10, 12),
            }
        )

    def get_estate_value(self, estate_size: int, investment_level: int) -> int:
        return self.map[estate_size][
            min(investment_level, len(self.map[estate_size]) - 1)
        ]


@dataclass(frozen=True)
class ScoringDefinition:
    """
    Definition of global scoring mechanisms.

    NB: per-street scoring handled by the street definition.
    """

    bis: Tuple[int, ...]
    invest: InvestDefinition
    permit_refusal: Tuple[int, ...]
    pool: Tuple[int, ...]
    roundabout: Tuple[int, ...]
    temp_agency: Tuple[int, ...]

    @classmethod
    def default(cls) -> "ScoringDefinition":
        return ScoringDefinition(
            bis=(0, -1, -3, -6, -9, -12, -16, -20, -24, -28),
            invest=InvestDefinition.default(),
            permit_refusal=(0, 0, -3, -5),
            pool=(0, 3, 6, 9, 13, 17, 21, 26, 31, 36),
            roundabout=(0, -3, -8),
            temp_agency=(7, 4, 1),
        )

    def bis_score(self, num_biss: int) -> int:
        return self.bis[min(num_biss, len(self.bis) - 1)]

    def permit_refusal_score(self, num_permit_refusals: int) -> int:
        return self.permit_refusal[
            min(num_permit_refusals, len(self.permit_refusal) - 1)
        ]

    def pool_score(self, num_pools: int) -> int:
        return self.pool[min(num_pools, len(self.pool) - 1)]

    def roundabouts_score(self, num_roundabouts: int) -> int:
        return self.roundabout[min(num_roundabouts, len(self.roundabout) - 1)]

    def investment_score(
        self, estates: Iterable[int], investments: Dict[int, int]
    ) -> int:
        estate_values: Dict[int, int] = {}

        # Build up map of estate size worth
        for estate_size in self.invest.map.keys():
            estate_values[estate_size] = self.invest.get_estate_value(
                estate_size, investments.get(estate_size, 0)
            )

        # Now sum up estate values.
        total = 0
        for estate in estates:
            total += estate_values[estate]

        return total

    def temp_agency_score(
        self, all_players_temps: Tuple[int, ...], player_temps: int
    ) -> int:
        # Have to use at least one temp to score anything.
        if player_temps == 0:
            return 0

        # Make list of num temps for each podium position, allowing friendly ties.
        reduced_sorted_all_players_temps = sorted(set(all_players_temps), reverse=True)
        podium_position = reduced_sorted_all_players_temps.index(player_temps)
        if podium_position < len(self.temp_agency):
            return self.temp_agency[podium_position]
        return 0


@dataclass(frozen=True)
class PlanDefinition:
    points: Tuple[int, int]


@dataclass(frozen=True)
class PlanDeckDefinition:
    no_1: Tuple[PlanDefinition, ...]
    no_2: Tuple[PlanDefinition, ...]
    no_3: Tuple[PlanDefinition, ...]

    @classmethod
    def default(cls) -> "PlanDeckDefinition":
        return cls(no_1=tuple(), no_2=tuple(), no_3=tuple(),)


@dataclass(frozen=True)
class GameDefinition:
    neighbourhood: NeighbourhoodDefinition
    scoring: ScoringDefinition
    deck: DeckDefinition
    plan_deck: PlanDeckDefinition

    @classmethod
    def default(cls) -> "GameDefinition":
        return cls(
            neighbourhood=NeighbourhoodDefinition.default(),
            scoring=ScoringDefinition.default(),
            deck=DeckDefinition.default(),
            plan_deck=PlanDeckDefinition.default(),
        )

    def can_have_pool_at(self, street_no: int, plot_no: int) -> bool:
        return self.neighbourhood.can_have_pool_at(street_no, plot_no)

    @property
    def max_roundabouts(self) -> int:
        return len(self.scoring.roundabout) - 1

    def max_investments_in_estate_size(self, estate_size: int) -> int:
        return len(self.scoring.invest.map[estate_size]) - 1
