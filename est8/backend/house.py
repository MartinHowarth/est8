"""Definition of a House that can be built in plots on a Street."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class House:
    """
    Definition of an object that fits into a street.

    This is usually a House but also represented roundabouts.
    """

    number: Optional[int] = None
    is_bis: bool = False
    has_pool: bool = False
    has_park: bool = False
    is_roundabout: bool = False
    built_by_temps: bool = False

    def __str__(self):
        """Get the short string representation of this House."""
        if self.is_roundabout:
            return "R"
        if self.is_bis:
            return f"{self.number}B"
        if self.has_pool:
            return f"{self.number}P"
        if self.number is not None:
            return f"{self.number}"
        else:
            return " "
