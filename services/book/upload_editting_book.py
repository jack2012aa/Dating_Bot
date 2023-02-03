import models
from services import line_bot_api, text_dict
from linebot.models import PostbackEvent, TextSendMessage

def upload_editting_book(event: PostbackEvent):
    '''Upload user's book if its information is filled in.'''

    empty = models.book.has_empty_column(event.source.user_id)
    if empty:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Empty column"]))
        return 0
    else:
        models.book.upload_book(event.source.user_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Upload book successfully"]))
        return 0