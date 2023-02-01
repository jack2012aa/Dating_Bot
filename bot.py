from flask import Flask, request, abort, send_file
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, ImageMessage, ImageSendMessage,
 TextSendMessage, FollowEvent, CarouselTemplate,CarouselColumn, PostbackTemplateAction, TemplateSendMessage, PostbackEvent, QuickReply, QuickReplyButton, PostbackAction, MessageAction)
import json
import pymysql
from expiringdict import ExpiringDict
from datetime import datetime
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os

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
    "Improper email": "此信箱不是台大學校信箱",
    "Upload book": "透過底下按鈕選擇填入書籍資料\n請在3分鐘內輸入完畢",
    "Repeat email": "此信箱已經被註冊過了",
    "No photo": "目前沒有上傳照片\n請在底下上傳照片",
    "Upload photo": "以上為目前上傳的照片\n請在底下上傳照片",
    "Upload successfully": "上傳成功",
    "Choose categories": "請選擇以下分類",
    "Choose tags": "目前標籤為：{tags}\n愈刪除請選擇已經有的標籤\n愈添加請選擇沒有加入的標籤\n請選擇以下標籤",
    "Delete successfully": "已成功刪除 {message}",
    "Edit book": "請在底下輸入資訊",
    "Empty column": "書籍資料尚未填妥",
    "Already have book": "尚有上架書籍未交換成功。若想上架新書請先下架舊書",
    "Find books": "選擇以下分類或標籤後搜尋",
    "Chosen": "已選擇{choice}",
    "Choose tag with existing tags": "已選擇 {tags}\n愈刪除請選擇已經有的標籤\n愈添加請選擇沒有加入的標籤\n請選擇以下標籤",
    "Choose tag without existing tags": "請選擇以下標籤",
    "Empty search fields": "請至少選擇一項搜尋條件",
    "Search result": "共搜尋到{num}筆結果",
    "More": "更多資訊"
}

editting_user = ExpiringDict(100, 180)
uploading_state = ExpiringDict(max_len=300, max_age_seconds=300)
verifying_codes = ExpiringDict(100, 180)
find_books_query = ExpiringDict(100, 180)
result_books = {}

