from . import get_information_string
from services import line_bot_api
from linebot.models import PostbackEvent, TextSendMessage
from flask import current_app
from datetime import datetime

def show_book_detail(event: PostbackEvent, userID: str, upload_time: str):
    """Show the book detail's to user."""

    text = get_information_string.get_information_string(userID, False, upload_time)[0]
    line_bot_api.reply_message(event.reply_token, [TextSendMessage(text = text)])
    current_app.logger.info(f"[{datetime.now()}] Action: find_book, Type: show_book_detail, ID: {event.source.user_id}, book: [{userID},{upload_time}]")
    return 0