'''Define APIs relate to upload book and act info. API will contact with model, check user's information and return an array of line reply messages or/and whether the input is valid.'''
import models, boto3
from . import config
from io import BytesIO
from datetime import datetime
from linebot.models import TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, PostbackAction

text_dict = {
    #Invalid user
    "Profile not finished": "請先將個人資訊填寫完畢再參加活動",
    "Already have book": "尚有上架書籍未交換成功。若想上架新書請先下架舊書",
    "Already exchanged today": "已經配對成功咯，快去配對邀請查看",

    #Choose
    "Choose what to edit": "透過底下按鈕選擇填入書籍資料",

    #act_info
    "Activity info": "你喜歡藉由分享閱讀的感動與喜悅來結交更多朋友嗎？\n這是一個結合讀書與交友的活動，透過這個活動不只可以將喜歡的書推廣出去，還能認識更多的書籍愛好者。\n心動不如馬上行動！",
    "Find method": "點選「尋找新書」，可選擇「分類」或「標籤」或「隨機」三種配對方式，看到喜歡的書籍可送出配對邀請\n\n1.「分類」：可單選或重複點選進行多選，選擇完後點選「搜尋」進行配對\n2.「標籤」：可單選或重複點選進行多選，選擇完後點選「搜尋」進行配對\n3.「隨機」：會直接跳出配對選項",
    "Invite and delete method": "點選「配對邀請」查看有無邀請，如「接受邀請」會收到對方line id，並於隔日才能再次配對\n\n點選「自己的書」可以查看或刪除原本上架的書籍；刪除後原先送出的配對邀請會刪除，請再重新「上傳新書」進行配對",
    "Activity warning": "注意事項：\n1.一次只能上架一本書\n2.一本書一天只能交換一次",

    #How to edit
    "Upload method": "點選「上傳新書」後可選擇「全部設定」一次性設定完所有資料、或選擇個別資料進行設定\n\n資料全部填妥後，點選「確認上傳」，如無誤再按下「確認」，完成上傳",
    "Edit order": "將依序設定以下資料：\n1.書名\n2.心得\n3.照片\n4.分類\n5.標籤",
    "How to edit name": "請透過文字輸入書名\n書名不可超過100字，若超過40字則在查詢結果中會有字被省略",
    "How to edit summary": "請透過文字輸入心得\n心得不可以超過1000字，越長對方看得越心煩，所以言簡意賅的表達吧！",
    "How to edit photo": "請從手機相簿中選擇書籍的照片並送出\n若不是上傳照片，將不會有任何回應",
    "How to edit category": "請透過下方按鈕選擇書籍分類\n請勿透過文字輸入",
    "How to edit tag": "請透過下方按鈕選擇書籍標籤\n一本書可以有多個標籤，點擊已選擇的標籤會刪除該標籤\n若以選則完畢，請按「完成」",

    #Error
    "Unknown error": "發生未知錯誤，請再試一次",
    "Name too long": "書名過長，請勿超過100字，請再試一次",
    "Summary too long": "心得過長，請勿超過1000字，請再試一次",
    "Empty column": "書籍資料尚未填妥",
    "Don't have editting book": "沒有編輯中的書籍",

    #Present information
    "Null information": "尚未設定{field}",
    "Present information": "目前的{field}為{value}",

    #Finish edit
    "Edit successfully": "已成功更改為 {value}",
    "Upload photo successfully": "已成功上傳照片",
    "Delete tag": "已成功刪除{tag}",
    "Insert tag": "已成功添加{tag}",
    "Finish": "編輯成功",
    "Upload book successfully": "已成功上架書籍",

    #All book info
    "Book info": "書名：{name}\n心得：{summary}\n分類：{category}\n標籤：{tags}",
}

cancel_quick_reply_button = QuickReplyButton(action = PostbackAction(label = "取消", display_text = "取消動作",data = "action=cancel&type=none"))

