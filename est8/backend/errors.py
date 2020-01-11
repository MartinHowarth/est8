class Est8Error(Exception):
    pass


class HousePlacementError(Est8Error):
    pass


class BisPlacementError(HousePlacementError):
    pass


class RoundaboutPlacementError(HousePlacementError):
    pass


class FencePlacementError(Est8Error):
    pass


class InvestmentError(Est8Error):
    pass
