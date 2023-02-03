import models
from services import cache, line_bot_api, text_dict, config
from linebot.models import PostbackEvent, TextSendMessage, CarouselColumn, PostbackTemplateAction, TemplateSendMessage, CarouselTemplate, QuickReply, QuickReplyButton, PostbackAction

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
    cache[event.source.user_id] = ["find_book", "next_page", books]
    books_carouel = []
    result_length = len(books)
    for i in range(min(10, len(books))):
        book = books.pop(0)
        tags_string = " ".join(models.book.get_book_tags(book[3], book[2]))
        books_carouel.append(
            CarouselColumn(
                thumbnail_image_url = config["url"] + "/images?file_name=" + book[1],
                title = book[0],
                text = "分類：" + models.book.get_book_information(book[3], book[2], ["category"])[0] + "\n標籤：" + tags_string,
                actions = [PostbackTemplateAction(label = text_dict["More"], data = f"action=show_book_detail&type={book[3]}+{book[2]}")]
            )
        )

    if len(books) == 0:
        return line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text = text_dict["Search result"].format(num = result_length)),
            TemplateSendMessage(alt_text = text_dict["See on the phone"], template = CarouselTemplate(columns = books_carouel))
        ])
    else:
        return line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text = text_dict["Search result"].format(num = result_length)),
            TemplateSendMessage(alt_text = text_dict["See on the phone"], template = CarouselTemplate(columns = books_carouel),
            quick_reply = QuickReply(items = [QuickReplyButton(action = PostbackAction(label = "下一頁", display_text = "下一頁", data = "action=find_book&type=next_page"))]))
        ])