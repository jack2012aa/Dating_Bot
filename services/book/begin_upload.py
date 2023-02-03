from .get_information_string import get_information_string
from services import cancel_quick_reply_button, line_bot_api, config
from linebot.models import PostbackEvent, QuickReply, QuickReplyButton, PostbackAction, TextSendMessage, ImageSendMessage

def begin_upload(event: PostbackEvent):
    '''Show present editting book's information and give checking quick reply'''

    quick_reply_buttons = [
        QuickReplyButton(action = PostbackAction(label = "確認", display_text = "確認上傳", data = "action=upload_book&type=upload")),
        cancel_quick_reply_button
    ]
    string, photo_dir = get_information_string(event.source.user_id, True)
    
    if photo_dir == None:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = string, quick_reply = QuickReply(items = quick_reply_buttons)))
    else:
        line_bot_api.reply_message(event.reply_token,
            [
            ImageSendMessage(original_content_url = config["url"] + "/images?file_name=" + photo_dir, preview_image_url = config["url"] + "/images?file_name=" + photo_dir),
            TextSendMessage(text = string, quick_reply = QuickReply(quick_reply_buttons))
            ]
        )
    return 0