from linebot import (LineBotApi, WebhookHandler)
from linebot.models import QuickReplyButton, PostbackAction
import json

with open("setting.json") as json_file:
    config = json.load(json_file)

line_bot_api = LineBotApi(config["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(config["CHANNEL_SECRET"])

text_dict = {
    #Relate with user
    "Welcome": "歡迎使用本服務～\n\n若想參加活動，請先使用下方功能按鈕更新資料並驗證",
    "How to edit profile": "透過底下按鈕選擇要修改哪項個人資訊，再輸入希望更改的訊息",
    "Null profile": "尚未設定{profile_type}",
    "Present profile": "目前的{profile_type}為 {profile}",
    "Update successfully": "已成功更改為 {value}",
    "Edit profile": "請在底下輸入您的{profile_type}",
    "Choose gender": "請選擇以下性別",
    "Repeat email": "此信箱已經被註冊過了",
    "Improper email": "此信箱不是台大學校信箱",
    "Verifying email title": "換書交友活動 認證信",
    "Verifying email content": "您的驗證碼為{code}。請勿回覆此訊息。",
    "Input verifying code": "驗證碼已發送至{email}，請輸入驗證碼",
    "Wrong verifying code": "驗證碼錯誤，請重新索取驗證碼",
    "Not year": "請輸入數字作為年份",
    "Year out of range": "請輸入合理的年份",

    #Relate with uploading book
    "Profile not finished": "請先將個人資訊填寫完畢再參加活動",
    "Already have book": "尚有上架書籍未交換成功。若想上架新書請先下架舊書",
    "Upload book": "透過底下按鈕選擇填入書籍資料",
    "Null information": "尚未上傳{field}",
    "Edit information": "請在底下輸入/上傳新的書籍{field}",
    "Upload photo successfully": "已成功上傳照片",
    "Present information": "目前的{field}為{information}",
    "Choose information": "請選擇以下{field}",
    "Upload successfully": "已成功更改為 {value}",
    "Delete tag": "已成功刪除{tag}",
    "Insert tag": "已成功添加{tag}",
    "Empty column": "書籍資料尚未填妥",
    "Upload book successfully": "已成功上架書籍",
    "Find books": "選擇以下分類或標籤後搜尋",
    "Empty search fields": "尚未選擇搜尋條件",
    "Choose search fields": "請選擇以下分類/標籤",
    "Present search fields": "目前以選擇搜尋條件：\n{values}",
    "Chosen": "已選擇",

    "See on the phone": "請於手機端觀看",
    "Cancel action": "已取消動作",
    "Verified": "已通過驗證",
    "Upload photo": "以上為目前上傳的照片\n請在底下上傳照片",
    "Choose categories": "請選擇以下分類",
    "Delete successfully": "已成功刪除 {message}",
    "Edit book": "請在底下輸入資訊",
    "Search result": "共搜尋到{num}筆結果",
    "More": "更多資訊"
}

cancel_quick_reply_button = QuickReplyButton(action = PostbackAction(label = "取消", display_text = "取消動作",data = "action=cancel&type=none"))
cache = {}

from . import user, book