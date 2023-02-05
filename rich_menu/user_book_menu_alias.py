import json
from linebot import LineBotApi
from linebot.models import RichMenuAlias, swi

with open("../setting.json") as json_file:
    config = json.load(json_file)
line_bot_api = LineBotApi(config["CHANNEL_ACCESS_TOKEN"])

line_bot_api.set_default_rich_menu("richmenu-698c579ff0a6412c58a2f6682a9db840")
line_bot_api.create_rich_menu_alias(RichMenuAlias("user", "richmenu-698c579ff0a6412c58a2f6682a9db840"))
line_bot_api.create_rich_menu_alias(RichMenuAlias("book", "richmenu-19f6de319ae003f0419707f484e0d3f6"))