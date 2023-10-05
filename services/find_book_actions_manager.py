'''Define APIs relate to find book. API will contact with model, check user's information and return an array of line reply messages or/and whether the input is valid.'''
import boto3, models
from models.exchange_book import Book
from . import config
from linebot.models import TextSendMessage, CarouselColumn, CarouselTemplate, PostbackTemplateAction, ImageSendMessage, QuickReply, QuickReplyButton, PostbackAction, TemplateSendMessage

#Define types to find book
MY_BOOK = "my_book"
CHECK_DELETE = "check_delete"
DELETE = "delete"
BEGIN_FIND_BOOK = "begin"
BEGIN_CHOOSE_TAGS = "begin_choose_tags"
BEGIN_CHOOSE_CATEGORIES = "begin_choose_categories"
CHOOSE_CATEGORY = "choose_category"
CHOOSE_TAG = "choose_tag"
FIND = "find"
RANDOM_FIND = "random_find"
NEXT_PAGE = "next_page"
SHOW_BOOK_DETAIL = "show_book_detail"
FINISH = "finish"

#Define text
text_dict = {

    #Carousel
    "More": "更多資訊",
    "Send invitation": "送出交換邀請",

    #Error
    "Unknown error": "發生未知錯誤，請再試一次",
    "Have accepted invitation": "已經配對成功咯，快去配對邀請查看",
    "No book": "尚未上傳書籍",

    #Success
    "Delete successfully": "書籍刪除成功",
    "Set success": "設定成功",
    "Choose success": "成功添加{value}",
    "Move success": "成功移除{value}",

    #Check
    "Delete?": "是否刪除書籍？",

    #Chosen
    "Haven't chosen": "尚未設定搜尋條件",
    "Chosen categories": "已選擇分類：{categories}",
    "Chosen tags": "已選擇標籤：{tags}",

    #Teaching
    "How to search": "點選分類及標籤，選擇想要找的種類後再按搜尋\n或選擇隨機搜尋將無視條件搜尋一本書",

    #Find books
    "No such books": "沒有找到符合的書籍喔，請用其他條件搜尋或是之後再看看吧",
    "Number of books": "共搜尋到{num}筆結果",
    "See on the phone": "請於手機端觀看",


}

book_dict = {} 
'''A dict to save cache books'''

search_field = {}
'''A dict to save user's search field'''


cancel_quick_reply_button = QuickReplyButton(action = PostbackAction(label = "取消", display_text = "取消動作",data = "action=cancel&type=none"))
finish_quick_reply_button = QuickReplyButton(action = PostbackAction(label = "完成", display_text = "完成",data = f"action=find_book&type={FINISH}"))


def is_valid(userID: str):
    '''
    Check whether the user has an uploaded and not blocked book, and do he have an accepted invitation.
    :param str userID: line user id
    :return list of messages and bool indicates whether the user is valid for find book
    '''

    if models.exchange_book.has_accept_invitation(userID):
        return [TextSendMessage(text_dict["Have accepted invitation"])], False
    
    if not models.exchange_book.has_book(userID, True):
        return [TextSendMessage(text_dict["No book"])], False

    return [], True

def get_info_text(book: Book):
    '''
    Handle info in book. Rearrange them into text message.
    :param list book: Book object
    '''
    
    return f"書名：{book.NAME}\n分類：{book.CATEGORY}\n標籤：{book.get_tags_string()}\n心得：{book.SUMMARY}"
        
def get_my_book(userID: str):
    '''
    Reply content of user's book and a delete button.
    :param str userID: line user id
    '''

    #Get book
    book: Book = models.exchange_book.get_newest_book(userID)
    
    if book == None:
        return [TextSendMessage(text_dict["Unknown error"])]

    book_dict[book.serialize()] = book
    url = book.get_photo_url()
    return [
        ImageSendMessage(url, url),
        TextSendMessage(get_info_text(book), quick_reply = QuickReply([QuickReplyButton(action = PostbackAction(label = "刪除", data = f"action=find_book&type={CHECK_DELETE}&book={book.serialize()}", display_text = "刪除這本書")), cancel_quick_reply_button]))
    ]

def check_delete(book_key: str):
    '''
    Show a check message to delete the book.
    :param str book_index: a key in dict
    '''

    return [TextSendMessage(text_dict["Delete?"], quick_reply = QuickReply([QuickReplyButton(action = PostbackAction(label = "確認", data = f"action=find_book&type={DELETE}&data={book_key}", display_text = "刪除這本書")), cancel_quick_reply_button]))]

def delete(book_key: str):
    '''
    Delete book.
    :param str book_index: a key in dict
    '''

    book: Book = book_dict.pop(book_key, None)
    if book == None:
        return [TextSendMessage(text_dict["Unknown error"])], False
    if models.exchange_book.delete_book(book.USERID, book.UPLOAD_TIME):
        return [TextSendMessage(text_dict["Delete successfully"])], True
    return [TextSendMessage(text_dict["Unknown error"])], False

