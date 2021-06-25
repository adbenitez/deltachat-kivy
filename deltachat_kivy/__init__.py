from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.spinner import MDSpinner
from pkg_resources import DistributionNotFound, get_distribution
from kivymd.uix.selection import MDSelectionList
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.lang import Builder

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    __version__ = "0.0.0.dev0-unknown"

Builder.load_string("""
<Separator>:
    rgba: app.theme_cls.divider_color
    canvas:
        Color:
            rgba: self.rgba or app.theme_cls.divider_color
        Rectangle:
            pos: self.pos
            size: self.size

<HSeparator@Separator>:
    size_hint_y: None
    height: dp(2)

<VSeparator@Separator>:
    size_hint_x: None
    width: dp(2)
""")


class SelectableRecycleBoxLayout(
        FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout
):
    """Adds selection and focus behaviour to the view."""


class SelectableRecycleGridLayout(
        FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout
):
    """Adds selection and focus behaviour to the view."""


class SpinnerDialog(MDDialog):
    def __init__(self, text: str = "Loading...", **kwargs) -> None:
        box = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(10),
            spacing=dp(12),
        )
        box.add_widget(
            MDSpinner(
                size_hint=(None, None),
                size=(dp(46), dp(46)),
            )
        )
        box.add_widget(
            MDLabel(
                text=text,
            )
        )

        super().__init__(type="custom", content_cls=box, **kwargs)


class Separator(Widget):
    """Separator line between widgets."""

    def __init__(self, rgba=None, **kwargs) -> None:
        super().__init__(**kwargs)
        if rgba is not None:
            self.rgba = rgba


class HSeparator(Separator):
    pass


class VSeparator(Separator):
    pass
