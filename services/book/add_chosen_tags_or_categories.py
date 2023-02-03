import models
from services import cache, line_bot_api, text_dict
from linebot.models import PostbackEvent, TextSendMessage

def add_chosen_tags_or_categories(event: PostbackEvent, type: str, value: str):
    '''Add chosen tag/category into cache'''

    state = cache.get(event.source.user_id, None)
    if state == None or state[0] != "find_book" or state[1] != "fill_in":
        cache[event.source.user_id] = ["find_book","fill_in",[],[]]

    if value != "all":
        if type == "choose_categories":
            cache.get(event.source.user_id)[2] = choose(cache.get(event.source.user_id)[2], value)
        else:
            cache.get(event.source.user_id)[3] = choose(cache.get(event.source.user_id)[3], value)
    else:
        if type == "choose_categories":
            for category in models.book.get_all_categories():
                cache.get(event.source.user_id)[2] = choose(cache.get(event.source.user_id)[2], category)
        else:
            for tag in models.book.get_all_tags():
                cache.get(event.source.user_id)[3] = choose(cache.get(event.source.user_id)[3], tag)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Chosen"]))
    return 0

def choose(arr: list, value: str):
    '''If value is in the array, remove it. Else insert it'''

    if value in arr:
        arr.remove(value)
    else:
        arr.append(value)
    return arr