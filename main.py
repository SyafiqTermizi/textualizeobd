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

    def watch_value(self, val):
        self.query_one(Digits).update(f"{val}".zfill(self.padding))

    def compose(self) -> ComposeResult:
        yield Label(self.label)
        yield Digits()


class OBDDisplay(App):
    CSS_PATH = "styles.tcss"

    temp = reactive(0)
    speed = reactive(0)
    rpm = reactive(0)

    def compose(self) -> ComposeResult:
        yield Display(
            label="Speed (km/h)",
            padding=3,
            id="speed",
        ).data_bind(value=OBDDisplay.speed)

        yield Display(
            label="RPM (x1000)",
            padding=2,
            id="rpm",
        ).data_bind(value=OBDDisplay.rpm)

        yield Display(
            label="Temp (c)",
            padding=3,
            id="temp",
        ).data_bind(value=OBDDisplay.temp)

    def update_rpm(self, response):
        self.rpm = response.value

    def update_speed(self, response):
        self.speed = response.value

    def update_temp(self, response):
        self.temp = response.value

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
