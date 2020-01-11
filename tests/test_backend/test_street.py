"""Tests for the Street class."""

import pytest

from est8.backend.errors import (
    FencePlacementError,
    HousePlacementError,
    BisPlacementError,
)
from est8.backend.definitions import NeighbourhoodDefinition
from est8.backend.house import House
from est8.backend.street import Street


@pytest.fixture()
def street() -> Street:
    """Construct a Street using the default definition for use as a fixture."""
    return Street.new(NeighbourhoodDefinition.default().streets[0])


def get_street_with_houses(start_house: int, end_house: int) -> Street:
    """Construct a Street filled with houses between the indices given."""
    street = Street.new(NeighbourhoodDefinition.default().streets[0])
    # Fill in house numbers so we can check which ones we got out
    for num in range(start_house, end_house):
        street.place_house(num, House(number=num))

    return street


def test_new(subtests):
    """Test creating a new Street from a definition works correctly."""
    street_defn = NeighbourhoodDefinition.default().streets[0]
    street = Street.new(street_defn)

    with subtests.test("Check houses initialised correctly."):
        assert len(street.houses) == street_defn.num_houses

    with subtests.test("Check fences initialised correctly."):
        assert len(street.fences) == street_defn.num_houses + 1

        with subtests.test("Check fences at each end of street exist."):
            assert street.fences[0] is True
            assert street.fences[-1] is True

        with subtests.test("Check non-end fences do not exist."):
            assert any(street.fences[1:-1]) is False


def test_get_neighbours(subtests, street):
    """Test that getting the neighbouring houses of a given plot works."""
    # Fill in house numbers so we can check which ones we got out
    street = get_street_with_houses(0, len(street.houses))

    with subtests.test("Can get two neighbours in middle of street."):
        to_left, to_right = street.get_neighbours(5)
        assert to_left.number == 4
        assert to_right.number == 6

    with subtests.test("Can get one neighbour at start of street."):
        to_left, to_right = street.get_neighbours(0)
        assert to_left is None
        assert to_right.number == 1

    with subtests.test("Can get one neighbour at end of street."):
        last_plot_num = len(street.houses) - 1
        to_left, to_right = street.get_neighbours(last_plot_num)
        assert to_left.number == last_plot_num - 1
        assert to_right is None

    with subtests.test("Get no neighbours for plot not in street."):
        to_left, to_right = street.get_neighbours(-100)
        assert to_left is None
        assert to_right is None

        to_left, to_right = street.get_neighbours(100)
        assert to_left is None
        assert to_right is None


def test_assert_place_fence_is_valid(subtests, street):
    """Test that fence placement validity checks work correctly."""
    with subtests.test("Can place fence where no fence exists."):
        street.assert_place_fence_is_valid(1)

    with subtests.test("Cannot place fence where fence exists already."):
        with pytest.raises(FencePlacementError):
            street.assert_place_fence_is_valid(0)

    with subtests.test("Cannot place fence off end of street."):
        with pytest.raises(FencePlacementError):
            street.assert_place_fence_is_valid(-1)
        with pytest.raises(FencePlacementError):
            street.assert_place_fence_is_valid(100)


def test_place_fence(street):
    """Test that placing a fence works correctly."""
    # Check fence does not exist first
    assert street.fences[5] is False
    street.place_fence(5)
    assert street.fences[5] is True


def test_get_possible_bis_numbers(subtests, street):
    """Test that getting valid house number for adjacenct bis's works correctly."""
    with subtests.test("No bis numbers when have no neighbours."):
        left, right = street.get_possible_bis_numbers(5)
        assert left is None
        assert right is None

    street.houses[4] = House(number=4)

    with subtests.test("One bis numbers when have one neighbour."):
        with subtests.test("Neighbour on left."):
            left, right = street.get_possible_bis_numbers(5)
            assert left == 4
            assert right is None

        with subtests.test("Neighbour on right."):
            left, right = street.get_possible_bis_numbers(3)
            assert left is None
            assert right == 4

    street.houses[6] = House(number=6)

    with subtests.test("Two bis numbers when have two neighbour."):
        left, right = street.get_possible_bis_numbers(5)
        assert left == 4
        assert right == 6

    street.place_fence(5)

    with subtests.test("One bis number when two neighbours but one cut off by fence."):
        left, right = street.get_possible_bis_numbers(5)
        assert left is None
        assert right == 6

    street.place_fence(6)

    with subtests.test(
        "No bis numbers when two neighbours but both cut off by fences."
    ):
        left, right = street.get_possible_bis_numbers(5)
        assert left is None
        assert right is None


