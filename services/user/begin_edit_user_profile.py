from services import line_bot_api, text_dict, cancel_quick_reply_button
from linebot.models import Event, TextSendMessage, QuickReply, QuickReplyButton, PostbackAction

def begin_edit_user_profile(event: Event):
    '''Show quick replys of editable profile'''
    quick_reply = QuickReply(
                items = [
                    QuickReplyButton(action = PostbackAction(label = "line id", data = "action=edit_profile&type=lineID")),
                    QuickReplyButton(action = PostbackAction(label = "性別", data = "action=edit_profile&type=gender")),
                    QuickReplyButton(action = PostbackAction(label = "希望配對性別", data = "action=edit_profile&type=expect_gender")),
                    QuickReplyButton(action = PostbackAction(label = "出生年份", data = "action=edit_profile&type=birth_year")),
                    QuickReplyButton(action = PostbackAction(label = "學校信箱", data = "action=edit_profile&type=email")),
                    cancel_quick_reply_button
                    ])
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["How to edit profile"], quick_reply = quick_reply))
    return 0    