def begin_find_book(userID: str, chosen_categories: list = None, chosen_tags: list = None):
    '''
    Let user select search fields.
    :param str userID: line user id
    :param list chosen_categories: chosen categories to search. If nothing chosen use None
    :param list chosen_tags: chosen tags to search. If nothing chosen use None
    '''

    search_fields = "搜尋條件：\n"
    if chosen_categories == None and chosen_tags == None:
        search_fields = text_dict["Haven't chosen"]
    if chosen_categories != None:
        search_fields = search_fields + "分類：" + "、".join(chosen_categories) + "\n"
    if chosen_tags != None:
        search_fields = search_fields + "標籤：" + "、".join(chosen_tags) + ""

    quick_replies = QuickReply([
        QuickReplyButton(action = PostbackAction(label = "分類", display_text = "選擇分類", data = f"action=find_book&type={BEGIN_CHOOSE_CATEGORIES}")),
        QuickReplyButton(action = PostbackAction(label = "標籤", display_text = "選擇標籤", data = f"action=find_book&type={BEGIN_CHOOSE_TAGS}")),
        QuickReplyButton(action = PostbackAction(label = "搜尋", display_text = "搜尋書籍", data = f"action=find_book&type={FIND}")),
        QuickReplyButton(action = PostbackAction(label = "隨機", display_text = "隨機搜尋", data = f"action=find_book&type={RANDOM_FIND}")),
        cancel_quick_reply_button
    ])

    return [TextSendMessage(text_dict["How to search"]), TextSendMessage(search_fields, quick_reply = quick_replies)]

def begin_choose_categories(userID: str):
    '''
    Let user selects search categories.
    :param str userID: line user id
    '''
    
    fields = search_field.get(userID, None)
    if fields == None:
        search_field[userID] = {"chosen_categories": [], "chosen_tags": []}
        chosen_categories = [None]
    else:
        chosen_categories = fields.get("chosen_categories")

    categories = models.exchange_book.get_all_categories()
    s3 = boto3.client("s3", aws_access_key_id = config["aws_access_key_id"], aws_secret_access_key = config["aws_secret_access_key"])
    red_url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": "red.png"})
    green_url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": "green.png"})
    quick_replies = []
    for category in categories:
        if category in chosen_categories:
            quick_replies.append(QuickReplyButton(red_url, PostbackAction(category, f"action=find_book&type={CHOOSE_CATEGORY}&value={category}", category)))
        else:
            quick_replies.append(QuickReplyButton(green_url, PostbackAction(category, f"action=find_book&type={CHOOSE_CATEGORY}&value={category}", category)))
    quick_replies.append(QuickReplyButton(action = PostbackAction(label = "全選", display_text = "全選",data = f"action=find_book&type={CHOOSE_CATEGORY}&value=all")))
    quick_replies.append(finish_quick_reply_button)
    quick_replies = QuickReply(quick_replies)
    if chosen_categories[0] != None:
        text = text_dict["Chosen categories"].format(categories =  "、".join(chosen_categories))
    else:
        text = text_dict["Haven't chosen"]
    return [TextSendMessage(text, quick_reply= quick_replies)]

def begin_choose_tags(userID: str):
    '''
    Let user selects search tags.
    :param str userID: line user id
    '''

    fields = search_field.get(userID, None)
    if fields == None:
        search_field[userID] = {"chosen_categories": [], "chosen_tags": []}
        chosen_tags = [None]
    else:
        chosen_tags = fields.get("chosen_tags")

    tags = models.exchange_book.get_all_tags()
    s3 = boto3.client("s3", aws_access_key_id = config["aws_access_key_id"], aws_secret_access_key = config["aws_secret_access_key"])
    red_url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": "red.png"})
    green_url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": "green.png"})
    quick_replies = []
    for tag in tags:
        if tag in chosen_tags:
            quick_replies.append(QuickReplyButton(red_url, PostbackAction(tag, f"action=find_book&type={CHOOSE_TAG}&value={tag}", tag)))
        else:
            quick_replies.append(QuickReplyButton(green_url, PostbackAction(tag, f"action=find_book&type={CHOOSE_TAG}&value={tag}", tag)))
    quick_replies.append(QuickReplyButton(action = PostbackAction(label = "全選", display_text = "全選",data = f"action=find_book&type={CHOOSE_TAG}&value=all")))
    quick_replies = QuickReply(quick_replies)
    if chosen_tags[0] != None:
        text = text_dict["Chosen tags"].format(tags = "、".join(chosen_tags))
    else:
        text = text_dict["Haven't chosen"]
    return [TextSendMessage(text, quick_reply= quick_replies)]

def choose_category(userID: str, value: str):
    '''
    Append or remove category from search fields.
    :param str userID: line user id
    :param str value: chosen category
    '''

    fields = search_field.get(userID, None)
    if fields == None:
        search_field[userID] = {"chosen_categories": [], "chosen_tags": []}
        chosen_categories = [None]
    else:
        chosen_categories = fields.get("chosen_categories")
    
    if value == "all":
        categories = models.exchange_book.get_all_categories()
        for category in categories:
            if category in chosen_categories:
                chosen_categories.remove(category)
            else:
                chosen_categories.append(category)
        return [TextSendMessage(text_dict["Set success"])]
    
    if value in chosen_categories:
        chosen_categories.remove(value)
        return [TextSendMessage(text_dict["Move success"].format(value = value))]
    else:
        chosen_categories.append(value)
        return [TextSendMessage(text_dict["Choose success"].format(value = value))]