def is_valid(userID: str):
    '''
    Check has the user finished his profile, do his have a book or an accepted invitation. 
    :param str userID: line user ID
    :return an error text message and false if the user is invalid, else return an empty list and true
    '''

    if not models.user.is_profile_finished(userID):
        return [TextSendMessage(text_dict["Profile not finished"])], False
    
    if models.exchange_book.has_book(userID, True):
        return [TextSendMessage(text_dict["Already have book"])], False
    
    if models.exchange_book.has_accept_invitation(userID):
        return [TextSendMessage(text_dict["Already exchanged today"])], False

    return [], True

def choose_what_to_edit(userID: str):
    '''
    Show quick replys and let user choose what to edit.
    :param str userID: line user id
    '''

    #Get green and red image url
    s3 = boto3.client("s3", aws_access_key_id = config["aws_access_key_id"], aws_secret_access_key = config["aws_secret_access_key"])
    red_url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": "red.png"})
    green_url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": "green.png"})

    #Set NULL column with red_url, not Null with green_url
    infos = models.exchange_book.get_editting_book_information(userID, all = True)
    if infos[0] != None:
        url_list = []
        for i in range(1, 5):
            if infos[i] == None:
                url_list.append(red_url)
            else:
                url_list.append(green_url)

        tag = models.exchange_book.get_editting_tags(userID)[0]
        if tag == None:
            url_list.append(red_url)
        else:
            url_list.append(green_url)
    else:
        url_list = [red_url] * 5
    
    quick_reply = QuickReply(
        items = [
            QuickReplyButton(action = PostbackAction(label = "全部設定", display_text = "全部設定", data = "action=upload_book&type=begin_edit_all")),
            QuickReplyButton(action = PostbackAction(label = "書名", display_text = "編輯 書名", data = "action=upload_book&type=begin_edit_name"), image_url = url_list[0]),
            QuickReplyButton(action = PostbackAction(label = "心得", display_text = "編輯 心得", data = "action=upload_book&type=begin_edit_summary"), image_url = url_list[1]),
            QuickReplyButton(action = PostbackAction(label = "照片", display_text = "編輯 照片", data = "action=upload_book&type=begin_edit_photo"), image_url = url_list[2]),
            QuickReplyButton(action = PostbackAction(label = "分類", display_text = "編輯 分類", data = "action=upload_book&type=begin_edit_category"), image_url = url_list[3]),
            QuickReplyButton(action = PostbackAction(label = "標籤", display_text = "編輯 標籤", data = "action=upload_book&type=begin_edit_tag"), image_url = url_list[4]),
            QuickReplyButton(action = PostbackAction(label = "確認上傳", data = "action=upload_book&type=begin_upload")),
            cancel_quick_reply_button
        ]
    )
    return [TextSendMessage(text_dict["Choose what to edit"], quick_reply = quick_reply)]

def act_info():
    '''
    Show information about present activity and quick replies to learn more.
    '''

    quick_replies = QuickReply([
        QuickReplyButton(action = PostbackAction(label = "如何上傳書籍？", display_text = "如何上傳書籍？", data = "action=act_info&type=upload_book")),
        QuickReplyButton(action = PostbackAction(label = "如何尋找書籍？", display_text = "如何尋找書籍？", data = "action=act_info&type=find_book")),
        QuickReplyButton(action = PostbackAction(label = "如何送出配對邀請？", display_text = "如何送出配對邀請？", data = "action=act_info&type=invite")),
        cancel_quick_reply_button
    ])
    
    return [TextSendMessage(text_dict["Activity info"], quick_reply = quick_replies)]

