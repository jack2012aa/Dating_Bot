import models
from . import get_book_carousels
from services import line_bot_api, text_dict, cache
from linebot.models import PostbackEvent, TextSendMessage, TemplateSendMessage

def get_random_book(event: PostbackEvent):
    '''Reply a random book'''

    cache.pop(event.source.user_id,None)
    gender, expect_gender = models.user.get_user_profiles(event.source.user_id, ["gender", "expect_gender"])
    book = models.book.get_random_book(event.source.user_id, expect_gender, gender)
    if book == None:
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["No such books"]))
    book.append(models.book.get_book_tags(book[3], book[4]))
    book_carousel, books = get_book_carousels.get_book_carousels([book], True)
    return line_bot_api.reply_message(event.reply_token, TemplateSendMessage(alt_text = text_dict["See on the phone"], template = book_carousel))