import models
from . import get_my_invitation
from services import line_bot_api, text_dict
from linebot.models import PostbackEvent, TextSendMessage

def accept_invitation(event: PostbackEvent, invitorID: str, invitor_upload_time: str, invitedID: str, invited_upload_time):
    
    models.exchange_book.accept_invitation(invitorID, invitor_upload_time, invitedID, invited_upload_time)
    return get_my_invitation.get_my_invitation(event, event.source.user_id)