def how_to_upload():
    '''
    Show how to edit and upload a book.
    '''

    quick_replies = QuickReply([
        QuickReplyButton(action = PostbackAction(label = "如何編輯書名？", display_text = "如何編輯書名？", data = "action=act_info&type=how_to_edit_name")),
        QuickReplyButton(action = PostbackAction(label = "如何編輯心得？", display_text = "如何編輯心得？", data = "action=act_info&type=how_to_edit_summary")),
        QuickReplyButton(action = PostbackAction(label = "如何編輯照片？", display_text = "如何編輯照片？", data = "action=act_info&type=how_to_edit_photo")),
        QuickReplyButton(action = PostbackAction(label = "如何編輯分類？", display_text = "如何編輯分類？", data = "action=act_info&type=how_to_edit_category")),
        QuickReplyButton(action = PostbackAction(label = "如何編輯標籤？", display_text = "如何編輯標籤？", data = "action=act_info&type=how_to_edit_tag")),
        cancel_quick_reply_button
    ])

    return [TextSendMessage(text_dict["Upload method"], quick_reply = quick_replies)]

def how_to_edit(type: str):
    '''
    Show how to edit specific type of information of books.
    :param str type: in ["how_to_edit_name","how_to_edit_summary","how_to_edit_photo","how_to_edit_category","how_to_edit_tag"]
    '''

    quick_replies = QuickReply([
        QuickReplyButton(action = PostbackAction(label = "如何編輯書名？", display_text = "如何編輯書名？", data = "action=act_info&type=how_to_edit_name")),
        QuickReplyButton(action = PostbackAction(label = "如何編輯心得？", display_text = "如何編輯心得？", data = "action=act_info&type=how_to_edit_summary")),
        QuickReplyButton(action = PostbackAction(label = "如何編輯照片？", display_text = "如何編輯照片？", data = "action=act_info&type=how_to_edit_photo")),
        QuickReplyButton(action = PostbackAction(label = "如何編輯分類？", display_text = "如何編輯分類？", data = "action=act_info&type=how_to_edit_category")),
        QuickReplyButton(action = PostbackAction(label = "如何編輯標籤？", display_text = "如何編輯標籤？", data = "action=act_info&type=how_to_edit_tag")),
        cancel_quick_reply_button
    ])

    if type not in ["how_to_edit_name","how_to_edit_summary","how_to_edit_photo","how_to_edit_category","how_to_edit_tag"]:
        return [TextSendMessage(text_dict["Unknown error"])]
    else:
        return [TextSendMessage(text_dict[type.replace("_", " ").capitalize()], quick_reply = quick_replies)]

