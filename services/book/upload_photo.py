import models, os
from services import line_bot_api, text_dict
from datetime import datetime
from linebot.models import MessageEvent, TextSendMessage

def upload_photo(event: MessageEvent):
    '''Get uploaded photo from Line, save it into static, delete the old one and update the database.'''
    
    photo_dir = models.book.get_editting_book_information(event.source.user_id, ["photo"])[0]
    if photo_dir != None:
        os.remove("./static/book/" + photo_dir)

    photo = line_bot_api.get_message_content(event.message.id)
    photo_dir = str(datetime.timestamp(datetime.now())) + ".jpeg"
    with open(f"./static/book/{photo_dir}", 'wb') as f:
        for chunk in photo.iter_content():
            f.write(chunk)
    models.book.insert_or_update_editting_book(event.source.user_id, "photo", photo_dir)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Upload photo successfully"]))

    return 0