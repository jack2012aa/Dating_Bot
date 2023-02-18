from flask import abort, current_app
from linebot.models import TextSendMessage, FollowEvent, PostbackEvent, MessageEvent, TextMessage, ImageMessage
from linebot.exceptions import (InvalidSignatureError)
from . import handler, user, book, cache, line_bot_api, text_dict, department_dict
import models
from datetime import datetime

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
    current_app.logger.info(f"[{datetime.now()}] Follow event. ID: {event.source.user_id}")
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
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return user.begin_edit_user_profile(event)

        elif type == "gender" or type == "expect_gender":
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return user.begin_update_gender(event, type)

        elif type == "choose_gender":
            field = data[2].split("=")[1]
            value = data[3].split("=")[1]
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, Field: {field}, Value: {value}")
            return user.update_user_profile(event, field, value)
        
        elif type == "birth_year":
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return user.begin_update_with_warning(event, type, "請輸入西元年")
        
        elif type == "email":
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return user.begin_update_with_warning(event, type, "請使用台大信箱，需完成認證才算更改完畢")

        elif type == "lineID":
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return user.begin_update(event, type)

        elif type == "get_all":
            me = models.user.get_user_profiles(event.source.user_id, all = True)
            for i in range(len(me)):
                if me[i] == None:
                    me[i] = "尚未設定"
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return line_bot_api.reply_message(event.reply_token, text_dict["My profile"].format(lineID = me[1], gender = me[2], expect_gender = me[3], year = me[4], email = me[5]))

    elif action == "teaching":

        current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Teaching"]))

    elif action == "contact_us":

        current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Contact info"]))

    elif action == "upload_book":

        if not models.user.is_profile_finished(event.source.user_id):
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, Exception: Profile not finished")
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Profile not finished"]))

        elif models.book.has_book(event.source.user_id, True):
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, Exception: Already have an unexchanged, unblocked book")
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Already have book"]))

        elif models.book.has_accept_invitation(event.source.user_id):
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, Exception: Already have an accepted invitation")
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Finished"]))

        elif type == "begin":
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return book.begin_edit_book(event)

        elif type == "photo":
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return book.begin_edit_photo(event)
        
        elif type == "category" or type == "tag":
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return book.begin_edit_tag_or_category(event, type)

        elif type == "choose_category":
            category = data[2].split("=")[1]
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, category: {category}")
            return book.insert_or_update_book(event, type, category)

        elif type == "choose_tag":
            tag = data[2].split("=")[1]
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, tag: {tag}")
            return book.insert_or_delete_tag(event, tag)

        elif type == "begin_upload":
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return book.begin_upload(event)

        elif type == "upload":
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return book.upload_editting_book(event)

        else:
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return book.begin_edit(event, type)

    elif action == "act_info":

        current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
        return line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text_dict["Activity info"]),
            TextSendMessage(text_dict["Upload method"]), 
            TextSendMessage(text_dict["Find method"]), 
            TextSendMessage(text_dict["Invite and delete method"]), 
            TextSendMessage(text_dict["Activity warning"])
        ])

    elif action == "find_book":

        if models.book.has_accept_invitation(event.source.user_id):
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, Exception: Already have an accepted invitation")
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Finished"]))
        
        elif not models.book.has_book(event.source.user_id, True):
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, Exception: Don't have unblocked book")
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Null information"].format(field = "書籍")))

        elif type == "begin":
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return book.begin_find_book(event)

        elif type == "tags" or type == "categories":
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return book.begin_choose_tags_or_categories(event, type)

        elif type == "choose_tags" or type == "choose_categories":
            tmp = data[2].split("=")[1]
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, tag/category: {tmp}")
            return book.add_chosen_tags_or_categories(event, type, tmp)
        
        elif type == "find":
            return book.find_books(event)

        elif type == "next_page":
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return book.next_search(event)

        elif type == "show_book_detail":
            return book.show_book_detail(event, data[2].split("=")[1].split("+")[0], data[2].split("=")[1].split("+")[1])

        elif type == "my_book":
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            book.get_my_book(event)

        elif type == "random_find":
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return book.get_random_book(event)

    elif action == "delete":

        if models.book.has_accept_invitation(event.source.user_id):
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, Exception: Already have an accepted invitation")
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Finished so cannot delete"]))
 
        current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
        models.book.delete_book(data[2].split("=")[1].split("+")[0], data[2].split("=")[1].split("+")[1])
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Delete tag"].format(tag = "書籍")))

    elif action == "invite":

        if type == "my_invitation":
            return book.get_my_invitation(event, event.source.user_id)

        elif type == "next_page":
            current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
            return book.show_invitations(event, True)

        elif type == "invite":
            invitedID = data[2].split("=")[1].split("+")[0]
            invited_upload_time = data[2].split("=")[1].split("+")[1]
            my_book = models.book.get_newest_book(event.source.user_id)
            if models.book.has_accept_invitation(event.source.user_id):
                current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, Exception: Already have an accepted invitation")
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Finished"]))

            elif not models.book.is_not_blocked(invitedID, invited_upload_time):
                current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, Exception: The invited book is blocked")
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["The book is blocked"]))

            elif models.book.has_invitation(my_book[0], my_book[1], invitedID, invited_upload_time):
                current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, Exception: Duplicate invitation")
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Duplicate invitation"]))

            else:
                if models.book.is_not_blocked(my_book[0], my_book[1]):
                    models.book.insert_invitation(my_book[0], my_book[1], invitedID, invited_upload_time)
                    current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, {invitedID}, {invited_upload_time}")
                    return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Send invitation successfully"]))
                else:
                    current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, Exception: Don't have unblocked book")
                    return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Null information"].format(field = "書籍")))

        elif type == "accept":
            invitorID, invitor_upload_time = data[2].split("=")[1].split("+")
            my_book = models.book.get_newest_book(event.source.user_id)
            
            if models.book.has_accept_invitation(event.source.user_id):
                current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, Exception: Already have an accepted invitation")
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Finished"]))
            
            elif models.book.is_expired(invitorID, invitor_upload_time, my_book[0], my_book[1]):
                current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, Exception: Invitation expired")
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Too late"]))

            else:
                models.book.accept_invitation(invitorID, invitor_upload_time, my_book[0], my_book[1])
                current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}")
                return book.get_my_invitation(event, event.source.user_id)

        elif type == "deny":
            if models.book.has_accept_invitation(event.source.user_id):
                current_app.logger.info(f"[{datetime.now()}] Action: {action}, Type: {type}, ID: {event.source.user_id}, Exception: Already have an accepted invitation")
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Finished"]))

            invitorID, invitor_upload_time = data[2].split("=")[1].split("+")
            my_book = models.book.get_newest_book(event.source.user_id)
            if models.book.is_expired(invitorID, invitor_upload_time, my_book[0], my_book[1]):
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Deny"]))
            if models.book.deny_invitation(invitorID, invitor_upload_time, my_book[0], my_book[1]):
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Deny"]))

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
                models.user.update_user_profile(event.source.user_id, "department", department_dict[address[3:7]])
                return user.update_user_profile(event, "email", address)

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
        
        elif type == "photo":
            cache.pop(event.source.user_id, None)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Please upload a photo"]))

        else:
            return user.update_user_profile(event, type, event.message.text)

    elif action == "upload_book":
        return book.insert_or_update_book(event, type, event.message.text)

@handler.add(MessageEvent, message = ImageMessage)
def handle_image(event: MessageEvent):
    
    if cache.pop(event.source.user_id, None)[1] == "photo":
       return book.upload_photo(event)