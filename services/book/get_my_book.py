import models, boto3
from . import get_information_string
from services import line_bot_api, config, cancel_quick_reply_button
from linebot.models import PostbackEvent, TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, PostbackAction

def get_my_book(event: PostbackEvent):
    '''Reply content of usesr's book and delete button'''

    book = models.book.get_newest_book(event.source.user_id)
    text, photo = get_information_string.get_information_string(book[0], False, book[1])
    s3 = boto3.client("s3", aws_access_key_id = config["aws_access_key_id"], aws_secret_access_key = config["aws_secret_access_key"])
    url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": photo})
    line_bot_api.reply_message(event.reply_token, [
        ImageSendMessage(url, url),
        TextSendMessage(text = text, quick_reply = QuickReply(items = [
            QuickReplyButton(action = PostbackAction(label = "刪除", data = f"action=delete&type=delete&data={book[0]}+{book[1]}", display_text = "刪除這本書")),
            cancel_quick_reply_button
        ]))
    ])
    return 0