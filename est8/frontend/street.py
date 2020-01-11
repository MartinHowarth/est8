from typing import Optional, Callable, List

from shimmer.display.components.box import Box, BoxDefinition
from shimmer.display.components.box_layout import BoxLayoutDefinition, BoxRow
from shimmer.display.alignment import HorizontalAlignment, VerticalAlignment
from shimmer.display.widgets.button import ButtonDefinition, Button
from shimmer.display.widgets.multiple_choice_buttons import (
    MultipleChoiceButtons,
    MultipleChoiceButtonsDefinition,
    MultipleChoiceQuestionDefinition,
)
from shimmer.display.widgets.text_box import TextBoxDefinition, TextBox

from ..backend.house import House
from ..backend.street import Street
from .input_handler import InputHandler
from .score_displays import ParkDisplay


class StreetDisplay(Box):
    plot_size = 60, 100
    spacing = 20

    def __init__(
        self,
        street: Street,
        street_index: int,
        on_plot_click_callback: Callable[[int, int], Optional[bool]],
    ):
        super(StreetDisplay, self).__init__()

        self.on_plot_click_callback = on_plot_click_callback
        self.street: Street = street
        self.street_index: int = street_index
        self.plots = self._create_empty_plots(self.street.definition.num_houses)
        self.plot_layout = BoxRow(self.plots, spacing=self.spacing)
        self.add(self.plot_layout)
        self.park_display = ParkDisplay(self.street.definition.park_scoring)
        self.park_display.set_position_in_alignment_with(
            self, align_x=HorizontalAlignment.right
        )
        # park_x = (
        #     self.plot_layout.rect.width
        #     - self.park_display.rect.width
        # )
        self.park_display.position = (
            self.park_display.x,
            self.plot_size[1] + 10,
        )
        self.add(self.park_display)

    def _create_empty_plots(self, num_plots) -> List[Button]:
        buttons = []
        for index in range(num_plots):
            button = Button(
                ButtonDefinition(
                    text="P"
                    if self.street.definition.can_have_pool_at(index)
                    else None,
                    width=self.plot_size[0],
                    height=self.plot_size[1],
                    depressed_color=None,
                    on_press=self._create_on_plot_click_callback(index),
                )
            )
            buttons.append(button)
        return buttons

    def _create_on_plot_click_callback(self, plot_index) -> Callable:
        def inner(*_, **__):
            return self.on_plot_click_callback(self.street_index, plot_index)

        return inner

    def update(self) -> None:
        self.park_display.set_score_obtained(self.street.num_parks)
