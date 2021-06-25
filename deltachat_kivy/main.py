import os
from threading import Thread

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField

from . import HSeparator, SpinnerDialog, VSeparator
from .client import DeltaChatClient
from .conversation import Conversation, ConversationList
from .utils import get_account_path


class DeltaChatApp(MDApp):
    def build(self) -> ScreenManager:
        self.client = DeltaChatClient(get_account_path())
        self.sm = ScreenManager()

        if self.client.account.is_configured():
            self.create_chat_screen(True)
        else:
            self.config_screen = ConfigScreen(self)
            self.sm.add_widget(self.config_screen)
            self.sm.current = self.config_screen.name

        return self.sm

    def create_chat_screen(self, select: bool = False) -> None:
        self.chat_screen = ChatScreen(self)
        self.sm.add_widget(self.chat_screen)
        if select:
            self.sm.current = self.chat_screen.name


class ConfigScreen(Screen):
    def __init__(self, app: DeltaChatApp) -> None:
        super().__init__(name="config")
        self.client = app.client
        self.app = app

        box = BoxLayout(
            orientation="vertical",
            size_hint=(0.5, None),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.add_widget(box)

        self.addr_tf = MDTextField(
            hint_text="E-Mail",
            multiline=False,
            write_tab=False,
        )
        box.add_widget(self.addr_tf)

        self.password_tf = MDTextField(
            hint_text="Password",
            password=True,
            multiline=False,
            write_tab=False,
        )
        box.add_widget(self.password_tf)

        login_btn = MDRaisedButton(
            text="Login",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            md_bg_color=app.theme_cls.primary_color,
        )
        login_btn.bind(on_release=self._on_login)
        box.add_widget(login_btn)

    def _on_login(self, *args) -> None:
        dialog = SpinnerDialog(auto_dismiss=False)
        dialog.open()
        Thread(target=self._configure, args=(dialog,), daemon=True).start()

    def _configure(self, dialog) -> None:
        try:
            self.client.configure(self.addr_tf.text, self.password_tf.text)
            Clock.schedule_once(lambda x: self.app.create_chat_screen(True), 0)
        except Exception as ex:
            Clock.schedule_once(
                lambda x: Snackbar(text=f"ERROR: Configuration failed.").open(), 0
            )
        finally:
            Clock.schedule_once(lambda x: dialog.dismiss(), 0)


class ChatScreen(Screen):
    def __init__(self, app: DeltaChatApp) -> None:
        super().__init__(name="chat")
        self.chatlist = ConversationList(app.client, size_hint_x=0.4)
        self.conversation = Conversation(self.chatlist)
        self.message_editor = TextInput(
            hint_text="Message",
            multiline=False,
            on_text_validate=self._send_msg,
        )
        self.send_btn = MDRaisedButton(
            text="SEND",
            md_bg_color=app.theme_cls.primary_color,
            size_hint=(None, 1),
            on_release=self._send_msg,
        )

        editor_box = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
            padding=dp(10),
        )
        editor_box.add_widget(self.message_editor)
        editor_box.add_widget(self.send_btn)

        chat_vbox = BoxLayout(orientation="vertical")
        chat_vbox.add_widget(self.conversation)
        chat_vbox.add_widget(HSeparator())
        chat_vbox.add_widget(editor_box)

        root_hbox = BoxLayout(orientation="horizontal")
        root_hbox.add_widget(self.chatlist)
        root_hbox.add_widget(VSeparator())
        root_hbox.add_widget(chat_vbox)

        self.add_widget(root_hbox)

        app.client.connect()

    def _send_msg(self, *args) -> None:
        account = self.chatlist.client.account
        chat = account.get_chat_by_id(self.chatlist.selected_chat)
        chat.send_text(self.message_editor.text)
        self.message_editor.text = ""

        def task(*args):
            self.message_editor.focus = True

        Clock.schedule_once(task, 0)


def main():
    DeltaChatApp().run()
