import models
from services import text_dict, line_bot_api
from linebot.models import PostbackEvent, QuickReply, QuickReplyButton, PostbackAction, TextSendMessage

def begin_choose_tags_or_categories(event: PostbackEvent, type: str):
    '''Show choosable tags/categories'''

    if type == "categories":
        choices = models.book.get_all_categories()
    elif type == "tags":
        choices = models.book.get_all_tags()

    quick_reply_buttons = []
    for choice in choices:
        quick_reply_buttons.append(QuickReplyButton(action = PostbackAction(label = choice, display_text = choice,data = "action=find_book&type=choose_"+type+"&"+type+"="+choice)))
    quick_reply_buttons.append(QuickReplyButton(action = PostbackAction(label = "全選", display_text = "全選",data = "action=find_book&type=choose_"+type+"&"+type+"=all")))
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Choose search fields"], quick_reply = QuickReply(items = quick_reply_buttons)))
    return 0