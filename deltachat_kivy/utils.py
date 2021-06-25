import json
import os

app_path = os.path.join(os.path.expanduser("~"), ".config", "deltachat-kivy")
cfg_path = os.path.join(app_path, "config.json")
acc_path = os.path.join(app_path, "accounts")


if not os.path.exists(acc_path):
    os.makedirs(app_path)


def get_account_path() -> str:
    return os.path.join(acc_path, "ac0", "db.sqlite")
