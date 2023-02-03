import models
from services import cache, line_bot_api, text_dict, cancel_quick_reply_button
from linebot.models import PostbackEvent, TextSendMessage, QuickReply

def begin_edit(event: PostbackEvent, type:str):
    '''中文'''

    cache[event.source.user_id] = ["upload_book", type]
    value = models.book.get_editting_book_information(event.source.user_id, [type])[0]

    field_dict = {
        "name":"書名",
        "summary":"心得",
        "exchange_method":"交換方式"
    }
    if value == None:
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text = text_dict["Null information"].format(field = field_dict[type])),
            TextSendMessage(text = text_dict["Edit information"].format(field = field_dict[type]), quick_reply = QuickReply(items = [cancel_quick_reply_button]))
            ]
        )
    else:
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text = text_dict["Present information"].format(field = field_dict[type], information = value)),
            TextSendMessage(text = text_dict["Edit information"].format(field = field_dict[type]), quick_reply = QuickReply(items = [cancel_quick_reply_button]))
            ]
        )
    return 0