def begin_edit(userID: str, type: str, continuously: bool = False):
    '''
    Show present editted book's info and show how to edit info.
    :param str userID: line user id
    :param str type: ["begin_edit_name","begin_edit_summary","begin_edit_photo","begin_edit_category","begin_edit_tag"]
    :param bool continuously: if the user is editting in continuous mode, this param should be true and will add a skip button before the cancel button.
    '''

    #Get present book info
    type = type[11:]
    if type == "tag":
        tags = models.exchange_book.get_editting_tags(userID)
        if tags[0] == None:
            present = None
        else:
            present = "、".join(tags)
    else:
        present = models.exchange_book.get_editting_book_information(userID, [type])[0]
    
    #Prepare quick replies
    quick_replies = []
    if type == "category":
        categories = models.exchange_book.get_all_categories()
        for category in categories:
            quick_replies.append(QuickReplyButton(action = PostbackAction(label = category, display_text = category, data = f"action=upload_book&type=edit_{type}&value={category}")))
        if continuously:
            quick_replies.append(QuickReplyButton(action = PostbackAction(label = "跳過", display_text = "跳過", data = "action=upload_book&type=skip")))
        quick_replies.append(cancel_quick_reply_button)
    elif type == "tag":
        tags = models.exchange_book.get_all_tags()
        chosen_tags = models.exchange_book.get_editting_tags(userID)
        #Get green and red image url
        s3 = boto3.client("s3", aws_access_key_id = config["aws_access_key_id"], aws_secret_access_key = config["aws_secret_access_key"])
        red_url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": "red.png"})
        green_url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": "green.png"})
        for tag in tags:
            if tag in chosen_tags:
                quick_replies.append(QuickReplyButton(action = PostbackAction(label = tag, display_text = tag, data = f"action=upload_book&type=edit_{type}&value={tag}"), image_url = red_url))
            else:
                quick_replies.append(QuickReplyButton(action = PostbackAction(label = tag, display_text = tag, data = f"action=upload_book&type=edit_{type}&value={tag}"), image_url = green_url))
        quick_replies.append(QuickReplyButton(action = PostbackAction(label = "完成", display_text = "完成", data = "action=upload_book&type=finish")))
    else:
        if continuously:
            quick_replies.append(QuickReplyButton(action = PostbackAction(label = "跳過", display_text = "跳過", data = f"action=upload_book&type=skip")))
        quick_replies.append(cancel_quick_reply_button)

    type_dict = {
        "name": "書名",
        "summary": "心得",
        "photo": "照片",
        "category": "分類",
        "tag": "標籤"
    }

    if type == "photo" and present != None:
        s3 = boto3.client("s3", aws_access_key_id = config["aws_access_key_id"], aws_secret_access_key = config["aws_secret_access_key"])
        url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": present})
        return [ImageSendMessage(url, url), TextSendMessage(text_dict[f"How to edit {type}"], quick_reply = QuickReply(quick_replies))]

    if present == None:
        return [TextSendMessage(text_dict["Null information"].format(field = type_dict[type])), TextSendMessage(text_dict[f"How to edit {type}"], quick_reply = QuickReply(quick_replies))]
    else:
        return [TextSendMessage(text_dict["Present information"].format(field = type_dict[type], value = present)), TextSendMessage(text_dict[f"How to edit {type}"], quick_reply = QuickReply(quick_replies))]

def edit_name(userID: str, name: str):
    '''
    Check whether the name is valid. If valid, update name to database and return success messages and true. If not valid return error message and false.
    :parapm str userID: line user id
    :param str name: book's name, must less than 100 words
    :return [TextSendMessage], bool
    '''

    if len(name) > 100:
        return [TextSendMessage(text_dict["Name too long"])], False
    
    ok = models.exchange_book.insert_or_update_editting_book(userID, "name", name)
    if not ok:
        return [TextSendMessage(text_dict["Unknown error"])], False
    return [TextSendMessage(text_dict["Edit successfully"].format(value = name))], True

def edit_summary(userID: str, summary: str):
    '''
    Check whether the summary is valid. If valid, update summary to database and return success messages and true. If not valid return error message and false.
    :parapm str userID: line user id
    :param str summary: book's summary, must less than 1000 words
    :return [TextSendMessage], bool
    '''

    if len(summary) > 1000:
        return [TextSendMessage(text_dict["Summary too long"])], False
    
    ok = models.exchange_book.insert_or_update_editting_book(userID, "summary", summary)
    if not ok:
        return [TextSendMessage(text_dict["Unknown error"])], False
    return [TextSendMessage(text_dict["Edit successfully"].format(value = summary))], True

def edit_photo(userID: str, photo):
    '''
    Upload photo onto S3 bucket, save its name into database and delete the old one.
    :param str userID: line user id
    :param photo: line response.content object
    '''

    s3 = boto3.client("s3", aws_access_key_id = config["aws_access_key_id"], aws_secret_access_key = config["aws_secret_access_key"])

    #Delete old photo
    photo_dir = models.exchange_book.get_editting_book_information(userID, ["photo"])[0]
    if photo_dir != None:
        s3.delete_object(Bucket = "linedatingapp", Key = photo_dir)

    #Change photo from content type into bytes and upload to S3
    photo = BytesIO(photo.content)
    photo_dir = str(datetime.timestamp(datetime.now())) + ".jpeg"
    s3.upload_fileobj(photo, "linedatingapp", photo_dir)
    photo.close()

    ok = models.exchange_book.insert_or_update_editting_book(userID, "photo", photo_dir)
    if not ok:
        return [TextSendMessage(text_dict["Unknown error"])], False
    return [TextSendMessage(text_dict["Upload photo successfully"])], True

