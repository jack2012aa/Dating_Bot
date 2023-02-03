import models
from services import cache, config, line_bot_api, text_dict
from linebot.models import PostbackEvent, CarouselColumn, CarouselTemplate, TemplateSendMessage, QuickReply, QuickReplyButton, PostbackAction, PostbackTemplateAction

def next_page(event: PostbackEvent):
    '''Return next 10 books'''
    
    books = cache.get(event.source.user_id)[2]
    books_carouel = []
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
        cache.pop(event.source.user_id)
        return line_bot_api.reply_message(event.reply_token, [
            TemplateSendMessage(alt_text = text_dict["See on the phone"], template = CarouselTemplate(columns = books_carouel))
        ])
    else:
        return line_bot_api.reply_message(event.reply_token, [
            TemplateSendMessage(alt_text = text_dict["See on the phone"], template = CarouselTemplate(columns = books_carouel),
            quick_reply = QuickReply(items = [QuickReplyButton(action = PostbackAction(label = "下一頁", data = "action=find_book&type=next_page"))]))
        ])