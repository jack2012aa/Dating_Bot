from flask import Flask, request, abort, send_file
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, ImageMessage,
 TextSendMessage, FollowEvent, CarouselTemplate,CarouselColumn, PostbackTemplateAction, TemplateSendMessage)
import json
import pymysql
from expiringdict import ExpiringDict
from datetime import datetime

app = Flask(__name__)

with open("setting.json") as json_file:
    config = json.load(json_file)

line_bot_api = LineBotApi(config["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(config["CHANNEL_SECRET"])

database = pymysql.connect(
    host = config["DATABASE_HOST"],
    user = config["USER"],
    password = config["PASSWORD"],
    database = config["DATABASE"]
)

uploading_state = ExpiringDict(max_len=300, max_age_seconds=300)

@app.route("/bot", methods=["POST"])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text = True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature")
        abort(400)
    
    return "OK"

@app.route("/images", methods=["GET"])
def get_image():
    file_name = request.args.get("file_name")
    print(file_name)
    return send_file(f"static/{file_name}", mimetype = "image/jpeg")

@handler.add(MessageEvent, message = TextMessage)
def handle_message(event):

    cursor = database.cursor()
    userID = str(event.source.user_id)

    if uploading_state.get(userID) == 0:
        cursor.execute(f"INSERT INTO books (userID, book_name) VALUES ('{userID}', '{str(event.message.text)}');")
        database.commit()
        cursor.close()
        uploading_state[userID] += 1
        return line_bot_api.reply_message(event.reply_token, [TextSendMessage(text = f"書名為: 「{event.message.text}」"), 
        TextSendMessage(text = "請輸入簡介")])

    elif uploading_state.get(userID) == 1:
        cursor.execute(f"UPDATE books SET description = '{event.message.text}' WHERE userID = '{userID}' and exchanged = 'F'")
        database.commit()
        cursor.close()
        uploading_state[userID] += 1
        return line_bot_api.reply_message(event.reply_token, [TextSendMessage(text = f"簡介為: 「{event.message.text}」"), 
        TextSendMessage(text = "請上傳書籍封面")])

    elif event.message.text == "我想上傳新書":
        
        cursor.execute(f"select * from books where userID = '{userID}' and exchanged = 'F'")
        have_book = len(cursor.fetchall()) != 0
        cursor.close()

        if have_book:
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "之前的書還沒有被借出去喔"))

        elif uploading_state.get(userID) == None:
            uploading_state[userID] = 0
            return line_bot_api.reply_message(event.reply_token, [TextSendMessage(text = "請依照順序輸入以下資訊："),
            TextSendMessage(text = "請輸入書名")])

    elif event.message.text == "我想找到適合我的書":
        url = 'https://d3c5-59-104-139-89.jp.ngrok.io/images?file_name='
        cursor.execute("SELECT * FROM books WHERE exchanged = 'F';")
        books = []
        book_introes = cursor.fetchall()
        for i in range(min(9, len(book_introes))):
            book = CarouselColumn(thumbnail_image_url = url + book_introes[i][3], title = book_introes[i][1], text = book_introes[i][2], 
             actions = [PostbackTemplateAction(label = "更多資訊", data = f"action=find_book_intro&userID={book_introes[i][0]}")],
             )
            books.append(book)
        cursor.close()
        
        return line_bot_api.reply_message(event.reply_token, TemplateSendMessage(alt_text = "請於手機端查看", template = CarouselTemplate(columns = books)))


@handler.add(MessageEvent, message = ImageMessage)
def handle_image(event: MessageEvent):

    cursor = database.cursor()
    userID = str(event.source.user_id)
    if uploading_state.get(userID) == 2:
        photo = line_bot_api.get_message_content(event.message.id)
        file_name = datetime.timestamp(datetime.now())
        with open(f"./static/{file_name}.jpeg", 'wb') as f:
            for chunk in photo.iter_content():
                f.write(chunk)
        cursor.execute(f"UPDATE books SET photo_route = '{file_name}.jpeg' WHERE userID = '{userID}' and exchanged = 'F'")
        database.commit()
        cursor.close()
        uploading_state.pop(userID)
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "書籍上架完畢"))

    else:
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "若要上架書籍請使用下方按鈕"))


@handler.add(FollowEvent)
def handle_new_follower(event):

    cursor = database.cursor()
    cursor.execute(f"INSERT INTO friends (userID, lineID) VALUES ('{str(event.source.user_id)}', 'Empty');")
    database.commit()
    cursor.close()
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "歡迎使用本服務～\n功能還在架設中請見諒"))

if __name__ == "__main__":
    app.run()