import models
from . import get_information_string, show_invitations
from services import line_bot_api, text_dict, config
from linebot.models import PostbackEvent, TextSendMessage, ImageSendMessage
from flask import current_app
from datetime import datetime

def get_my_invitation(event: PostbackEvent, userID: str):
    '''Get all user's invitation request. If already have a accepted request, reply invitor's book info and line id'''

    if models.book.has_accept_invitation(event.source.user_id):
        userID, upload_time, lineID = models.book.get_exchanged_book_and_lineID(event.source.user_id)
        info, photo = get_information_string.get_information_string(userID, False, upload_time)
        url = config["url"] + "/images?file_name=" + photo
        current_app.logger.info(f"[{datetime.now()}] Action: invite, Type: my_invitation, ID: {event.source.user_id}, accept: True")
        return line_bot_api.reply_message(event.reply_token, [
            ImageSendMessage(url, url),
            TextSendMessage(info),
            TextSendMessage(text_dict["Lucky"].format(lineID = lineID))
        ])
    else:
        return show_invitations.show_invitations(event)