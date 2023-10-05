import models
import boto3
from io import BytesIO
from services import line_bot_api, text_dict,config
from datetime import datetime
from linebot.models import MessageEvent, TextSendMessage

def upload_photo(event: MessageEvent):
    '''Get uploaded photo from Line, save it into static, delete the old one and update the database.'''
    
    s3 = boto3.client("s3", aws_access_key_id = config["aws_access_key_id"], aws_secret_access_key = config["aws_secret_access_key"])

    photo_dir = models.exchange_book.get_editting_book_information(event.source.user_id, ["photo"])[0]
    if photo_dir != None:
        s3.delete_object(Bucket = "linedatingapp", Key = photo_dir)

    photo = line_bot_api.get_message_content(event.message.id)
    photo = BytesIO(photo.content)
    photo_dir = str(datetime.timestamp(datetime.now())) + ".jpeg"
    s3.upload_fileobj(photo, "linedatingapp", photo_dir)
    photo.close()
    models.exchange_book.insert_or_update_editting_book(event.source.user_id, "photo", photo_dir)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Upload photo successfully"]))

    return 0