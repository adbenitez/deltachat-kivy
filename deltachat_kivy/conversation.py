from deltachat import Account, account_hookimpl
from kivy.lang import Builder
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.uix.label import MDLabel
from kivymd.uix.list import ImageLeftWidget, OneLineAvatarListItem

from .client import DeltaChatClient

Builder.load_string(
    """
<ConversationList>:
    viewclass: "ConversationListItem"
    SelectableRecycleBoxLayout:
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: "vertical"
        multiselect: False
<ConversationListItem>:
    # Draw a background to indicate selection
    canvas.before:
        Color:
            rgba: app.theme_cls.primary_color[:-1]+[.2] if self.selected else (0, 0, 0, 0)
        Rectangle:
            pos: self.pos
            size: self.size


<Conversation>:
    viewclass: "ConversationItem"
    SelectableRecycleGridLayout:
        cols: 1
        padding: dp(10)
        default_size: None, dp(52)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        multiselect: True

<ConversationItem>:
    default_size_hint: 1, None
    orientation: "horizontal"
"""
)


class ConversationList(RecycleView):
    selected_chat = NumericProperty()

    def __init__(self, client: DeltaChatClient, **kwargs) -> None:
        super().__init__(**kwargs)
        self.client = client
        client.account.add_account_plugin(self)
        self._load_data()

    def _load_data(self) -> None:
        self.data = [{"chat_id": i} for i in self.client.get_chats_ids()]

    @account_hookimpl
    def ac_process_ffi_event(self, ffi_event) -> None:
        if ffi_event.name != "DC_EVENT_INFO":
            print(ffi_event)  # TODO: debugging, remove this
        if ffi_event.name == "DC_EVENT_MSGS_CHANGED":
            self._load_data()
        if ffi_event.name == "DC_EVENT_CHAT_MODIFIED":
            self._load_data()


class Conversation(RecycleView):
    def __init__(self, chatlist: ConversationList, **kwargs) -> None:
        super().__init__(**kwargs)
        self.chatlist = chatlist
        self.client = chatlist.client
        chatlist.bind(selected_chat=self.on_selected_chat)
        self.client.account.add_account_plugin(self)

    def _load_data(self, chat_id: int) -> None:
        self.data = [
            {"msg_id": i} for i in self.chatlist.client.get_messages_ids(chat_id)
        ]

    def on_selected_chat(self, chatlist: ConversationList, chat_id: int) -> None:
        self._load_data(chat_id)

    @account_hookimpl
    def ac_process_ffi_event(self, ffi_event) -> None:
        if ffi_event.name == "DC_EVENT_MSGS_CHANGED":
            if self.chatlist.selected_chat:
                self._load_data(self.chatlist.selected_chat)
        if ffi_event.name in ("DC_EVENT_CHAT_MODIFIED", "DC_EVENT_INCOMING_MSG"):
            if ffi_event.data1 == self.chatlist.selected_chat:
                self._load_data(ffi_event.data1)


class ConversationListItem(RecycleDataViewBehavior, OneLineAvatarListItem):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.avatar = ImageLeftWidget(radius=(10,))
        self.add_widget(self.avatar)

    def refresh_view_attrs(self, rv, index, data):
        """Catch and handle the view changes"""
        self.index = index
        chat = rv.client.account.get_chat_by_id(data["chat_id"])
        self.avatar.source = chat.get_profile_image() or ""
        data = {"text": chat.get_name()}
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """Add selection on touch down"""
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        self.selected = is_selected
        if is_selected:
            rv.selected_chat = rv.data[index]["chat_id"]
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))


class ConversationItem(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.body = MDLabel()
        self.add_widget(self.body)

    def refresh_view_attrs(self, rv, index, data):
        """Catch and handle the view changes"""
        self.index = index
        msg = rv.client.account.get_message_by_id(data["msg_id"])
        if msg.filename:
            text = "[File]"
            if msg.text:
                text += " - "
        else:
            text = ""
        text += msg.text
        name = msg.get_sender_contact().name
        self.body.text = f"{name}> {text}"
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """Add selection on touch down"""
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            pass  # return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        self.selected = is_selected