def test_assert_place_house_is_valid(subtests, street):
    """Test that checking validity of house placement works correctly."""
    with subtests.test("Cannot place house off end of street."):
        with subtests.test("Off left end of street."):
            with pytest.raises(HousePlacementError):
                street.assert_place_house_is_valid(-1, House())
        with subtests.test("Off rightend of street."):
            with pytest.raises(HousePlacementError):
                street.assert_place_house_is_valid(100, House())

    street.houses[2] = House(number=2)

    # Street is now: | | |2| | | | | | | |
    with subtests.test("Cannot place house on top of another house."):
        with pytest.raises(HousePlacementError):
            street.assert_place_house_is_valid(2, House())

    with subtests.test("Cannot place bis not next to another house."):
        # Testing layout: | | |2| | | |bis| | | |
        with pytest.raises(BisPlacementError):
            street.assert_place_house_is_valid(6, House(is_bis=True))

    with subtests.test(
        "Cannot place house with higher number to left of lower number house."
    ):
        # Testing layout: | |12|2| | | | | | | |
        with pytest.raises(HousePlacementError):
            street.assert_place_house_is_valid(1, House(12))

    with subtests.test(
        "Cannot place house with lower number to right of higher number house."
    ):
        # Testing layout: | | |2| | | |2| | | |
        with pytest.raises(HousePlacementError):
            street.assert_place_house_is_valid(6, House(2))

    street.houses[5] = House(is_roundabout=True)
    street.houses[8] = House(8)

    # Street is now: | | |2| | |R| | |8| |
    with subtests.test("Test that roundabout resets house numbering."):
        # Test positives - make sure roundabout resetting allows out-of-order numbers
        with subtests.test(
            "Can place house with lower number to right of higher number house."
        ):
            # Testing layout : | | |2| | |R|2| |8| |
            street.assert_place_house_is_valid(6, House(2))
        with subtests.test(
            "Can place house with higher number to left of lower number house."
        ):
            # Testing layout : | | |2| |12|R| | |8| |
            street.assert_place_house_is_valid(4, House(12))

        # Test negatives - make sure roundabout resetting still prevents ordering
        # within a sub-street
        with subtests.test(
            "Cannot place house with higher number to left of lower number house."
        ):
            # Testing layout : | | |2| | |R|12| |8| |
            with pytest.raises(HousePlacementError):
                street.assert_place_house_is_valid(6, House(12))

            # Testing layout : | |12|2| | |R| | |8| |
            with pytest.raises(HousePlacementError):
                street.assert_place_house_is_valid(1, House(12))
        with subtests.test(
            "Cannot place house with lower number to right of higher number house."
        ):
            # Testing layout : | | |2| |1|R| | |8| |
            with pytest.raises(HousePlacementError):
                street.assert_place_house_is_valid(4, House(1))

            # Testing layout : | | |2| | |R| | |8|1|
            with pytest.raises(HousePlacementError):
                street.assert_place_house_is_valid(9, House(1))


def test_place_house(subtests, street):
    """Test that placing a house in a street works correctly."""
    street.place_house(4, House(4))
    street.place_house(8, House(8))

    with subtests.test("Place bis autodetects number"):
        with subtests.test("Main house on left."):
            street.place_house(5, House(is_bis=True))
            assert street.houses[5].number == 4

        with subtests.test("Main house on right."):
            street.place_house(7, House(is_bis=True))
            assert street.houses[7].number == 8

    with subtests.test("Place roundabout adds surrounding fences"):
        street.place_house(6, House(is_roundabout=True))
        assert street.fences[6] is True
        assert street.fences[7] is True

    with subtests.test("Parks are counted."):
        street.place_house(1, House(1, has_park=True))
        assert street.num_parks == 1


def test_street_to_str(subtests, street):
    """Test that the string representation of streets works correctly."""
    with subtests.test("Empty street."):
        assert str(street) == "| . . . . . . . . . |"

    street.place_house(4, House(12))

    with subtests.test("One house."):
        assert str(street) == "| . . . .12. . . . . |"

    street.place_fence(4)

    with subtests.test("One house and fence."):
        assert str(street) == "| . . . |12. . . . . |"

    street.place_fence(5)

    with subtests.test("One house and two fences."):
        assert str(street) == "| . . . |12| . . . . |"

    street.place_house(6, House(13, has_pool=True))

    with subtests.test("House with pool."):
        assert str(street) == "| . . . |12| .13P. . . |"

    street.place_house(5, House(None, is_bis=True))

    with subtests.test("Bis."):
        assert str(street) == "| . . . |12|13B.13P. . . |"

    street.place_house(3, House(None, is_roundabout=True))

    with subtests.test("Roundabout."):
        assert str(street) == "| . . |R|12|13B.13P. . . |"


def test_get_complete_estates(subtests, street):
    """Test that determining completed estate sizes works correctly."""
    with subtests.test("Get 0 estates when no houses built."):
        assert street.get_complete_estates() == []

    with subtests.test("Get 1 large estate when all houses built."):
        test_street = get_street_with_houses(0, len(street.houses))
        assert test_street.get_complete_estates() == [len(test_street.houses)]

    with subtests.test("Get 0 estates when all but one house is built with no fences."):
        with subtests.test("Missing first house."):
            test_street = get_street_with_houses(1, len(street.houses))
            assert test_street.get_complete_estates() == []

        with subtests.test("Missing middle house."):
            test_street = get_street_with_houses(0, len(street.houses))
            test_street.houses[5] = None
            assert test_street.get_complete_estates() == []

        with subtests.test("Missing last house."):
            test_street = get_street_with_houses(0, len(street.houses) - 1)
            assert test_street.get_complete_estates() == []

    with subtests.test("Can get estate of size 1 with other estate incomplete."):
        test_street = get_street_with_houses(0, len(street.houses))
        test_street.houses[5] = None
        test_street.fences[1] = True
        assert test_street.get_complete_estates() == [1]

    with subtests.test("Can get two estates split by single fence"):
        with subtests.test("Split with minimal estate size."):
            test_street = get_street_with_houses(0, len(street.houses))
            test_street.fences[1] = True
            assert test_street.get_complete_estates() == [1, 9]

        with subtests.test("Split with equal estate sizes."):
            test_street = get_street_with_houses(0, len(street.houses))
            test_street.fences[5] = True
            assert test_street.get_complete_estates() == [5, 5]

    with subtests.test("Roundabouts are not registered as estates."):
        test_street = get_street_with_houses(0, len(street.houses))
        test_street.houses[5] = None
        test_street.place_house(5, House(is_roundabout=True))
        assert test_street.get_complete_estates() == [5, 4]
