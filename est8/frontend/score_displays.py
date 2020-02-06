from dataclasses import replace
from typing import Tuple, Optional, Union

from shimmer.display.components.box import Box, BoxDefinition
from shimmer.display.components.box_layout import (
    BoxRow,
    BoxColumn,
    BoxLayoutDefinition,
    create_box_layout,
)
from shimmer.display.data_structures import Color
from shimmer.display.widgets.text_box import add_centralised_text
from ..backend.definitions import InvestDefinition, ScoringDefinition


def create_score_layout(
    score_levels: Tuple[int, ...],
    score_box_definition: BoxDefinition,
    layout_defn: BoxLayoutDefinition,
) -> Union[BoxRow, BoxColumn]:
    boxes = []
    for score in score_levels:
        box = Box(score_box_definition)
        add_centralised_text(box, str(score))
        boxes.append(box)

    layout = create_box_layout(definition=layout_defn, boxes=boxes)

    return layout


def create_score_obtained_layout(
    num_obtained: int,
    score_box_obtained_definition: BoxDefinition,
    layout_defn: BoxLayoutDefinition,
) -> Union[BoxRow, BoxColumn]:
    boxes = []
    for score in range(num_obtained):
        box = Box(score_box_obtained_definition)
        boxes.append(box)
    layout = create_box_layout(definition=layout_defn, boxes=boxes)

    return layout


class ShadeInNumberDisplay(Box):
    ScoreBoxDefinition = BoxDefinition(
        width=30, height=30, background_color=Color(100, 100, 100)
    )
    ScoreBoxObtainedDefinition = BoxDefinition(
        width=20, height=20, background_color=Color(0, 0, 0, 170)
    )
    LayoutDefinition = BoxLayoutDefinition(
        boxes_per_row=None, boxes_per_column=1, spacing=10
    )

    def __init__(self, score_levels: Tuple[int, ...]):
        super(ShadeInNumberDisplay, self).__init__()
        self.score_levels = score_levels
        self.score_layout = create_score_layout(
            self.score_levels, self.ScoreBoxDefinition, self.LayoutDefinition
        )
        self.obtained_layout: Optional[BoxRow] = None
        self.add(self.score_layout)

    def set_score_obtained(self, num_obtained: int) -> None:
        if self.obtained_layout is not None:
            self.remove(self.obtained_layout)

        width_diff = (
            self.ScoreBoxDefinition.width - self.ScoreBoxObtainedDefinition.width
        )
        height_diff = (
            self.ScoreBoxDefinition.height - self.ScoreBoxObtainedDefinition.height
        )
        obtained_spacing = self.LayoutDefinition.spacing + width_diff

        obtained_layout_definition = replace(
            self.LayoutDefinition, spacing=obtained_spacing
        )
        self.obtained_layout = create_score_obtained_layout(
            num_obtained, self.ScoreBoxObtainedDefinition, obtained_layout_definition
        )
        self.obtained_layout.position = width_diff / 2, height_diff / 2
        self.add(self.obtained_layout)


class ParkDisplay(ShadeInNumberDisplay):
    ScoreBoxDefinition = BoxDefinition(
        width=40, height=40, background_color=Color(0, 200, 0)
    )
    ScoreBoxObtainedDefinition = BoxDefinition(
        width=30, height=30, background_color=Color(0, 0, 0, 170)
    )


class RoundaboutDisplay(ShadeInNumberDisplay):
    ScoreBoxDefinition = BoxDefinition(
        width=30, height=30, background_color=Color(200, 0, 0)
    )


class PermitRefusalDisplay(ShadeInNumberDisplay):
    ScoreBoxDefinition = BoxDefinition(
        width=30, height=30, background_color=Color(200, 0, 0)
    )


class BisDisplay(ShadeInNumberDisplay):
    ScoreBoxDefinition = BoxDefinition(
        width=30, height=30, background_color=Color(255, 192, 200)
    )
    LayoutDefinition = BoxLayoutDefinition(
        boxes_per_row=None, boxes_per_column=2, spacing=20
    )


class PoolDisplay(ShadeInNumberDisplay):
    ScoreBoxDefinition = BoxDefinition(
        width=30, height=30, background_color=Color(0, 100, 200)
    )
    LayoutDefinition = BoxLayoutDefinition(
        boxes_per_row=None, boxes_per_column=2, spacing=20
    )


class TempAgencyDisplay(ShadeInNumberDisplay):
    ScoreBoxDefinition = BoxDefinition(
        width=30, height=30, background_color=Color(255, 165, 0)
    )


class InvestmentDisplay(ShadeInNumberDisplay):
    """Display of a single type of investment."""

    ScoreBoxDefinition = BoxDefinition(
        width=30, height=30, background_color=Color(128, 0, 128)
    )


def create_all_investments_display(
    investment_definition: InvestDefinition,
) -> BoxColumn:
    """Create a grid showing investments made."""
    definition = BoxLayoutDefinition(boxes_per_row=2, boxes_per_column=None, spacing=10)
    columns = [
        InvestmentDisplay(values) for values in investment_definition.map.values()
    ]

    column_labels = []
    for label in investment_definition.map.keys():
        box = Box(
            BoxDefinition(
                width=InvestmentDisplay.ScoreBoxDefinition.width,
                height=InvestmentDisplay.ScoreBoxDefinition.height,
                background_color=Color(100, 100, 255),
            )
        )
        add_centralised_text(box, str(label))
        column_labels.append(box)

    # Interleave the labels and columns so they get laid out with labels at the bottom.
    all_boxes = [item for sublist in zip(column_labels, columns) for item in sublist]
    return create_box_layout(definition, all_boxes)


class ScoreBoardDisplay(Box):
    """Collection of all of the score boxes except for the parks, which are per-street."""

    def __init__(self, scoring_definition: ScoringDefinition):
        super(ScoreBoardDisplay, self).__init__()
        self.investment_display = create_all_investments_display(
            scoring_definition.invest
        )
        self.pool_display = PoolDisplay(scoring_definition.pool)
        self.bis_display = BisDisplay(scoring_definition.bis)
        self.roundabout_display = RoundaboutDisplay(scoring_definition.roundabout)
        self.permit_refusal_display = PermitRefusalDisplay(
            scoring_definition.permit_refusal
        )
        self.temp_agency_display = TempAgencyDisplay(scoring_definition.temp_agency)

        layout = create_box_layout(
            BoxLayoutDefinition(boxes_per_row=1, boxes_per_column=None, spacing=30),
            [
                self.pool_display,
                self.temp_agency_display,
                self.investment_display,
                self.bis_display,
                self.roundabout_display,
                self.permit_refusal_display,
            ],
        )
        self.add(layout)
