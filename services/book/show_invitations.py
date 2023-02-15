import models
from . import get_book_carousels
from services import line_bot_api, text_dict, cache
from linebot.models import PostbackEvent, TextSendMessage, TemplateSendMessage, QuickReply, QuickReplyButton, PostbackAction

def show_invitations(event: PostbackEvent, next_page: bool = False):
    '''
    Reply invitor carousels
    :param bool next_page: If False, reply all invitors.
    '''

    if not next_page:
        invitors = models.book.get_all_invitations(event.source.user_id)
        if invitors == None:
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["No invite"]))
        else:
            books = []
            for invitor in invitors:
                book = models.book.get_book_information(invitor[0], invitor[1], ["photo", "name", "category", "userID", "upload_time"])
                tags = models.book.get_book_tags(invitor[0], invitor[1])
                book.append(tags)
                books.append(book)
    else:
        books = cache.get(event.source.user_id, None)

    books_carousel, books = get_book_carousels.get_book_carousels(books, False)
    cache[event.source.user_id] = ["invite", "next_page", books]
    if len(books) == 0:
        cache.pop(event.source.user_id)
        return line_bot_api.reply_message(event.reply_token, TemplateSendMessage(alt_text = text_dict["See on the phone"], template = books_carousel))
    else:
        return line_bot_api.reply_message(event.reply_token, [
            TemplateSendMessage(alt_text = text_dict["See on the phone"], template = books_carousel,
            quick_reply = QuickReply(items = [QuickReplyButton(action = PostbackAction(label = "下一頁", display_text = "下一頁", data = "action=invite&type=next_page"))]))
        ])