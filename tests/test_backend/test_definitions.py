from est8.backend.definitions import (
    NeighbourhoodDefinition,
    DeckDefinition,
    CardDefinition,
    ScoringDefinition,
    StreetDefinition,
    GameDefinition,
    InvestDefinition,
)


def test_street_definition(subtests):
    defn = StreetDefinition(num_houses=2, pool_locations=(0,), park_scoring=(0, 2))

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


def test_game_definition(subtests):
    defn = GameDefinition.default()

    with subtests.test("Test checking pool location."):
        assert defn.can_have_pool_at(0, 2) is True

    card_pair_gen = defn.generate_card_pairs()

    with subtests.test("Test drawing CardPairs from the deck."):
        first_card_pairs = next(card_pair_gen)
        assert len(first_card_pairs) == defn.num_cards_drawn_at_once
        assert all(
            [
                card_pair.number_card is not card_pair.action_card
                for card_pair in first_card_pairs
            ]
        )

    with subtests.test(
        "Test second set of CardPairs re-use the number cards as action cards."
    ):
        second_card_pairs = next(card_pair_gen)
        assert len(second_card_pairs) == defn.num_cards_drawn_at_once
        assert all(
            [
                first_pair.number_card is second_pair.action_card
                for first_pair, second_pair in zip(first_card_pairs, second_card_pairs)
            ]
        )


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


def test_deck_definition(subtests):
    defn = DeckDefinition.default()
    rand_generator = defn.random_card_generator()

    draw_cards = []
    for index in range(defn.deck_size):
        draw_cards.append(next(rand_generator))

    with subtests.test("Check that no card was drawn twice."):
        # Compare IDs of card because some cards are actually identical otherwise.
        assert len(set((id(card) for card in draw_cards))) == len(draw_cards)

    with subtests.test(
        "Check that deck gets reshuffled without re-creating the rand generator."
    ):
        next_card = next(rand_generator)
        # Next drawn card must be in the previously drawn set because we have reshuffled it.
        assert next_card in draw_cards

    with subtests.test("Test that we can not re-shuffle the last N cards."):
        no_reshuffle_last_n = 3
        rand_generator = defn.random_card_generator(no_reshuffle_last_n)

        # Draw the entire deck once.
        first_drawn_cards = []
        for index in range(defn.deck_size):
            first_drawn_cards.append(next(rand_generator))

        last_n_cards = first_drawn_cards[defn.deck_size - no_reshuffle_last_n :]

        # Draw the reshuffled deck once - that means drawing all but the few left unshuffled.
        second_drawn_cards = []
        for index in range(defn.deck_size - no_reshuffle_last_n):
            second_drawn_cards.append(next(rand_generator))

        # Check the last N cards are not in that shuffled deck.
        for card in last_n_cards:
            assert id(card) not in [id(_card) for _card in second_drawn_cards]

        # Repeat the above a second time - the cards that were left out the first time
        # should now be shuffled in.
        third_drawn_cards = []
        for index in range(defn.deck_size - no_reshuffle_last_n):
            third_drawn_cards.append(next(rand_generator))

        for card in last_n_cards:
            assert id(card) in [id(_card) for _card in third_drawn_cards]
