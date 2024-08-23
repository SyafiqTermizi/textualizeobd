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
        yield Display(label="Speed (km/h)", padding=3)
        yield Display(label="RPM (x1000)", padding=2)
        yield Display(label="Temp (c)", padding=3)


if __name__ == "__main__":
    OBDDisplay().run()
