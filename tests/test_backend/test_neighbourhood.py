import pytest

from est8.backend.errors import HousePlacementError
from est8.backend.definitions import NeighbourhoodDefinition
from est8.backend.neighbourhood import Neighbourhood
from est8.backend.house import House


@pytest.fixture()
def neighbourhood():
    return Neighbourhood.new(NeighbourhoodDefinition.default())


def test_assert_place_house_is_valid(subtests, neighbourhood):
    with subtests.test("Cannot place house on non existent street."):
        with pytest.raises(HousePlacementError):
            neighbourhood.assert_place_house_is_valid(-1)

        with pytest.raises(HousePlacementError):
            neighbourhood.assert_place_house_is_valid(100)


def test_get_all_estates(subtests, neighbourhood):
    neighbourhood.place_house(0, 0, House(1))
    neighbourhood.streets[0].place_fence(1)

    neighbourhood.place_house(1, 0, House(1))
    neighbourhood.streets[1].place_fence(1)

    assert neighbourhood.get_all_estates() == [1, 1]
