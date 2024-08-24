import os
from typing import Any

import obd
from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Digits, Header, Label


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

    oil_temp = reactive(0.0)
    coolant_temp = reactive(0.0)
    speed = reactive(0)
    rpm = reactive(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Container(id="grid"):
            yield Display(
                label="Speed (km/h)",
                padding=3,
            ).data_bind(value=OBDDisplay.speed)

            yield Display(
                label="RPM",
                padding=5,
            ).data_bind(value=OBDDisplay.rpm)

            yield Display(
                label="Coolant temp (ºc)",
                padding=3,
            ).data_bind(value=OBDDisplay.coolant_temp)

            yield Display(
                label="Oil temp (ºc)",
                padding=3,
            ).data_bind(value=OBDDisplay.oil_temp)

        yield Container(id="bar")

    def update_rpm(self, response):
        self.rpm = response.value.magnitude

    def update_speed(self, response):
        self.speed = response.value.magnitude

    def update_coolant_temp(self, response):
        self.coolant_temp = response.value.magnitude

    def update_oil_temp(self, response):
        self.coolant_temp = response.value.magnitude

    def update_throttle_pos(self, response):
        val = response.value.magnitude
        self.query_one("#bar").styles.width = f"{val}%"

    def on_mount(self):
        self.connection = obd.Async(portstr=os.environ.get("OBD_PORT"))

        self.connection.watch(
            obd.commands.COOLANT_TEMP,
            callback=self.update_coolant_temp,
        )
        self.connection.watch(
            obd.commands.OIL_TEMP,
            callback=self.update_oil_temp,
        )
        self.connection.watch(obd.commands.RPM, callback=self.update_rpm)
        self.connection.watch(obd.commands.SPEED, callback=self.update_speed)
        self.connection.watch(
            obd.commands.THROTTLE_POS, callback=self.update_throttle_pos
        )

        self.query_one("#bar").styles.width = "0%"

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
    load_dotenv()
    OBDDisplay().run()
