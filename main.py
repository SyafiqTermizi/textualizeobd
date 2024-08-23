from typing import Any

import obd
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Digits, Label


class Display(Widget):
    value: reactive[int] = reactive(0)

    def __init__(self, label: str, padding: int, *args, **kwargs) -> None:
        self.label = label
        self.padding = padding
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Label(self.label)
        yield Digits(f"{self.value}".zfill(self.padding))


class OBDDisplay(App):
    CSS_PATH = "styles.tcss"

    def compose(self) -> ComposeResult:
        yield Display(label="Speed (km/h)", padding=3, id="speed")
        yield Display(label="RPM (x1000)", padding=2, id="rpm")
        yield Display(label="Temp (c)", padding=3, id="temp")

    def update_rpm(self, response):
        self.query_one("#rpm").value = response.value

    def update_speed(self, response):
        self.query_one("#speed").value = response.value

    def update_temp(self, response):
        self.query_one("#temp").value = response.value

    def on_mount(self):
        self.connection = obd.Async()

        self.connection.watch(obd.commands.COOLANT_TEMP, callback=self.update_temp)
        self.connection.watch(obd.commands.RPM, callback=self.update_rpm)
        self.connection.watch(obd.commands.SPEED, callback=self.update_speed)

        self.connection.start()

    def exit(
        self,
        result: Any | None = None,
        return_code: int = 0,
        message: str | None = None,
    ) -> None:
        self.connection.stop()
        return super().exit(result, return_code, message)


if __name__ == "__main__":
    OBDDisplay().run()
