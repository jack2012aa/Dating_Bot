import models
from services import line_bot_api, text_dict
from linebot.models import PostbackEvent, TextSendMessage

def insert_or_delete_tag(event: PostbackEvent, tag: str):
    '''Insert tag into editting_tags if it isn't exist, else delete it.'''

    exist = models.book.has_editting_tag(event.source.user_id, tag)
    if exist:
        models.book.delete_editting_tag(event.source.user_id, tag)
        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text = text_dict["Delete tag"].format(tag = tag))])
    else:
        models.book.insert_editting_tag(event.source.user_id, tag)
        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text = text_dict["Insert tag"].format(tag = tag))])
    return 0