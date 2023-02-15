from . import get_book_carousels
from services import cache, line_bot_api, text_dict
from linebot.models import PostbackEvent, TemplateSendMessage, QuickReply, QuickReplyButton, PostbackAction
from flask import current_app
from datetime import datetime

def next_search(event: PostbackEvent):
    '''Return next 10 books'''
    
    books = cache.get(event.source.user_id)[2]
    books_carousel, books = get_book_carousels.get_book_carousels(books, True)
    cache[event.source.user_id] = ["find_book", "next_page", books]

    try:       
        if len(books) == 0:
            cache.pop(event.source.user_id)
            return line_bot_api.reply_message(event.reply_token, [
                TemplateSendMessage(alt_text = text_dict["See on the phone"], template = books_carousel)
            ])
        else:
            return line_bot_api.reply_message(event.reply_token, [
                TemplateSendMessage(alt_text = text_dict["See on the phone"], template = books_carousel,
                quick_reply = QuickReply(items = [QuickReplyButton(action = PostbackAction(label = "下一頁", data = "action=find_book&type=next_page"))]))
            ])
    except Exception as err:
        current_app.logger.error(f"[{datetime.now()}] Action error. Call: find_books({event}), {type(err)}, {str(err.args)}")