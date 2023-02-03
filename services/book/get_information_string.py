import models

def get_information_string(userID: str, editting: bool):
    '''Get all user book's information and photo name'''

    if editting and models.book.has_editting_book(userID):
        id, name, summary, photo, exchange_method, category = map(lambda x: "尚未填寫" if x == None else x, models.book.get_editting_book_information(userID, all = True))
        tags = models.book.get_editting_tags(userID)
        if tags[0] == None:
            tags_string = "尚未填寫"
        else:
            tags_string = " ".join(tags)
        string = f"書名：{name}\n心得：{summary}\n分類：{category}\n標籤：{tags_string}\n交換方式：{exchange_method}"
        return [string, photo]