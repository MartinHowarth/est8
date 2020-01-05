"""Definition of a row of Houses and fences."""

from dataclasses import dataclass
from typing import List, Tuple, Optional

from flipville.backend.errors import (
    HousePlacementError,
    BisPlacementError,
    FencePlacementError,
)
from flipville.backend.definitions import StreetDefinition
from flipville.backend.house import House


@dataclass
class Street:
    """Class defining the layout of houses and fences between them."""

    definition: StreetDefinition
    houses: List[Optional[House]]

    # Fences are indexed to the left of houses.
    # i.e. fences[0] is the fence to the left of houses[0]
    fences: List[bool]
    num_parks: int = 0

    def __str__(self):
        """Simplified string representation of this Street."""
        result = ""
        for index, house in enumerate(self.houses):
            fence = "|" if self.fences[index] else "."
            result += f"{fence}{house if house is not None else ' '}"
        result += "|" if self.fences[-1] else "."
        return result

    @classmethod
    def new(cls, definition: StreetDefinition) -> "Street":
        """Construct a new Street using the given definition."""
        fences = [False for _ in range(definition.num_houses)]

        # Get fences for free on both ends of the street.
        fences.insert(0, True)
        fences[-1] = True
        return cls(
            definition=definition,
            houses=[None for _ in range(definition.num_houses)],
            fences=fences,
        )

    def get_neighbours(self, plot_no: int) -> Tuple[Optional[House], Optional[House]]:
        """Get the neighbouring houses to the given plot, if they exist."""
        if plot_no < 0 or plot_no >= len(self.houses):
            # Off either end of street -  no neighbours
            return None, None

        to_left = self.houses[plot_no - 1] if plot_no > 0 else None
        to_right = (
            self.houses[plot_no + 1] if plot_no < (len(self.houses) - 1) else None
        )
        return to_left, to_right

    def assert_place_fence_is_valid(self, fence_index: int) -> None:
        """Raise a FencePlacementError if the given fence_index is not a valid fence placement."""
        if fence_index < 0 or fence_index >= len(self.fences):
            raise FencePlacementError("Cannot place fence off end fo street.")
        if self.fences[fence_index] is True:
            raise FencePlacementError("A fence already exists in this location.")

    def place_fence(self, fence_index: int) -> None:
        """
        Place a fence at the given index.

        Checks for validity before placing.
        """
        self.assert_place_fence_is_valid(fence_index)
        self.fences[fence_index] = True

    def get_possible_bis_numbers(
        self, plot_no: int
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Get the possible numbers for a bis construction in a given plot.

        The possibilities are the numbers of adjacent houses, excluding those that are
        separated from the bis by a fence.
        """
        to_left, to_right = self.get_neighbours(plot_no)
        left_no, right_no = None, None
        if to_left is not None:
            # Check if there is a fence to the left of the plot_no
            # i.e. between the potential bis placement and the house on the left
            if not self.fence_to_left_of_plot(plot_no):
                left_no = to_left.number
        if to_right is not None:
            # Check if there is a fence to the right of the plot_no
            # i.e. between the potential bis placement and the house on the right
            if not self.fence_to_right_of_plot(plot_no):
                right_no = to_right.number
        return left_no, right_no

    def assert_bis_placement_is_valid(self, plot_no: int) -> None:
        """Raise a BisPlacementError a bis cannot be placed at the given plot_no."""
        left_no, right_no = self.get_possible_bis_numbers(plot_no)
        if left_no is None and right_no is None:
            raise BisPlacementError(
                "A Bis must be placed next to a house with no fence between them."
            )

    def assert_place_house_is_valid(self, plot_no: int, house: House) -> None:
        """
        Raise a HousePlacementError if the given house cannot be placed at the given plot_no.

        This checks that:
         - the plot is empty
         - is a valid bis placement (if the house is a bis)
         - obeys increasing house number rules (resetting at roundabouts)
        """
        if plot_no < 0 or plot_no >= len(self.houses):
            raise HousePlacementError("Can't place house off end of street.")

        if self.houses[plot_no] is not None:
            raise HousePlacementError("Plot is not empty.")

        if house.is_roundabout:
            # Roundabout needs no further checks.
            pass

        elif house.is_bis:
            self.assert_bis_placement_is_valid(plot_no)

        else:
            # Check that the proposed house fits into a strictly increasing
            # numbering from left to right.
            # Also account for house numbering resetting at roundabouts.
            highest_to_left = -1
            for existing_house in self.houses[:plot_no]:
                if existing_house is None:
                    continue
                if existing_house.is_roundabout:
                    highest_to_left = 0
                elif (
                    existing_house.number is not None
                    and existing_house.number > highest_to_left
                ):
                    highest_to_left = existing_house.number

            lowest_to_right = 99999
            for existing_house in self.houses[:plot_no:-1]:
                if existing_house is None:
                    continue
                if existing_house.is_roundabout:
                    lowest_to_right = 99999
                elif (
                    existing_house.number is not None
                    and existing_house.number < lowest_to_right
                ):
                    lowest_to_right = existing_house.number

            if house.number <= highest_to_left or house.number >= lowest_to_right:
                raise HousePlacementError(
                    f"House number invalid. "
                    f"{highest_to_left} < {house.number} < {lowest_to_right} not satisfied."
                )

    def place_house(self, plot_no: int, house: House) -> None:
        """
        Place the given house in the given plot_no.

        Checks for validity before placing.

        Also performs:
         - Automatically determining bis number on placement.
         - Building fences on both sides of a roundabout.
         - Increasing the park counter if a house comes with a park.
        """
        self.assert_place_house_is_valid(plot_no, house)

        if house.is_bis:
            # Auto set the number of the house if it is a bis.
            # We are guaranteed to get a non-None for one of left or right
            # because we've already asserted that placement is valid.
            left_no, right_no = self.get_possible_bis_numbers(plot_no)
            house.number = left_no if left_no is not None else right_no

        if house.is_roundabout:
            if not self.fence_to_left_of_plot(plot_no):
                self.place_fence(plot_no)
            if not self.fence_to_right_of_plot(plot_no):
                self.place_fence(plot_no + 1)

        self.houses[plot_no] = house
        if house.has_park and self.num_parks < len(self.definition.park_scoring) - 1:
            self.num_parks += 1

    def fence_to_left_of_plot(self, plot_no: int) -> bool:
        """Return True if there is a fence to the left of the given plot_no, otherwise False."""
        return self.fences[plot_no]

    def fence_to_right_of_plot(self, plot_no: int) -> bool:
        """Return True if there is a fence to the right of the given plot_no, otherwise False."""
        return self.fences[plot_no + 1]

    def get_complete_estates(self) -> List[int]:
        """
        Get the estate sizes in this street.

        A complete estate is bounded by fences on either side and every house in between
        has been built.
        """
        estates: List[int] = []

        fence_indices = [
            fence_index
            for fence_index, fence_is_built in enumerate(self.fences)
            if fence_is_built
        ]
        for start, end in zip(fence_indices, fence_indices[1:]):
            if all(
                (
                    house is not None and not house.is_roundabout
                    for house in self.houses[start:end]
                )
            ):
                estates.append(end - start)
        return estates

    def get_park_score(self) -> int:
        return self.definition.park_score(self.num_parks)
