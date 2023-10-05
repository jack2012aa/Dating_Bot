import models
from services import cancel_quick_reply_button, line_bot_api, text_dict
from linebot.models import PostbackEvent, QuickReplyButton, QuickReply, PostbackAction, TextSendMessage

def begin_edit_tag_or_category(event: PostbackEvent, type: str):
    '''Show choosable tags/categories'''

    if type == "category":
        choices = models.exchange_book.get_all_categories()
        value = models.exchange_book.get_editting_book_information(event.source.user_id, [type])[0]
    elif type == "tag":
        choices = models.exchange_book.get_all_tags()
        values = models.exchange_book.get_editting_tags(event.source.user_id)
        if values[0] == None:
            value = None
        else:
            value = " ".join(values)

    quick_reply_buttons = []
    for choice in choices:
        quick_reply_buttons.append(QuickReplyButton(action = PostbackAction(label = choice, data = "action=upload_book&type=choose_"+type+"&"+type+"="+choice)))
    quick_reply_buttons.append(cancel_quick_reply_button)
    
    field = {"category": "分類", "tag": "標籤"}
    if value == None:
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text = text_dict["Null information"].format(field = field[type])),
            TextSendMessage(text = text_dict["Choose information"].format(field = field[type]), quick_reply = QuickReply(items = quick_reply_buttons))
            ]
        )
    else:
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text = text_dict["Present information"].format(field = field[type], information = value)),
            TextSendMessage(text = text_dict["Choose information"].format(field = field[type]), quick_reply = QuickReply(items = quick_reply_buttons))
        ])
    return 0