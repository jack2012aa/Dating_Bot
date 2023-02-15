import boto3
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
        s3 = boto3.client("s3", aws_access_key_id = config["aws_access_key_id"], aws_secret_access_key = config["aws_secret_access_key"])
        url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": photo_dir})
        line_bot_api.reply_message(event.reply_token,
            [
            ImageSendMessage(original_content_url = url, preview_image_url = url),
            TextSendMessage(text = string, quick_reply = QuickReply(quick_reply_buttons))
            ]
        )
    return 0