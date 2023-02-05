import json
from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuSize, RichMenuBounds, RichMenuArea, PostbackAction, RichMenuSwitchAction, RichMenuAlias

with open("../setting.json") as json_file:
    config = json.load(json_file)
line_bot_api = LineBotApi(config["CHANNEL_ACCESS_TOKEN"])

rich_menu = RichMenu(size = RichMenuSize(width = 1576, height = 1001),
 selected = True,
 name = "user_menu_1",
 chat_bar_text = "查看更多",
 areas = [
    RichMenuArea(bounds = RichMenuBounds(x = 788, y = 0, width = 788, height = 120), action = RichMenuSwitchAction(label = "Switch menu", rich_menu_alias_id = "book_menu_1", data = "switch menu")),
    RichMenuArea(bounds = RichMenuBounds(x = 0, y = 120, width = 394, height = 881), action = PostbackAction(label = "edit profile", data = "action=teaching&type=teaching")),
    RichMenuArea(bounds = RichMenuBounds(x = 394, y = 120, width = 394, height = 881), action = PostbackAction(label = "edit profile", data = "action=edit_profile&type=get_all")),
    RichMenuArea(bounds = RichMenuBounds(x = 788, y = 120, width = 394, height = 881), action = PostbackAction(label = "edit profile", data = "action=edit_profile&type=begin")),
    RichMenuArea(bounds = RichMenuBounds(x = 1182, y = 120, width = 394, height = 881), action = PostbackAction(label = "contact us", data = "action=contact_us&type=contact_us")),
  ])

rich_menu_id = line_bot_api.create_rich_menu(rich_menu = rich_menu)

with open("../static/rich_menu/user_menu_1.jpeg", "rb") as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, "image/jpeg",f)

line_bot_api.create_rich_menu_alias(RichMenuAlias("user_menu_1", rich_menu_id))
line_bot_api.set_default_rich_menu(rich_menu_id)