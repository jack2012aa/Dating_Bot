from flask import Flask, request, abort, send_file
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, ImageMessage,
 TextSendMessage, FollowEvent, CarouselTemplate,CarouselColumn, PostbackTemplateAction, TemplateSendMessage, PostbackEvent, QuickReply, QuickReplyButton, PostbackAction, MessageAction)
import json
import pymysql
from expiringdict import ExpiringDict
from datetime import datetime
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

app = Flask(__name__)

with open("setting.json") as json_file:
    config = json.load(json_file)

line_bot_api = LineBotApi(config["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(config["CHANNEL_SECRET"])
url = config["url"]

database = pymysql.connect(
    host = config["DATABASE_HOST"],
    user = config["USER"],
    password = config["PASSWORD"],
    database = config["DATABASE"]
)

uploading_state = ExpiringDict(max_len=300, max_age_seconds=300)

text_dict = {
    "Welcome": "歡迎使用本服務～\n若想參加活動，請使用下方功能按鈕更新資料並驗證",
    "How to edit profile": "透過底下按鈕選擇要修改哪項個人資訊，再輸入希望更改的訊息喔\n請在3分鐘內輸入完畢",
    "Edit profile": "請在底下輸入您的{profile_type}",
    "See on the phone": "請於手機端觀看",
    "Update successfully": "已成功更改為 {message}",
    "Present profile": "目前的{profile_type}為 {profile}",
    "Cancel action": "已取消動作",
    "Choose gender": "請選擇以下性別",
    "Input wrong gender": "請輸入\"男\"或\"女\"",
    "Input verifying code": "驗證碼已發送至{email}，請輸入驗證碼",
    "Verified": "已通過驗證",
    "Wrong verifying code": "驗證碼錯誤",
    "Improper email": "此信箱不是台大學校信箱"
}

editting_user = ExpiringDict(100, 180)
verifying_codes = ExpiringDict(100, 180)

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
    '''API getting books photo used for line'''

    file_name = request.args.get("file_name")
    print(file_name)
    return send_file(f"static/{file_name}", mimetype = "image/jpeg")

@handler.add(FollowEvent)
def handle_new_follower(event):
    '''Show welcome messages and insert user into database.'''

    cursor = database.cursor()
    cursor.execute(f"INSERT IGNORE INTO friends (userID) VALUES ('{event.source.user_id}');")
    database.commit()
    cursor.close()

    return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Welcome"]))

@handler.add(PostbackEvent)
def handle_change(event: PostbackEvent):
    '''
    Handle postback action.
    Postback action occurs when user want to post or update data.
    '''

    data = event.postback.data.split("&")
    action = data[0].split("=")[1]
    type = data[1].split("=")[1]
    profile_type = {"lineID": "line ID", "gender": "性別", "expect_gender": "希望配對的性別", "birth_year": "出生年份", "email": "學校 Email"}
    
    if action == "edit_profile":
        if type == "begin":
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(action = PostbackAction(label = "line id", data = "action=edit_profile&type=lineID")),
                    QuickReplyButton(action = PostbackAction(label = "性別", data = "action=edit_profile&type=gender")),
                    QuickReplyButton(action = PostbackAction(label = "希望配對性別", data = "action=edit_profile&type=expect_gender")),
                    QuickReplyButton(action = PostbackAction(label = "出生年份", data = "action=edit_profile&type=birth_year")),
                    QuickReplyButton(action = PostbackAction(label = "學校 email", data = "action=edit_profile&type=email"))
                    ])
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["How to edit profile"], quick_reply = quick_reply))
        
        elif type == "gender" or type == "expect_gender":
            editting_user[event.source.user_id] = type
            cursor = database.cursor()
            cursor.execute(f"SELECT {type} FROM friends WHERE userID = '{event.source.user_id}';")
            result = cursor.fetchall()
            profile = lambda : result[0][0] if result[0][0] != None else "空"
            cursor.close()
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(action = MessageAction(label = "男", text = "男")),
                    QuickReplyButton(action = MessageAction(label = "女", text = "女")),
                    QuickReplyButton(action = PostbackAction(label = "取消", data = "action=cancel&type=profile"))
                ]
            )
            return line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text = text_dict["Present profile"].format(profile_type = profile_type[type], profile = profile())),
                    TextSendMessage(text = text_dict["Choose gender"], quick_reply = quick_reply)
                ]
            )

        else:
            editting_user[event.source.user_id] = type
            cursor = database.cursor()
            cursor.execute(f"SELECT {type} FROM friends WHERE userID = '{event.source.user_id}';")
            result = cursor.fetchall()
            profile = lambda : result[0][0] if result[0][0] != None else "空"
            cursor.close()
            if type == "birth_year":
                return line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text = text_dict["Present profile"].format(profile_type = profile_type[type], profile = profile())),
                        TextSendMessage(text = text_dict["Edit profile"].format(profile_type = profile_type[type]) + "\n請輸入西元年", quick_reply = QuickReply(items = [QuickReplyButton(action = PostbackAction(label = "取消", data = "action=cancel&type=profile"))]))
                    ]
                )
            return line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text = text_dict["Present profile"].format(profile_type = profile_type[type], profile = profile())),
                    TextSendMessage(text = text_dict["Edit profile"].format(profile_type = profile_type[type]), quick_reply = QuickReply(items = [QuickReplyButton(action = PostbackAction(label = "取消", data = "action=cancel&type=profile"))]))
                ]
            )

    elif action == "cancel":
        if type == "profile":
            editting_user.pop(event.source.user_id)
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Cancel action"]))

