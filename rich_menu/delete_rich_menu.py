import json
from linebot import LineBotApi
from linebot.models import RichMenuResponse

with open("../setting.json") as json_file:
    config = json.load(json_file)
line_bot_api = LineBotApi(config["CHANNEL_ACCESS_TOKEN"])

rich_menu = line_bot_api.get_rich_menu_list()
for menu in rich_menu:
    line_bot_api.delete_rich_menu(menu.rich_menu_id)

line_bot_api.delete_rich_menu_alias("user_menu_4")
line_bot_api.delete_rich_menu_alias("book_menu_4")
