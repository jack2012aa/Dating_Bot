import models
from services import line_bot_api, text_dict, cancel_quick_reply_button, config, cache
from linebot.models import PostbackEvent, TextSendMessage, QuickReply, ImageSendMessage

def begin_edit_photo(event: PostbackEvent):
    '''Return present photo.'''

    photo_dir = models.book.get_editting_book_information(event.source.user_id, ["photo"])[0]
    if photo_dir == None:
        line_bot_api.reply_message(event.reply_token, 
            [
            TextSendMessage(text = text_dict["Null information"].format(field = "照片")),
            TextSendMessage(text = text_dict["Edit information"].format(field = "照片"), quick_reply = QuickReply(items = [cancel_quick_reply_button]))
            ]
        )
    else:
        line_bot_api.reply_message(event.reply_token,
            [
            ImageSendMessage(original_content_url = config["url"] + "/images?file_name=" + photo_dir, preview_image_url = config["url"] + "/images?file_name=" + photo_dir),
            TextSendMessage(text = "以上為目前書籍照片" + text_dict["Edit information"].format(field = "照片"), quick_reply = QuickReply(items = [cancel_quick_reply_button]))
            ]
        )
    
    cache[event.source.user_id] = ["upload_book", "photo"]
    return 0