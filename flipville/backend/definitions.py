from dataclasses import dataclass
from enum import Enum, auto
from random import choice, shuffle
from typing import Tuple, Dict, Iterable, Optional, Generator


class ActionEnum(Enum):
    """Enum of possible card actions."""

    bis = auto()
    fence = auto()
    park = auto()
    invest = auto()
    pool = auto()
    temp = auto()


@dataclass(frozen=True)
class CardDefinition:
    number: int
    action: ActionEnum


@dataclass
class CardPair:
    number_card: CardDefinition = None
    action_card: CardDefinition = None


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

    @property
    def deck_size(self) -> int:
        return sum(
            (
                len(self.bis_numbers),
                len(self.fence_numbers),
                len(self.park_numbers),
                len(self.invest_numbers),
                len(self.pool_numbers),
                len(self.temp_agency_numbers),
            )
        )

    def ordered_card_generator(self) -> Generator[CardDefinition, None, None]:
        for number in self.bis_numbers:
            yield CardDefinition(number=number, action=ActionEnum.bis)
        for number in self.fence_numbers:
            yield CardDefinition(number=number, action=ActionEnum.fence)
        for number in self.park_numbers:
            yield CardDefinition(number=number, action=ActionEnum.park)
        for number in self.pool_numbers:
            yield CardDefinition(number=number, action=ActionEnum.pool)
        for number in self.invest_numbers:
            yield CardDefinition(number=number, action=ActionEnum.invest)
        for number in self.temp_agency_numbers:
            yield CardDefinition(number=number, action=ActionEnum.temp)

    def random_card_generator(
        self, no_reshuffle_last_n: int = 0
    ) -> Generator[CardDefinition, None, None]:
        """
        A generator that returns each defined card in a random order.

        When trying to draw more cards than there are in the deck, all of the cards are
        shuffled again and then more are picked.
        
        :param no_reshuffle_last_n: Number of cards that were last drawn to not re-shuffle into 
            the deck. This simulates behaviour of leaving cards on the table while reshuffling
            the rest.
        """
        all_cards = list(self.ordered_card_generator())
        last_n_cards = []

        while True:
            # Deal out the current deck in a random order.
            shuffle(all_cards)
            for card in all_cards:
                yield card

            # Add back in the previous set of last cards to the front.
            all_cards = last_n_cards + all_cards

            # Record the last cards dealt from the end
            last_n_cards = all_cards[-no_reshuffle_last_n:]

            # Remove those cards from the current deck
            all_cards = all_cards[: len(all_cards) - no_reshuffle_last_n]


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
        return cls(
            no_1=(PlanDefinition((6, 2)),),
            no_2=(PlanDefinition((8, 3)),),
            no_3=(PlanDefinition((11, 5)),),
        )

    def pick_3(self) -> Tuple[PlanDefinition, PlanDefinition, PlanDefinition]:
        return choice(self.no_1), choice(self.no_2), choice(self.no_3)


@dataclass(frozen=True)
class GameDefinition:
    neighbourhood: NeighbourhoodDefinition
    scoring: ScoringDefinition
    deck: DeckDefinition
    plans: Tuple[PlanDefinition, PlanDefinition, PlanDefinition]
    num_cards_drawn_at_once: int = 3

    @classmethod
    def default(cls) -> "GameDefinition":
        return cls(
            neighbourhood=NeighbourhoodDefinition.default(),
            scoring=ScoringDefinition.default(),
            deck=DeckDefinition.default(),
            plans=PlanDeckDefinition.default().pick_3(),
        )

    def can_have_pool_at(self, street_no: int, plot_no: int) -> bool:
        return self.neighbourhood.can_have_pool_at(street_no, plot_no)

    @property
    def max_roundabouts(self) -> int:
        return len(self.scoring.roundabout) - 1

    def max_investments_in_estate_size(self, estate_size: int) -> int:
        return len(self.scoring.invest.map[estate_size]) - 1

    def generate_card_pairs(self) -> Generator[Tuple[CardPair, ...], None, None]:
        """
        Generate tuples of CardPairs representing the deck being drawn from.

        The number card of the pair is used as the action card in the next pair.
        """
        random_card_gen = self.deck.random_card_generator()

        def next_n_cards() -> Tuple[CardDefinition]:
            return tuple(
                (next(random_card_gen) for _ in range(self.num_cards_drawn_at_once))
            )

        action_cards = next_n_cards()

        while True:
            number_cards = next_n_cards()
            yield tuple(
                (
                    CardPair(number_card=number_cards[i], action_card=action_cards[i])
                    for i in range(self.num_cards_drawn_at_once)
                )
            )
            action_cards = number_cards