def choose_tag(userID: str, value: str):
    '''
    Append or remove tag from search fields.
    :param str userID: line user id
    :param str value: chosen tag
    '''

    fields = search_field.get(userID, None)
    if fields == None:
        search_field[userID] = {"chosen_categories": [], "chosen_tags": []}
        chosen_tags = [None]
    else:
        chosen_tags = fields.get("chosen_tags")
    
    if value == "all":
        tags = models.exchange_book.get_all_tags()
        for tag in tags:
            if tag in chosen_tags:
                chosen_tags.remove(tag)
            else:
                chosen_tags.append(tag)
        return [TextSendMessage(text_dict["Set success"])]
    
    if value in chosen_tags:
        chosen_tags.remove(value)
        return [TextSendMessage(text_dict["Move success"].format(value = value))]
    else:
        chosen_tags.append(value)
        return [TextSendMessage(text_dict["Choose success"].format(value = value))]

def get_book_carousels(books: list[Book]):
    '''
    Return a line carousel template containing at most 10 books and remain books.
    :param list books: list of Book objects
    '''

    books_carousel = []
    #Append at most 10 books
    for i in range(min(10, len(books))):
        book: Book = books.pop(0)
        books_carousel.append(
            CarouselColumn(
                thumbnail_image_url = book.get_photo_url,
                title = book[1],
                text = f"分類：{book.CATEGORY}\n標籤：{book.get_tags_string()}",
                actions = [
                    PostbackTemplateAction(label = text_dict["More"], data = f"action=find_book&type={SHOW_BOOK_DETAIL}&book={book.serialize()}", display_text = text_dict["More"]),
                    PostbackTemplateAction(label = text_dict["Send invitation"], data = f"action=invite&type=invite&book={book.serialize()}", display_text = text_dict["Send invitation"])
                    ]
            )
        )

    return CarouselTemplate(columns = books_carousel), books

def find_books(userID: str, chosen_categories: list = None, chosen_tags: list = None):
    '''
    Choose book fulfill search field.
    :param str userID: line user id
    :param list chosen_categories: search fields
    :param list chosen_tags: search fields
    :Return message and remain books
    '''

    gender, expect_gender = models.user.get_user_profiles(userID, ["gender, expect_gender"])
    books = models.exchange_book.find_books(userID, expect_gender, gender, chosen_categories, chosen_tags)
    
    if books == None:
        return [TextSendMessage(text_dict["No such books"])]
    if books == False:
        return [TextSendMessage(text_dict["Unknown error"])]

    result_length = len(books)
    book_carousel, books = get_book_carousels(books, True)
    
    if len(books) == 0:
        return [TextSendMessage(text = text_dict["Number of books"].format(num = result_length)), TemplateSendMessage(alt_text = text_dict["See on the phone"], template = book_carousel)], None
    else:
        return [TextSendMessage(text = text_dict["Number of books"].format(num = result_length)), TemplateSendMessage(alt_text = text_dict["See on the phone"], template = book_carousel, quick_reply = QuickReply(items = [QuickReplyButton(action = PostbackAction(label = "下一頁", display_text = "下一頁", data = f"action=find_book&type={NEXT_PAGE}"))]))], books

def show_book_detail(book: Book):
    '''
    Show books photo, name, category, tags, summary.
    :param Book book: a Book object
    '''
    
    return [ImageSendMessage(book.get_photo_url(), book.get_photo_url()), TextSendMessage(get_info_text(book))]

def next_page(books: list[Book]):
    '''
    Show next 10 books carousels.
    :param list books: list of Book objects
    :Return message and remain books
    '''

    book_carousel, books = get_book_carousels(books, True)
    
    if len(books) == 0:
        return [TemplateSendMessage(alt_text = text_dict["See on the phone"], template = book_carousel)], None
    else:
        return [TemplateSendMessage(alt_text = text_dict["See on the phone"], template = book_carousel, quick_reply = QuickReply(items = [QuickReplyButton(action = PostbackAction(label = "下一頁", display_text = "下一頁", data = f"action=find_book&type={NEXT_PAGE}"))]))], books

def random_find(userID: str):
    '''
    Show a random book.
    :param str userID: line user id
    '''

    gender, expect_gender = models.user.get_user_profiles(userID, ["gender", "expect_gender"])
    book: Book = models.exchange_book.get_random_book(userID, expect_gender, gender)

    if book == None:
        return [TextSendMessage(text_dict["No such books"])]

    book_carousel = get_book_carousels([book])[0]
    return [TemplateSendMessage(alt_text = text_dict["See on the phone"], template = book_carousel)]