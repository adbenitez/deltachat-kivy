from deltachat import Account, account_hookimpl
from deltachat.tracker import ConfigureTracker
from typing import List
from deltachat.capi import ffi, lib

class DeltaChatClient:
    def __init__(self, db_path: str) -> None:
        self.account = Account(db_path)
        self.account.add_account_plugin(self)

    def configure(self, addr: str, mail_pw: str, **kwargs) -> None:
        kwargs["addr"] = addr
        kwargs["mail_pw"] = mail_pw
        self.account.update_config(kwargs)
        with self.account.temp_plugin(ConfigureTracker(self.account)) as tracker:
            self.account.configure()
            tracker.wait_finish()

    def connect(self) -> None:
        assert self.account.is_configured(), "Account not configured"
        self.account.start_io()

    def disconnect(self) -> None:
        self.account.shutdown()

    def get_chats_ids(self) -> List[int]:
        """return list of chat ids."""
        dc_chatlist = ffi.gc(
            lib.dc_get_chatlist(self.account._dc_context, 0, ffi.NULL, 0),
            lib.dc_chatlist_unref
        )

        assert dc_chatlist != ffi.NULL
        chatlist = []
        for i in range(0, lib.dc_chatlist_get_cnt(dc_chatlist)):
            chatlist.append(lib.dc_chatlist_get_chat_id(dc_chatlist, i))
        return chatlist

    def get_messages_ids(self, chat_id: int) -> List[int]:
        """return list of ids from messages in this chat."""
        dc_array = ffi.gc(
            lib.dc_get_chat_msgs(self.account._dc_context, chat_id, 0, 0),
            lib.dc_array_unref
        )
        return [lib.dc_array_get_id(dc_array, i) for i in range(0, lib.dc_array_get_cnt(dc_array))]

    # EVENTS

    @account_hookimpl
    def ac_incoming_message(self, message) -> None:
        # always accept incoming contact requests
        message.create_chat()
