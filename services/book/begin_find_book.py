from services import cancel_quick_reply_button, line_bot_api, text_dict, cache
from linebot.models import PostbackEvent, QuickReply, QuickReplyButton, PostbackAction, TextSendMessage

def begin_find_book(event: PostbackEvent):
    '''Show quick replys of fields to find books'''

    #status: [action, type, categories, tags]
    status = cache.get(event.source.user_id, None)
    if status == None or status[0] != "find_book" or status[1] != "fill_in":
        value = None
    else:
        value = ""
        categories = cache.get(event.source.user_id, None)[2]
        if len(categories) != 0:
            value = "分類：" + " ".join(categories)
        tags = cache.get(event.source.user_id, None)[3]
        if len(tags) != 0:
            if len(value) == 0:
                value = "標籤：" + " ".join(tags)
            else:
                value = value + "\n標籤：" + " ".join(tags)

    quick_reply_buttons = [
        QuickReplyButton(action = PostbackAction(label = "分類", display_text = "選擇分類", data = "action=find_book&type=categories")),
        QuickReplyButton(action = PostbackAction(label = "標籤", display_text = "選擇標籤", data = "action=find_book&type=tags")),
        ＱuickReplyButton(action = PostbackAction(label = "隨機", display_text = "隨機搜尋", data = "action=find_book&type=random_find")),
        QuickReplyButton(action = PostbackAction(label = "搜尋", display_text = "搜尋書籍", data = "action=find_book&type=find")),
        cancel_quick_reply_button
    ]
    if value == None:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Find books"], quick_reply = QuickReply(items = quick_reply_buttons)))
    else:
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text = text_dict["Present search fields"].format(values = value)),
            TextSendMessage(text = text_dict["Find books"], quick_reply = QuickReply(items = quick_reply_buttons))
        ])
    return 0    