cancel_quick_reply_button = QuickReplyButton(action = PostbackAction(label = "取消", data = "action=cancel&type=none"))

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
    return send_file(f"static/book/{file_name}", mimetype = "image/jpeg")

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
    userID = event.source.user_id

    if action == "edit_profile":

        clean_state(userID)

        if type == "begin":
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(action = PostbackAction(label = "line id", data = "action=edit_profile&type=lineID")),
                    QuickReplyButton(action = PostbackAction(label = "性別", data = "action=edit_profile&type=gender")),
                    QuickReplyButton(action = PostbackAction(label = "希望配對性別", data = "action=edit_profile&type=expect_gender")),
                    QuickReplyButton(action = PostbackAction(label = "出生年份", data = "action=edit_profile&type=birth_year")),
                    QuickReplyButton(action = PostbackAction(label = "學校 email", data = "action=edit_profile&type=email")),
                    cancel_quick_reply_button
                    ])
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["How to edit profile"], quick_reply = quick_reply))
        
        elif type == "gender" or type == "expect_gender":
            editting_user[userID] = type
            cursor = database.cursor()
            cursor.execute(f"SELECT {type} FROM friends WHERE userID = '{userID}';")
            result = cursor.fetchall()
            profile = lambda : result[0][0] if result[0][0] != None else "空"
            cursor.close()
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(action = MessageAction(label = "男", text = "男")),
                    QuickReplyButton(action = MessageAction(label = "女", text = "女")),
                    cancel_quick_reply_button
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
            editting_user[userID] = type
            cursor = database.cursor()
            cursor.execute(f"SELECT {type} FROM friends WHERE userID = '{userID}';")
            result = cursor.fetchall()
            profile = lambda : result[0][0] if result[0][0] != None else "空"
            cursor.close()
            if type == "birth_year":
                return line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text = text_dict["Present profile"].format(profile_type = profile_type[type], profile = profile())),
                        TextSendMessage(text = text_dict["Edit profile"].format(profile_type = profile_type[type]) + "\n請輸入西元年", quick_reply = QuickReply(items = [cancel_quick_reply_button]))
                    ]
                )
            return line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text = text_dict["Present profile"].format(profile_type = profile_type[type], profile = profile())),
                    TextSendMessage(text = text_dict["Edit profile"].format(profile_type = profile_type[type]), quick_reply = QuickReply(items = [cancel_quick_reply_button]))
                ]
            )

    elif action == "upload_book":

        clean_state(userID)
        '''
        cursor = database.cursor()
        cursor.execute(f"SELECT * FROM books WHERE userID = '{userID}' AND exchanged = 'F';")
        if len(cursor.fetchall()) != 0:
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Already have book"]))
        cursor.close()
'''
        if type == "begin":
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(action = PostbackAction(label = "書名", data = "action=upload_book&type=name")),
                    QuickReplyButton(action = PostbackAction(label = "心得", data = "action=upload_book&type=summary")),
                    QuickReplyButton(action = PostbackAction(label = "照片", data = "action=upload_book&type=photo")),
                    QuickReplyButton(action = PostbackAction(label = "交換方式", data = "action=upload_book&type=exchange_method")),
                    QuickReplyButton(action = PostbackAction(label = "分類", data = "action=upload_book&type=categories")),
                    QuickReplyButton(action = PostbackAction(label = "標籤", data = "action=upload_book&type=tags")),
                    QuickReplyButton(action = PostbackAction(label = "確認上傳", data = "action=upload_book&type=upload")),
                    cancel_quick_reply_button
                ]
            )
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Upload book"], quick_reply = quick_reply))

        elif type == "photo":
            uploading_state[userID] = type
            cursor = database.cursor()
            cursor.execute(f"SELECT photo FROM editting_books WHERE userID = '{userID}';")
            route = cursor.fetchall()
            cursor.close()
            if route[0][0] == None:
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["No photo"], quick_reply = QuickReply(items = [cancel_quick_reply_button])))
            else:
                return line_bot_api.reply_message(
                    event.reply_token,
                    [
                        ImageSendMessage(original_content_url = config["url"] + "/images?file_name=" + route[0][0], preview_image_url = config["url"] + "/images?file_name=" + route[0][0]),
                        TextSendMessage(text = text_dict["Upload photo"], quick_reply = QuickReply(items = [cancel_quick_reply_button]))
                    ]
                )
        
        elif type == "categories":
            cursor = database.cursor()
            cursor.execute("SELECT category FROM categories;")
            categories = list(map(lambda x: x[0], cursor.fetchall()))
            cursor.close()
            quick_reply_buttons = []
            for category in categories:
                quick_reply_buttons.append(QuickReplyButton(action = PostbackAction(label = category, data = "action=upload_book&type=choose_categories&categories=" + category)))
            quick_reply_buttons.append(cancel_quick_reply_button)
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Choose categories"], quick_reply = QuickReply(items = quick_reply_buttons)))

        elif type == "choose_categories":
            category = data[2].split("=")[1]
            cursor = database.cursor()
            cursor.execute(f"INSERT INTO editting_books (userID, category) VALUES ('{userID}', '{category}') ON DUPLICATE KEY UPDATE category = '{category}';")
            database.commit()
            cursor.close()
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Update successfully"].format(message = category)))

        elif type == "tags":
            cursor = database.cursor()
            cursor.execute("SELECT tag FROM tags ORDER BY sort ASC;")
            tags = list(map(lambda x: x[0], cursor.fetchall()))
            cursor.close()
            quick_reply_buttons = []
            for tag in tags:
                quick_reply_buttons.append(QuickReplyButton(action = PostbackAction(label = tag, data = "action=upload_book&type=choose_tags&tags=" + tag)))
            quick_reply_buttons.append(cancel_quick_reply_button)

            cursor = database.cursor()
            cursor.execute(f"SELECT tag FROM editting_tags WHERE userID = '{userID}';")
            chosen_tags = ""
            for chosen_tag in map(lambda x: x[0], cursor.fetchall()):
                chosen_tags = chosen_tags + chosen_tag + " "
            if len(chosen_tags) == 0:
                chosen_tags = "空"
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Choose tags"].format(tags = chosen_tags), quick_reply = QuickReply(items = quick_reply_buttons)))

        elif type == "choose_tags":
            tag = data[2].split("=")[1]
            cursor = database.cursor()
            cursor.execute(f"SELECT * FROM editting_tags WHERE userID = '{userID}' AND tag = '{tag}';")
            exist = len(cursor.fetchall()) == 1;
            cursor.close()

            cursor = database.cursor()
            if not exist:
                cursor.execute(f"INSERT INTO editting_tags (userID, tag) VALUES ('{userID}', '{tag}');")
                database.commit()
                cursor.close()
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Update successfully"].format(message = tag)))
            else:
                cursor.execute(f"DELETE FROM editting_tags WHERE userID = '{userID}' AND tag = '{tag}';")
                database.commit()
                cursor.close()
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Delete successfully"].format(message = tag)))
        
        elif type == "upload":
            cursor = database.cursor()
            cursor.execute(f"SELECT * FROM editting_books WHERE userID = '{userID}' AND name IS NOT NULL AND summary IS NOT NULL AND photo IS NOT NULL AND exchange_method IS NOT NULL AND category IS NOT NULL;")
            empty_column = len(cursor.fetchall()) == 0
            cursor.close()
            if empty_column:
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Empty column"]))
            else:
                cursor = database.cursor()
                cursor.execute(f"INSERT INTO books (userID, name, summary, photo, exchange_method, category) SELECT userID, name, summary, photo, exchange_method, category FROM editting_books WHERE userID = '{event.source.user_id}';")
                cursor.execute(f"DELETE FROM editting_books WHERE userID = '{userID}';")
                database.commit()
                cursor.execute(f"SELECT upload_time FROM books WHERE userID = '{userID}' AND exchanged = 'F';")
                upload_time = cursor.fetchall()[0][0]
                cursor.execute(f"SELECT tag FROM editting_tags WHERE userID = '{userID}';")
                tags = list(map(lambda x: x[0], cursor.fetchall()))
                cursor.execute(f"DELETE FROM editting_tags WHERE userID = '{userID}';")
                for tag in tags:
                    cursor.execute(f"INSERT INTO book_tags (userID, tag, upload_time) VALUES ('{userID}', '{tag}', '{upload_time}');")
                database.commit()
                cursor.close()
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Upload successfully"]))
        
        else:
            uploading_state[userID] = type
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Edit book"], quick_reply = QuickReply(items = [cancel_quick_reply_button])))

    elif action == "find_book":
        
        clean_state(userID)

        if type == "begin":
            quick_reply_buttons = [
                QuickReplyButton(action = PostbackAction(label = "分類", data = "action=find_book&type=categories")),
                QuickReplyButton(action = PostbackAction(label = "標籤", data = "action=find_book&type=tags")),
                QuickReplyButton(action = PostbackAction(label = "搜尋", data = "action=find_book&type=find")),
                cancel_quick_reply_button
            ]
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Find books"], quick_reply = QuickReply(items = quick_reply_buttons)))
        
        elif type == "categories":
            cursor = database.cursor()
            cursor.execute("SELECT category FROM categories;")
            categories = list(map(lambda x: x[0], cursor.fetchall()))
            cursor.close()
            quick_reply_buttons = []
            for category in categories:
                quick_reply_buttons.append(QuickReplyButton(action = PostbackAction(label = category, data = "action=find_book&type=choose_categories&categories=" + category)))
            quick_reply_buttons.append(cancel_quick_reply_button)
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Choose categories"], quick_reply = QuickReply(items = quick_reply_buttons)))

        elif type == "choose_categories":
            category = data[2].split("=")[1]
            if find_books_query.get(userID) == None:
                find_books_query[userID] = {"category":category}
            else:
                find_books_query[userID]["category"] = category
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Chosen"].format(choice = category)))

        elif type == "tags":
            cursor = database.cursor()
            cursor.execute("SELECT tag, sort FROM tags ORDER BY sort ASC;")
            tags = list(map(lambda x: [x[0],x[1]], cursor.fetchall()))
            cursor.close()
            quick_reply_buttons = []
            for tag in tags:
                quick_reply_buttons.append(QuickReplyButton(action = PostbackAction(label = tag[0], data = "action=find_book&type=choose_tags&tags=" + str(tag[1]))))
            quick_reply_buttons.append(cancel_quick_reply_button)

            if find_books_query.get(userID) != None:
                chosen = find_books_query.get(userID).get("tags")
                if chosen != None:
                    chosen_tags = []
                    for i in range(1, 13):
                        if chosen[i]:
                            chosen_tags.append(tags[i - 1][0])
                    return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Choose tag with existing tags"].format(tags = " ".join(chosen_tags)), quick_reply = QuickReply(quick_reply_buttons)))
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Choose tag without existing tags"], quick_reply = QuickReply(items = quick_reply_buttons)))

        elif type == "choose_tags":
            tag = int(data[2].split("=")[1])
            if find_books_query.get(userID) == None:
                find_books_query[userID] = {"tags":[False] * 13}
            else:
                if find_books_query.get(userID).get("tags") == None:
                    find_books_query.get(userID)["tags"] = [False] * 13
            
            find_books_query.get(userID).get("tags")[tag] = not find_books_query.get(userID).get("tags")[tag]
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Chosen"].format(choice = "")))

        elif type == "find":
            if find_books_query.get(userID) == None:
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Empty search fields"]))
            category = find_books_query.get(userID).get("category")
            choice = find_books_query.get(userID).get("tags")
            query_string = "\
                SELECT DISTINCT a.name, a.photo, a.upload_time, a.userID \
                FROM books a JOIN friends c ON a.userID = c.userID JOIN book_tags ON a.userID = book_tags.userID AND a.upload_time = book_tags.upload_time\
                WHERE a.exchanged = 'F' AND a.blocked = 'F' AND a.userID != '{self}' AND c.gender = '{gender}' AND c.expect_gender = '{expect_gender}' {category} {tags}\
                ORDER BY \
                (SELECT count(*) \
                FROM book_tags \
                WHERE book_tags.userID = a.userID AND book_tags.upload_time = a.upload_time {tags}) \
                DESC;"
            if category == None:
                category = ""
            else:
                category = "AND category = '" + category + "'"

            if choice == None:
                chosen_tags = ""
            else:
                chosen_tags = []
                cursor = database.cursor()
                cursor.execute("SELECT tag FROM tags ORDER BY sort ASC;")
                tags = cursor.fetchall()
                cursor.close()
                for i in range(1, 13):
                    if choice[i]:
                        chosen_tags.append("book_tags.tag = '" + tags[i - 1][0] + "'")
                chosen_tags = "AND (" + " OR ".join(chosen_tags) + ")"
            
            cursor = database.cursor()
            cursor.execute(f"SELECT gender, expect_gender FROM friends WHERE userID = '{userID}';")
            expect_gender, gender = cursor.fetchall()[0]
            cursor.close()

            cursor = database.cursor()
            query_string = query_string.format(category = category, tags = chosen_tags, self = userID, gender = gender, expect_gender = expect_gender)
            print(query_string)
            cursor.execute(query_string)
            books = list(cursor.fetchall())
            result_length = len(books)
            result_books[userID] = books
            cursor.close()

            books_carouel = []
            for i in range(min(10, len(books))):
                book = books.pop(0)
                cursor = database.cursor()
                cursor.execute(f"SELECT tag FROM book_tags WHERE userID = '{book[3]}' AND upload_time = '{book[2]}';")
                tags = list(map(lambda x: x[0], cursor.fetchall()))
                cursor.close()
                tags_string = " ".join(tags)
                books_carouel.append(
                    CarouselColumn(
                        thumbnail_image_url = config["url"] + "/images?file_name=" + book[1],
                        title = book[0],
                        text = "標籤: " + tags_string,
                        actions = [PostbackTemplateAction(label = text_dict["More"], data = f"action=show_book_detail&type={book[3]}+{book[2]}")]
                    )
                )
            
            if len(books) == 0:
                return line_bot_api.reply_message(event.reply_token, [
                    TextSendMessage(text = text_dict["Search result"].format(num = result_length)),
                    TemplateSendMessage(alt_text = text_dict["See on the phone"], template = CarouselTemplate(columns = books_carouel))
                ])
            else:
                return line_bot_api.reply_message(event.reply_token, [
                    TextSendMessage(text = text_dict["Search result"].format(num = result_length)),
                    TemplateSendMessage(alt_text = text_dict["See on the phone"], template = CarouselTemplate(columns = books_carouel),
                    quick_reply = QuickReply(items = [QuickReplyButton(action = PostbackAction(label = "下一頁", data = "action=find_book&type=next_page"))]))
                ])

        elif type == "next_page":
            books = result_books.get(userID)
            books_carouel = []
            for i in range(min(10, len(books))):
                book = books.pop(0)
                cursor = database.cursor()
                cursor.execute(f"SELECT tag FROM book_tags WHERE userID = '{book[3]}' AND upload_time = '{book[2]}';")
                tags = list(map(lambda x: x[0], cursor.fetchall()))
                cursor.close()
                tags_string = " ".join(tags)
                books_carouel.append(
                    CarouselColumn(
                        thumbnail_image_url = config["url"] + "/images?file_name=" + book[1],
                        title = book[0],
                        text = "標籤: " + tags_string,
                        actions = [PostbackTemplateAction(label = text_dict["More"], data = f"action=show_book_detail&type={book[3]}+{book[2]}")]
                    )
                )
            
            if len(books) == 0:
                result_books.pop(userID)
                return line_bot_api.reply_message(event.reply_token, [
                    TemplateSendMessage(alt_text = text_dict["See on the phone"], template = CarouselTemplate(columns = books_carouel))
                ])
            else:
                return line_bot_api.reply_message(event.reply_token, [
                    TemplateSendMessage(alt_text = text_dict["See on the phone"], template = CarouselTemplate(columns = books_carouel),
                    quick_reply = QuickReply(items = [QuickReplyButton(action = PostbackAction(label = "下一頁", data = "action=find_book&type=next_page"))]))
                ])

    elif action == "show_book_detail":
        print(type)

    elif action == "cancel":
        clean_state(userID)
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
            cursor.execute(f"SELECT * FROM friends WHERE email = '{event.message.text}';")
            if len(cursor.fetchall()) > 0:
                editting_user.pop(userID)
                cursor.close()
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Repeat email"]))
            verifying_code = send_verify_email(event.message.text)
            if verifying_code == "0":
                editting_user.pop(userID)
                cursor.close()
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Improper email"]))
            editting_user[userID] = "verify email"
            verifying_codes[userID] = [verifying_code, event.message.text]
            cursor.close()
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Input verifying code"].format(email = event.message.text), quick_reply = QuickReply([cancel_quick_reply_button])))
        
        elif (editting_user.get(userID) == "verify email"):
            if verifying_codes.get(userID)[0] == event.message.text:
                cursor.execute(f"UPDATE friends SET email = '{verifying_codes.get(userID)[1]}' WHERE userID = '{userID}';")
                database.commit()
                cursor.close()
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Verified"]))
            else:
                cursor.close()
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Wrong verifying code"], quick_reply = QuickReply([cancel_quick_reply_button])))
        
        else:
            cursor.execute(f"UPDATE friends SET {editting_user.pop(userID)} = '{event.message.text}' WHERE userID = '{userID}';")
            database.commit()
            cursor.close()
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Update successfully"].format(message = event.message.text)))
    
    elif uploading_state.get(userID) != None:
        type = uploading_state.pop(userID)
        cursor.execute(f"INSERT INTO editting_books (userID, {type}) VALUES ('{event.source.user_id}', '{event.message.text}') ON DUPLICATE KEY UPDATE {type} = '{event.message.text}';")
        database.commit()
        cursor.close()
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Upload successfully"]))

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

@handler.add(MessageEvent, message = ImageMessage)
def handle_image(event: MessageEvent):
    
    if uploading_state.pop(event.source.user_id) == "photo":

        photo = line_bot_api.get_message_content(event.message.id)
        file_name = str(datetime.timestamp(datetime.now())) + ".jpeg"
        with open(f"./static/book/{file_name}", 'wb') as f:
            for chunk in photo.iter_content():
                f.write(chunk)
        cursor = database.cursor()
        cursor.execute(f"SELECT photo FROM editting_books WHERE userID = '{event.source.user_id}';")
        deleted_file = cursor.fetchall()[0][0]
        if deleted_file != None:
            os.remove("./static/book/" + deleted_file)
        cursor.close()
        cursor = database.cursor()
        cursor.execute(f"INSERT INTO editting_books (userID, photo) VALUES ('{event.source.user_id}', '{file_name}') ON DUPLICATE KEY UPDATE photo = '{file_name}';")
        database.commit()
        cursor.close()
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Upload successfully"]))

def clean_state(userID : str):
    uploading_state.pop(userID)
    editting_user.pop(userID)
    return

if __name__ == "__main__":
    app.run()