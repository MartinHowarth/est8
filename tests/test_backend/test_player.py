"""Tests for the Player class."""

import pytest

from mock import MagicMock

from flipville.backend.errors import RoundaboutPlacementError, InvestmentError
from flipville.backend.definitions import GameDefinition
from flipville.backend.house import House
from flipville.backend.player import Player


@pytest.fixture()
def player():
    """Create a dummy player to be as a fixture in these tests."""
    return Player.new(GameDefinition.default())


def test_assert_roundabout_placement_is_valid(subtests, player):
    """Test validity of placing a roundabout."""
    with subtests.test("Can place first roundabout."):
        player.assert_roundabout_placement_is_valid()

    with subtests.test("Cannot place more roundabouts than allowed."):
        player.num_roundabouts = 5
        with pytest.raises(RoundaboutPlacementError):
            player.assert_roundabout_placement_is_valid()


def test_assert_make_investment_is_valid(subtests, player):
    """Test checking validity of making an investment."""
    with subtests.test("Cannot invest in not-allowed estate size."):
        with pytest.raises(InvestmentError):
            player.assert_make_investment_is_valid(0)
        with pytest.raises(InvestmentError):
            player.assert_make_investment_is_valid(100)

    with subtests.test("Can invest in valid estate."):
        player.assert_make_investment_is_valid(1)
        player.assert_make_investment_is_valid(6)

    with subtests.test("Cannot invest in same estate size too many times."):
        # Default definition has 4 allowed investments in estate size of 6
        player.investments[6] = 4
        with pytest.raises(InvestmentError):
            player.assert_make_investment_is_valid(6)


def test_make_investment(subtests, player):
    """Test player making an ivnestment."""
    with subtests.test("Can invest in uninvested estate size."):
        player.make_investment(4)
        assert player.investments[4] == 1

    with subtests.test("Can invest a second time in same estate size."):
        player.make_investment(4)
        assert player.investments[4] == 2

    with subtests.test("Can invest in a different estate size independently."):
        player.make_investment(1)
        assert player.investments[1] == 1
        assert player.investments[4] == 2


def test_place_house(subtests, player):
    """Test player placing a house."""
    player.neighbourhood = MagicMock()

    with subtests.test("Placing Bis increases bis counter."):
        player.place_house(0, 0, House(is_bis=True))
        assert player.num_biss == 1

    with subtests.test("Placing pool increases pool counter."):
        player.place_house(0, 2, House(has_pool=True))
        assert player.num_biss == 1

    with subtests.test("Placing roundabout increases roundabout counter."):
        player.place_house(0, 1, House(is_roundabout=True))
        assert player.num_roundabouts == 1

    with subtests.test("Placing using temp agency increases temp agency counter."):
        player.place_house(0, 3, House(built_by_temps=True))
        assert player.num_temp_agencies == 1


def test_scoring(subtests, player):
    """Test calculating player score."""
    with subtests.test("Test default player definition has score of 0."):
        assert player.get_score(tuple()) == 0

    with subtests.test("Test player scores a bit of everything."):
        # Individual types of scoring are all tested elsewhere, so
        # just check that we sum up correctly here.
        player.num_permit_refusals = 2
        player.num_temp_agencies = 5
        player.num_roundabouts = 1
        player.num_pools = 4
        player.num_biss = 3
        player.investments = {1: 1, 6: 4}

        player.neighbourhood.streets[0].num_parks = 3
        player.neighbourhood.streets[1].num_parks = 2
        player.neighbourhood.streets[2].num_parks = 1

        # Make estate of size 2
        player.place_house(1, 0, House(1))
        player.place_house(1, 1, House(2))
        player.place_fence(1, 2)

        # Make estate of size 6
        for i in range(6):
            player.place_house(0, i, House(i))
        player.place_fence(0, 6)

        assert player.get_score((3,)) == sum(
            (
                -6,  # biss
                7,  # most temp agencies
                -3,  # roundabouts
                13,  # pools
                -3,  # permit refusals
                2 + 12,  # investments (1 * 2) + (1 * 12)
                10 + 4 + 2,  # parks
            )
        )
