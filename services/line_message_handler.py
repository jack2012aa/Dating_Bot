from flask import request, abort
from linebot.models import TextSendMessage, FollowEvent, PostbackEvent, MessageEvent, TextMessage, ImageMessage
from linebot.exceptions import (InvalidSignatureError)
from . import handler, user, book, cache, line_bot_api, text_dict
import models

def line_message_handler(request):
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text = True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature")
        abort(400)
    
    return "OK"

@handler.add(FollowEvent)
def handle_new_follower(event: FollowEvent):
    '''Show welcome messages and insert user into database.'''
    user.add_new_user(event)
    return

@handler.add(PostbackEvent)
def handle_postback(event: PostbackEvent):
    '''Postback events are triggerred by different buttons. Reply these event'''

    data = event.postback.data.split("&")
    action = data[0].split("=")[1]
    type = data[1].split("=")[1]

    if action == "edit_profile":

        if type == "begin":
            return user.begin_edit_user_profile(event)

        elif type == "gender" or type == "expect_gender":
            return user.begin_update_gender(event, type)

        elif type == "choose_gender":
            field = data[2].split("=")[1]
            value = data[3].split("=")[1]
            return user.update_user_profile(event, field, value)
        
        elif type == "birth_year":
            return user.begin_update_with_warning(event, type, "請輸入西元年")
        
        elif type == "email":
            return user.begin_update_with_warning(event, type, "請使用台大信箱，需完成認證才算更改完畢")

        else:
            return user.begin_update(event, type)

    elif action == "upload_book":

        if not models.user.is_profile_finished(event.source.user_id):
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Profile not finished"]))

        if models.book.has_unexchanged_book(event.source.user_id):
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Already have book"]))

        if type == "begin":
            return book.begin_edit_book(event)

        elif type == "photo":
            return book.begin_edit_photo(event)
        
        elif type == "category" or type == "tag":
            return book.begin_edit_tag_or_category(event, type)

        elif type == "choose_category":
            return book.insert_or_update_book(event, type, data[2].split("=")[1])

        elif type == "choose_tag":
            return book.insert_or_delete_tag(event, data[2].split("=")[1])

        elif type == "begin_upload":
            return book.begin_upload(event)

        elif type == "upload":
            return book.upload_editting_book(event)

        else:
            return book.begin_edit(event, type)

    elif action == "find_book":

        if type == "begin":
            return book.begin_find_book(event)

        elif type == "tags" or type == "categories":
            return book.begin_choose_tags_or_categories(event, type)

        elif type == "choose_tags" or type == "choose_categories":
            return book.add_chosen_tags_or_categories(event, type, data[2].split("=")[1])
        
        elif type == "find":
            return book.find_books(event)

        elif type == "next_page":
            return book.next_page(event)

    elif action == "cancel":
        cache.pop(event.source.user_id, None)
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Cancel action"]))
    
@handler.add(MessageEvent, message = TextMessage)
def handle_text_message(event: MessageEvent):
    '''Handle message used for editting'''

    action = cache.get(event.source.user_id)[0]
    type = cache.get(event.source.user_id)[1]
    
    if action == "edit_profile":
        if type == "email":
            return user.send_verifying_email(event)
        
        elif type == "verify_email":
            code = cache.get(event.source.user_id)[2]
            if event.message.text != code:
                cache.pop(event.source.user_id)
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Wrong verifying code"]))
            else:
                address = cache.get(event.source.user_id)[3]
                cache.pop(event.source.user_id)
                return user.update_user_profile(event, type, address)

        elif type == "birth_year":
            try:
                int(event.message.text)
            except:
                cache.pop(event.source.user_id)
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Not year"]))
            if int(event.message.text) < 1923 or int(event.message.text) > 2023:
                cache.pop(event.source.user_id)
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Year out of range"]))
            else:
                cache.pop(event.source.user_id)
                return user.update_user_profile(event, type, event.message.text)
        
        else:
            return user.update_user_profile(event, type, event.message.text)

    elif action == "upload_book":
        return book.insert_or_update_book(event, type, event.message.text)

@handler.add(MessageEvent, message = ImageMessage)
def handle_image(event: MessageEvent):
    
    if cache.get(event.source.user_id, None)[1] == "photo":
       return book.upload_photo(event)