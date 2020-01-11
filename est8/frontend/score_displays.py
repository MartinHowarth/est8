from dataclasses import replace
from typing import Tuple, Optional, Union

from shimmer.display.alignment import (
    VerticalAlignment,
    HorizontalAlignment,
)
from shimmer.display.data_structures import (
    LabelDefinition,
    Color,
)
from shimmer.display.components.box import Box, BoxDefinition
from shimmer.display.widgets.text_box import TextBox, TextBoxDefinition
from shimmer.display.components.box_layout import (
    BoxRow,
    BoxColumn,
    BoxLayoutDefinition,
    create_box_layout,
)


def create_score_layout(
    score_levels: Tuple[int, ...],
    score_box_definition: BoxDefinition,
    layout_defn: BoxLayoutDefinition,
) -> Union[BoxRow, BoxColumn]:
    boxes = []
    for score in score_levels:
        box = Box(score_box_definition)
        text_box = TextBox(
            TextBoxDefinition(
                label=LabelDefinition(text=str(score)), background_color=None
            ),
        )
        text_box.set_position_in_alignment_with(
            box, HorizontalAlignment.center, VerticalAlignment.center
        )
        box.add(text_box)
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
        width=40, height=40, background_color=Color(100, 100, 100)
    )
    ScoreBoxObtainedDefinition = BoxDefinition(
        width=30, height=30, background_color=Color(0, 0, 0, 200)
    )
    LayoutDefinition = BoxLayoutDefinition(
        boxes_per_row=None, boxes_per_column=1, spacing=20
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


class RoundaboutDisplay(ShadeInNumberDisplay):
    ScoreBoxDefinition = BoxDefinition(
        width=40, height=40, background_color=Color(200, 0, 0)
    )


class PermitRefusalDisplay(ShadeInNumberDisplay):
    ScoreBoxDefinition = BoxDefinition(
        width=40, height=40, background_color=Color(200, 0, 0)
    )


class BisDisplay(ShadeInNumberDisplay):
    ScoreBoxDefinition = BoxDefinition(
        width=40, height=40, background_color=Color(255, 192, 200)
    )
    LayoutDefinition = BoxLayoutDefinition(
        boxes_per_row=None, boxes_per_column=2, spacing=20
    )


class PoolDisplay(ShadeInNumberDisplay):
    ScoreBoxDefinition = BoxDefinition(
        width=40, height=40, background_color=Color(0, 100, 200)
    )
    LayoutDefinition = BoxLayoutDefinition(
        boxes_per_row=None, boxes_per_column=2, spacing=20
    )


class SingleInvestmentDisplay(ShadeInNumberDisplay):
    ScoreBoxDefinition = BoxDefinition(
        width=40, height=40, background_color=Color(128, 0, 128)
    )


class ScoreBoardDisplay(Box):
    """Collection of all of the score boxes except for the parks, which are per-street."""
