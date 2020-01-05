from flipville.backend.definitions import (
    NeighbourhoodDefinition,
    ScoringDefinition,
    StreetDefinition,
    GameDefinition,
    InvestDefinition,
)


def test_street_definition(subtests):
    defn = StreetDefinition(
        num_houses=2, pool_locations=(0,), num_parks=1, park_scoring=(0, 2)
    )

    with subtests.test("Test checking pool locations."):
        assert defn.can_have_pool_at(0) is True
        assert defn.can_have_pool_at(1) is False

    with subtests.test("Test getting score for built parks."):
        assert defn.park_score(0) == 0
        assert defn.park_score(1) == 2


def test_neighbourhood_definition(subtests):
    defn = NeighbourhoodDefinition.default()

    with subtests.test("Can have pool at valid plot, and pool allowed."):
        assert defn.can_have_pool_at(0, 2) is True

    with subtests.test("Can't have pool at valid plot, but no pool allowed."):
        assert defn.can_have_pool_at(1, 2) is False

    with subtests.test("Can't have pool on invalid streets."):
        assert defn.can_have_pool_at(-1, 2) is False
        assert defn.can_have_pool_at(5, 2) is False


def test_game_definition():
    defn = GameDefinition.default()
    assert defn.can_have_pool_at(0, 2) is True


def test_investment_definition(subtests):
    defn = InvestDefinition.default()

    with subtests.test("Test valid investment amount."):
        assert defn.get_estate_value(1, 0) == 1

    with subtests.test("Test maxed out investment amount."):
        assert defn.get_estate_value(5, 100) == 10


def test_scoring_definition(subtests):
    defn = ScoringDefinition.default()

    with subtests.test("Test bis scoring."):
        with subtests.test("Bis scoring in range."):
            assert defn.bis_score(5) == -12

        with subtests.test("Bis scoring maxed out."):
            assert defn.bis_score(100) == defn.bis[-1]

    with subtests.test("Test permit refusal scoring."):
        with subtests.test("Permit refusal scoring in range."):
            assert defn.permit_refusal_score(2) == -3

        with subtests.test("Permit refusal scoring maxed out."):
            assert defn.permit_refusal_score(100) == defn.permit_refusal[-1]

    with subtests.test("Test pool scoring."):
        with subtests.test("Pool scoring in range."):
            assert defn.pool_score(5) == 17

        with subtests.test("Pool scoring maxed out."):
            assert defn.pool_score(100) == defn.pool[-1]

    with subtests.test("Test roundabout scoring."):
        with subtests.test("Roundabout scoring in range."):
            assert defn.roundabouts_score(1) == -3

        with subtests.test("Roundabout scoring maxed out."):
            assert defn.roundabouts_score(100) == defn.roundabout[-1]

    with subtests.test("Test investment scoring."):
        with subtests.test("Test 0 score with 0 estates."):
            assert defn.investment_score([], {}) == 0

        with subtests.test("Test estates with no investment default to minimal value"):
            # Default estate of size [1, 2] is worth [1, 2] respectively
            assert defn.investment_score([1, 2], {}) == 3

        with subtests.test("Test multiple estates with some investment in each."):
            assert defn.investment_score([1, 1, 3, 6], {1: 1, 3: 3, 6: 4}) == 24

    with subtests.test("Test temp agency scoring."):
        with subtests.test("0 score if player used 0 temps."):
            assert defn.temp_agency_score(tuple(), 0) == 0

        with subtests.test("0 score if player has 4th place or worse."):
            assert defn.temp_agency_score((5, 4, 3, 1), 1) == 0

        with subtests.test("Get score if player in top 3, even if tied."):
            assert defn.temp_agency_score((5, 4, 4, 1), 4) == defn.temp_agency[1]
