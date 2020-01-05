from typing import Optional, Callable, List

from shimmer.display.components.box_layout import BoxLayoutDefinition, BoxRow
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


class StreetDisplay(BoxRow):
    plot_size = 60, 100
    spacing = 20

    def __init__(
        self,
        street: Street,
        street_index: int,
        on_plot_click_callback: Callable[[int, int], Optional[bool]],
    ):
        self.on_plot_click_callback = on_plot_click_callback
        self.street: Street = street
        self.street_index: int = street_index
        self.plots = self._create_empty_plots(self.street.definition.num_houses)
        super(StreetDisplay, self).__init__(self.plots, spacing=self.spacing)

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
            return self.on_plot_click(plot_index)

        return inner

    def on_plot_click(self, plot_index) -> Optional[bool]:
        return self.on_plot_click_callback(self.street_index, plot_index)