@handler.add(MessageEvent, message = TextMessage)
def handle_message(event : MessageEvent):
    '''Handle message used for editting'''

    cursor = database.cursor()
    userID = event.source.user_id

    if editting_user.get(userID) != None:
        if (editting_user.get(userID) == "gender" or editting_user.get(userID) == "expect_gender") and (event.message.text != "男" and event.message.text != "女"):
            editting_user.pop(userID)
            cursor.close()
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Input wrong gender"]))
        elif (editting_user.get(userID) == "email"):
            verifying_code = send_verify_email(event.message.text)
            if verifying_code == "0":
                editting_user.pop(userID)
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Improper email"]))
            editting_user[userID] = "verify email"
            verifying_codes[userID] = [verifying_code, event.message.text]
            cursor.close()
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Input verifying code"].format(email = event.message.text)))
        elif (editting_user.get(userID) == "verify email"):
            if verifying_codes.get(userID)[0] == event.message.text:
                cursor.execute(f"UPDATE friends SET email = '{verifying_codes.get(userID)[1]}' WHERE userID = '{userID}';")
                database.commit()
                cursor.close()
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Verified"]))
            else:
                cursor.close()
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Wrong verifying code"]))
        else:
            cursor.execute(f"UPDATE friends SET {editting_user.pop(userID)} = '{event.message.text}' WHERE userID = '{userID}';")
            database.commit()
            cursor.close()
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Update successfully"].format(message = event.message.text)))

def send_verify_email(recipient: str):
    '''Send a email with verifying code to new updated emails and return the verifying code. If it is not a ntumail, return 0'''

    if recipient.split("@")[1] != "ntu.edu.tw" or len(recipient.split("@")[0]) != 9:
        return "0"

    content = MIMEMultipart()
    content["subject"] = "換書交友 認證信"
    content["from"] = config["DOMAIN_MAIL_ACCOUNT"]
    content["to"] = recipient
    verifying_code = str(random.randint(100000, 999999))
    content.attach(MIMEText("你的驗證碼為 " + verifying_code + " 驗證碼將於3分鐘後失效"))
    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(config["DOMAIN_MAIL_ACCOUNT"], config["DOMAIN_MAIL_PASSWORD"])
            smtp.send_message(content)
        except Exception as e:
            print("Errpr message: ", e)

    return verifying_code

'''
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
'''

if __name__ == "__main__":
    app.run()