def edit_category(userID: str, category: str):
    '''
    Check whether the category is valid. If valid, update category to database and return success messages and true. If not valid return error message and false.
    :param str userID: line user id
    :param str category: book's category, must be declared in the database
    '''

    categories = models.exchange_book.get_all_categories()
    if category not in categories:
        return [TextSendMessage(text_dict["Unknown error"])], False
    ok = models.exchange_book.insert_or_update_editting_book(userID, "category", category)
    if not ok:
        return [TextSendMessage(text_dict["Unknown error"])], False
    return [TextSendMessage(text_dict["Edit successfully"].format(value = category))], True

def edit_tag(userID: str, tag: str):
    '''
    Check whether the tag is valid.
    If not valid return error message and false.
    If valid and the tag hasn't been chosen, insert the tag into database.
    If valid and the tag has been chosen, delete the tag from database.
    :param str userID: line user id
    :param str tag: book's tag, must be declared in the database
    '''

    tags = models.exchange_book.get_all_tags()
    if tag not in tags:
        return [TextSendMessage(text_dict["Unknown error"])], False
    
    try:
        chosen_tags = models.exchange_book.get_editting_tags(userID)
        if tag in chosen_tags:
            models.exchange_book.delete_editting_tag(userID, tag)
            return [TextSendMessage(text_dict["Delete tag"].format(tag = tag))], True
        else:
            models.exchange_book.insert_editting_tag(userID, tag)
            return [TextSendMessage(text_dict["Insert tag"].format(tag = tag))], True
    except:
        return [TextSendMessage(text_dict["Unknown error"])], False

def get_continuous_edit_order():
    '''
    Return the order to edit info of book in continuous mode.
    '''

    return [TextSendMessage(text_dict["Edit order"])]

def finish():
    '''Get finish message.'''
    return [TextSendMessage(text_dict["Finish"])]

def begin_upload(userID: str):
    '''
    Show editting book's info and quick reply for check.
    :param str userID: line user id
    '''

    book = models.exchange_book.get_editting_book_information(userID, all = True)
    if len(book) <= 1:
        return [TextSendMessage(text_dict["Don't have editting book"])]
    
    result = []

    #Set image message
    photo = book[3]
    if photo != None:
        s3 = boto3.client("s3", aws_access_key_id = config["aws_access_key_id"], aws_secret_access_key = config["aws_secret_access_key"])
        url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": photo})
        result.append(ImageSendMessage(url, url))
    
    #Get tags
    tags = models.exchange_book.get_editting_tags(userID)
    if tags[0] == None:
        tags = "尚未設定"
    else:
        tags = "、".join(tags)

    #Handle empty column
    for i in range(len(book)):
        if book[i] == None:
            book[i] = "尚未設定"

    result.append(TextSendMessage(
        text_dict["Book info"].format(name = book[1], summary = book[2], category = book[4], tags = tags),
        quick_reply = QuickReply([QuickReplyButton(action = PostbackAction(label = "確認上傳", data = "action=upload_book&type=upload", display_text = "確認上傳")), cancel_quick_reply_button])
    ))
    return result

def upload(userID: str):
    '''
    Check editting book info. If no info is empty then upload it and delete the editting book.
    :param str userID: line user ID
    :return a list of message and bool indicates whether upload successfully
    '''

    if models.exchange_book.has_empty_column(userID):
        return [TextSendMessage(text_dict["Empty column"])], False

    if models.exchange_book.upload_book(userID):
        return [TextSendMessage(text_dict["Upload book successfully"])], True
    else:
        return [TextSendMessage(text_dict["Unknown error"])], False