import json
from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuSize, RichMenuBounds, RichMenuArea, PostbackAction

with open("setting.json") as json_file:
    config = json.load(json_file)
line_bot_api = LineBotApi(config["CHANNEL_ACCESS_TOKEN"])
'''
rich_menu = RichMenu(size = RichMenuSize(width = 824, height = 550),
 selected = False,
 name = "Book_test_1",
 chat_bar_text = "查看更多",
 areas = [RichMenuArea(bounds = RichMenuBounds(x = 0, y = 0, width = 824, height = 275), action = PostbackAction(label = "edit profile", data = "action=edit_profile&type=begin")),
  RichMenuArea(bounds = RichMenuBounds(x = 0, y = 275, width = 274, height = 275), action = PostbackAction(label = "upload book", data = "action=upload_book&type=begin")),
  RichMenuArea(bounds = RichMenuBounds(x = 275, y = 275, width = 274, height = 275), action = PostbackAction(label = "find book", data = "action=find_book&type=begin")),
  RichMenuArea(bounds = RichMenuBounds(x = 550, y = 275, width = 274, height = 275), action = PostbackAction(label = "modify book", data = "action=modify_book&type=begin")),
  ])

rich_menu_id = line_bot_api.create_rich_menu(rich_menu = rich_menu)
print(rich_menu_id)

with open("./static/rich_menu/book_test_1.jpeg", "rb") as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, "image/jpeg",f)
'''
line_bot_api.set_default_rich_menu(rich_menu_id = "richmenu-aa9beac293449ffcdd317f1bae00417f")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            