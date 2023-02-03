import models
from services import cancel_quick_reply_button, line_bot_api, text_dict, cache
from linebot.models import Event, QuickReply, TextSendMessage


def begin_update_with_warning(event: Event, type, warning_message: str):
    '''Show warning of input birth year.'''
    
    cache[event.source.user_id] = ["edit_profile", type]
    profile_dict = {"email":"學校信箱","birth_year":"出生年份"}
    value = models.user.get_user_profiles(event.source.user_id, [type])[0]
    if value != None:
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text = text_dict["Present profile"].format(profile_type = type, profile = value)),
                TextSendMessage(text = text_dict["Edit profile"].format(profile_type = type) + "\n" + warning_message, quick_reply = QuickReply(items = [cancel_quick_reply_button]))
            ]
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text = text_dict["Null profile"].format(profile_type = profile_dict[type])),
                TextSendMessage(text = text_dict["Edit profile"].format(profile_type = profile_dict[type]) + "\n" + warning_message, quick_reply = QuickReply(items = [cancel_quick_reply_button]))
            ]
        )
    return 0