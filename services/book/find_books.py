import models
from . import get_book_carousels
from services import cache, line_bot_api, text_dict
from linebot.models import PostbackEvent, TextSendMessage, TemplateSendMessage, QuickReply, QuickReplyButton, PostbackAction
from flask import current_app
from datetime import datetime

def find_books(event: PostbackEvent):
    '''Find books fulfill requirements in cache.'''

    state = cache.get(event.source.user_id, None)
    if state == None or state[0] != "find_book" or (len(state[1]) == 0 and len(state[2]) == 0):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Empty search fields"]))
        return 0
    
    categories = cache.get(event.source.user_id)[2]
    tags = cache.get(event.source.user_id)[3]
    gender = models.user.get_user_profiles(event.source.user_id, ["expect_gender"])[0]
    expect_gender = models.user.get_user_profiles(event.source.user_id, ["gender"])[0]
    books = models.book.get_books(event.source.user_id, gender, expect_gender, categories, tags)
    if books == None:
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["No such books"]))

    for book in books:
        book.append(models.book.get_book_tags(book[3], book[4]))

    result_length = len(books)
    book_carousel, books = get_book_carousels.get_book_carousels(books, True)
    cache[event.source.user_id] = ["find_book", "next_page", books]

    current_app.logger.info(f"[{datetime.now()}] Action: find_books, Type: find, ID: {event.source.user_id}, Search on: {categories} {tags}, Books: {books}")
    try:
        if len(books) == 0:
            cache.pop(event.source.user_id, None)
            return line_bot_api.reply_message(event.reply_token, [
                TextSendMessage(text = text_dict["Search result"].format(num = result_length)),
                TemplateSendMessage(alt_text = text_dict["See on the phone"], template = book_carousel)
            ])
        else:
            return line_bot_api.reply_message(event.reply_token, [
                TextSendMessage(text = text_dict["Search result"].format(num = result_length)),
                TemplateSendMessage(alt_text = text_dict["See on the phone"], template = book_carousel,
                quick_reply = QuickReply(items = [QuickReplyButton(action = PostbackAction(label = "下一頁", display_text = "下一頁", data = "action=find_book&type=next_page"))]))
            ])
    except Exception as err:
        current_app.logger.error(f"[{datetime.now()}] Action error. Call: find_books({event}), {type(err)}, {str(err.args)}")