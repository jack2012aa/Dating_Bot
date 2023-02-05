import json
from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuSize, RichMenuBounds, RichMenuArea, PostbackAction, RichMenuSwitchAction, RichMenuAlias

with open("../setting.json") as json_file:
    config = json.load(json_file)
line_bot_api = LineBotApi(config["CHANNEL_ACCESS_TOKEN"])

rich_menu = RichMenu(size = RichMenuSize(width = 1572, height = 1001),
 selected = True,
 name = "book_menu_1",
 chat_bar_text = "查看更多",
 areas = [
    RichMenuArea(bounds = RichMenuBounds(x = 0, y = 0, width = 786, height = 120), action = RichMenuSwitchAction(labe = "Switch menu", rich_menu_alias_id = "user_menu_1", data = "switch menu")),
    RichMenuArea(bounds = RichMenuBounds(x = 0, y = 121, width = 692, height = 880), action = PostbackAction(label = "find book", data = "action=find_book&type=act_info")),
    RichMenuArea(bounds = RichMenuBounds(x = 693, y = 121, width = 440, height = 440), action = PostbackAction(label = "upload book", data = "action=upload_book&type=begin")),
    RichMenuArea(bounds = RichMenuBounds(x = 693, y = 561, width = 440, height = 440), action = PostbackAction(label = "find book", data = "action=find_book&type=begin")),
    RichMenuArea(bounds = RichMenuBounds(x = 1133, y = 121, width = 440, height = 440), action = PostbackAction(label = "upload book", data = "action=upload_book&type=my_book")),
    RichMenuArea(bounds = RichMenuBounds(x = 1122, y = 561, width = 440, height = 440), action = PostbackAction(label = "find book", data = "action=find_book&type=invite")),
  ])

rich_menu_id = line_bot_api.create_rich_menu(rich_menu = rich_menu)

with open("../static/rich_menu/book_menu_1.jpeg", "rb") as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, "image/jpeg",f)
line_bot_api.create_rich_menu_alias(RichMenuAlias("book_menu_1", rich_menu_id))