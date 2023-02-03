import models
from services import cache, line_bot_api, text_dict
from linebot.models import Event,TextSendMessage

def insert_or_update_book(event: Event, type: str, value: str):
    '''Update type with value'''

    cache.pop(event.source.user_id, None)
    if type == "choose_category":
        type = "category"
    models.book.insert_or_update_editting_book(event.source.user_id, type, value)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Upload successfully"].format(value = value)))
    return 0