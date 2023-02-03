from services import cancel_quick_reply_button, line_bot_api, text_dict
from linebot.models import PostbackEvent, QuickReply, QuickReplyButton, PostbackAction,TextSendMessage

def begin_edit_book(event: PostbackEvent):
    '''Show quick replys of editable book information'''

    quick_reply = QuickReply(
        items = [
            QuickReplyButton(action = PostbackAction(label = "書名", data = "action=upload_book&type=name")),
            QuickReplyButton(action = PostbackAction(label = "心得", data = "action=upload_book&type=summary")),
            QuickReplyButton(action = PostbackAction(label = "照片", data = "action=upload_book&type=photo")),
            QuickReplyButton(action = PostbackAction(label = "交換方式", data = "action=upload_book&type=exchange_method")),
            QuickReplyButton(action = PostbackAction(label = "分類", data = "action=upload_book&type=category")),
            QuickReplyButton(action = PostbackAction(label = "標籤", data = "action=upload_book&type=tag")),
            QuickReplyButton(action = PostbackAction(label = "確認上傳", data = "action=upload_book&type=begin_upload")),
            cancel_quick_reply_button
        ]
    )
    return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Upload book"], quick_reply = quick_reply))
