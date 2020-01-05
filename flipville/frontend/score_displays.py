from typing import Tuple, Optional

from shimmer.display.data_structures import (
    LabelDefinition,
    VerticalAlignment,
    HorizontalAlignment,
    Color,
)
from shimmer.display.components.box import Box, BoxDefinition
from shimmer.display.widgets.text_box import TextBox, TextBoxDefinition
from shimmer.display.components.box_layout import (
    BoxRow,
    BoxLayoutDefinition,
    create_box_layout,
)


ScoreBoxDefinition = BoxDefinition(
    width=40, height=40, background_color=Color(0, 200, 0)
)
ScoreBoxObtainedDefinition = BoxDefinition(
    width=30, height=30, background_color=Color(0, 0, 0, 200)
)


def create_park_score_layout(park_scores: Tuple[int, ...]) -> BoxRow:
    layout_defn = BoxLayoutDefinition(
        boxes_per_row=None, boxes_per_column=1, spacing=10
    )
    boxes = []
    for score in park_scores:
        box = Box(ScoreBoxDefinition)
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


def create_park_obtained_layout(num_parks: int) -> BoxRow:
    layout_defn = BoxLayoutDefinition(
        boxes_per_row=None, boxes_per_column=1, spacing=20
    )
    boxes = []
    for score in range(num_parks):
        box = Box(ScoreBoxObtainedDefinition)
        boxes.append(box)
    layout = create_box_layout(definition=layout_defn, boxes=boxes)

    return layout


class ParkDisplay(Box):
    def __init__(self, park_scores: Tuple[int, ...]):
        super(ParkDisplay, self).__init__()
        self.park_scores = park_scores
        self.park_layout = create_park_score_layout(self.park_scores)
        self.park_obtained_layout: Optional[BoxRow] = None
        self.add(self.park_layout)

    def set_parks_obtained(self, num_parks: int) -> None:
        if self.park_obtained_layout is not None:
            self.remove(self.park_obtained_layout)

        self.park_obtained_layout = create_park_obtained_layout(num_parks)
        self.park_obtained_layout.position = 5, 5
        self.add(self.park_obtained_layout)
