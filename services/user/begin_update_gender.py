import models
from services import cancel_quick_reply_button, line_bot_api, text_dict
from linebot.models import Event, QuickReply, QuickReplyButton, PostbackAction,TextSendMessage

def begin_update_gender(event: Event, type: str):
    '''Show present gender profile and give quick reply to choose gender'''

    quick_reply = QuickReply(
                items = [
                    QuickReplyButton(action = PostbackAction(label = "男", display_text = "男" ,data = f"action=edit_profile&type=choose_gender&field={type}&value=男")),
                    QuickReplyButton(action = PostbackAction(label = "女", display_text = "女",data = f"action=edit_profile&type=choose_gender&field={type}&value=女")),
                    QuickReplyButton(action = PostbackAction(label = "非二元", display_text = "非二元",data = f"action=edit_profile&type=choose_gender&field={type}&value=非二元")),
                    cancel_quick_reply_button
                ]
            )
    present_gender = models.user.get_user_profiles(event.source.user_id, [type])[0]
    profile_dict = {"gender":"性別","expect_gender":"希望配對性別"}
    if present_gender == None:
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text = text_dict["Null profile"].format(profile_type = profile_dict[type])),
                TextSendMessage(text = text_dict["Choose gender"], quick_reply = quick_reply)
            ]
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text = text_dict["Present profile"].format(profile_type = profile_dict[type], profile = present_gender)),
                TextSendMessage(text = text_dict["Choose gender"], quick_reply = quick_reply)
            ]
        )
    return 0