import models
from services import cache, line_bot_api, text_dict, cancel_quick_reply_button
from linebot.models import Event, TextSendMessage, QuickReply

def begin_update(event: Event, type: str):
    '''Show present value and put user into changing profile state'''

    cache[event.source.user_id] = ["edit_profile", type]
    profile_dict = {
        "lineID": "line id",
    }
    value = models.user.get_user_profiles(event.source.user_id, [type])[0]
    if value == None:
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text = text_dict["Null profile"].format(profile_type = profile_dict[type])),
            TextSendMessage(text = text_dict["Edit profile"].format(profile_type = profile_dict[type]), quick_reply = QuickReply(items = [cancel_quick_reply_button]))
            ]
        )
    else:
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text = text_dict["Present profile"].format(profile_type = type, profile = value)),
            TextSendMessage(text = text_dict["Edit profile"].format(profile_type = profile_dict[type]), quick_reply = QuickReply(items = [cancel_quick_reply_button]))
            ]
        )
    return 0