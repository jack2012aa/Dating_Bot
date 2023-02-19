import models
from services import line_bot_api, text_dict
from linebot.models import Event, TextSendMessage

def add_new_user(event: Event):
    '''Insert userID into friends table and show welcome message'''    
    models.user.insert_user(event.source.user_id)
    line_bot_api.reply_message(event.reply_token, [TextSendMessage(text = text_dict["Welcome"]), TextSendMessage(text = text_dict["User contract"])])
    return 0