class FlipvilleError(Exception):
    pass


class HousePlacementError(FlipvilleError):
    pass


class BisPlacementError(HousePlacementError):
    pass


class RoundaboutPlacementError(HousePlacementError):
    pass


class FencePlacementError(FlipvilleError):
    pass


class InvestmentError(FlipvilleError):
    pass
