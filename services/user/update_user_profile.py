import models
from services import text_dict, line_bot_api
from linebot.models import Event, TextSendMessage

def update_user_profile(event: Event, field: str, value):
    '''Update user profile(field)'''

    models.user.update_user_profile(event.source.user_id, field, value)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Update successfully"].format(value = value)))
    return 0