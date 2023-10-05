import models, boto3
from . import get_information_string, show_invitations
from services import line_bot_api, text_dict, config
from linebot.models import PostbackEvent, TextSendMessage, ImageSendMessage
from flask import current_app
from datetime import datetime

def get_my_invitation(event: PostbackEvent, userID: str):
    '''Get all user's invitation request. If already have a accepted request, reply invitor's book info and line id'''

    if models.exchange_book.has_accept_invitation(event.source.user_id):
        userID, upload_time, lineID = models.exchange_book.get_exchanged_book_and_lineID(event.source.user_id)
        info, photo_dir = get_information_string.get_information_string(userID, False, upload_time)
        s3 = boto3.client("s3", aws_access_key_id = config["aws_access_key_id"], aws_secret_access_key = config["aws_secret_access_key"])
        url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": photo_dir})
        
        return line_bot_api.reply_message(event.reply_token, [
            ImageSendMessage(url, url),
            TextSendMessage(info),
            TextSendMessage(text_dict["Lucky"].format(lineID = lineID))
        ])
    else:
        return show_invitations.show_invitations(event)