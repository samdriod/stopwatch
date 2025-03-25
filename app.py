from typing import Type
from time import monotonic
from textual._path import CSSPathType
from textual.app import App, ComposeResult
from textual.driver import Driver
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Digits, Header, Footer
from textual.reactive import reactive

class TimeDisplay(Digits):
    """A widget to display elapsed time"""
    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler for when the widget is mounted"""
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        """Update the time to current time"""
        self.time = self.total + (monotonic() - self.start_time)

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes"""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")

    def start(self) -> None:
        """Start (or resume) the timer"""
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self) -> None:
        """Stop the timer"""
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def reset(self) -> None:
        """Reset the timer"""
        self.total = 0
        self.time = 0

class BtnContainer(Horizontal):
    """A container with buttons"""
    def compose(self) -> ComposeResult:
        """Compose the buttons"""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")

class StopWatch(Vertical):
    """A widget containing main components"""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler for button press"""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if event.button.id == "start":
            time_display.start()
            self.add_class("started")
        elif event.button.id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif event.button.id == "reset":
            time_display.reset()

    def compose(self) -> ComposeResult:
        """Compose the Stopwatch"""
        yield TimeDisplay()
        yield BtnContainer()

class MainApp(App):
    """The main App"""

    BINDINGS = [
        ("h", "toggle_head_foot", "Toggles Header and Footer")
    ]

    CSS = """
        Screen {
            align: center middle;
        }
        """
    CSS_PATH = "main.css"

    def __init__(
            self,
            driver_class: Type[Driver] | None = None,
            css_path: CSSPathType | None = None,
            watch_css: bool = False,
            ansi_color: bool = False,
    ):
        super().__init__(driver_class, css_path, watch_css, ansi_color)

        self.header = Header()
        self.header.visible = False

        self.footer = Footer()
        self.footer.visible = False

    def on_mount(self) -> None:
        """Method called when the component is mounted."""
        self.theme = "nord"

    def compose(self) -> ComposeResult:
        """Compose the App"""
        yield self.header
        yield StopWatch(id="watch")
        yield self.footer

    def action_toggle_head_foot(self) -> None:
        """Toggle Header Footer"""
        if self.header.visible and self.footer.visible:
            self.header.visible = False
            self.footer.visible = False
        else:
            self.header.visible = True
            self.footer.visible = True

if __name__ == '__main__':
    app = MainApp()
    app.run()
