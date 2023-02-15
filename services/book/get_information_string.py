import models
from flask import current_app
from datetime import datetime

def get_information_string(userID: str, editting: bool, upload_time: str = None):
    '''
    Return book's information and photo name [string, photo]
    :param bool editting: If true, search in table 'editting_books'.
    :param str upload_time: If editting = False, upload_time must be specified.
    '''

    if editting and models.book.has_editting_book(userID):
        info = list(map(lambda x: "尚未填寫" if x == None else x, models.book.get_editting_book_information(userID, all = True)))
        tags = models.book.get_editting_tags(userID)
        if tags[0] == None:
            tags_string = "尚未填寫"
        else:
            tags_string = " ".join(tags)
        string = f"書名：{info[1]}\n分類：{info[4]}\n標籤：{tags_string}\n心得：{info[2]}"
        current_app.logger.debug(f"[{datetime.now()}] Call: get_information_string({userID}, {editting}), info: {info}, tags: {tags}")
        return [string, info[3]]

    elif not editting:
        info = models.book.get_book_information(userID, upload_time, all = True)
        tags = models.book.get_book_tags(userID, upload_time)
        if tags[0] == None:
            tags_string = "尚未填寫"
        else:
            tags_string = " ".join(tags)
        string = f"書名：{info[0]}\n分類：{info[3]}\n標籤：{tags_string}\n心得：{info[1]}"
        current_app.logger.debug(f"[{datetime.now()}] Call: get_information_string({userID}, {editting}), info: {info}, tags: {tags}")
        return [string, info[2]]
        
    current_app.logger.debug(f"[{datetime.now()}] Call: get_information_string({userID}, {editting})")
    return None