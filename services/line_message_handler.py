from flask import abort, current_app
from linebot import (LineBotApi, WebhookHandler)
from linebot.models import TextSendMessage, FollowEvent, PostbackEvent, MessageEvent, TextMessage, ImageMessage
from linebot.exceptions import (InvalidSignatureError)
from . import config, user
import models

'''
Handle all line events and log them.
'''

#Declare line objects
line_bot_api = LineBotApi(config["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(config["CHANNEL_SECRET"])

cache = {} 
'''Dict for membering user status. Format: [Action, Type, [Data]]'''

def line_message_handler(request):
    '''
    A simple line message handler. Return "OK" if the signature is correct.
    :param Request request: A http request.
    '''
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text = True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError as err:
        current_app.logger.error(f"{type(err)}, {err.message}")
        abort(400)
    
    return "OK"

@handler.add(FollowEvent)
def handle_new_follower(event: FollowEvent):
    '''Show welcome messages and insert user into database.'''

    current_app.logger.info(f"action: follow, type: follow, user: {event.source.user_id}")
    return line_bot_api.reply_message(event.reply_token, user.add_new_user(event.source.user_id))

@handler.add(PostbackEvent)
def handle_postback(event: PostbackEvent):
    '''Postback events are triggerred by different buttons. Reply these events'''

    data = event.postback.data.split("&")
    '''Format: "action=action&type=type&data=data"'''
    action = data[0].split("=")[1]
    type = data[1].split("=")[1]

    if action == "edit_profile":

        if type == "begin_modify":
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
            return line_bot_api.reply_message(event.reply_token, user.begin_modify())

        elif type == "begin_gender" or type == "begin_expect_gender":
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
            return line_bot_api.reply_message(event.reply_token, user.begin_edit_gender(event.source.user_id, type))

        elif type == "choose_gender":
            field = data[2].split("=")[1]
            value = data[3].split("=")[1]
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, field: {field}, value: {value}")
            return line_bot_api.reply_message(event.reply_token, user.edit_user_profile(event.source.user_id, field, value))
        
        elif type in ["begin_birth_year", "begin_email", "begin_lineID"]:
            cache[event.source.user_id] = [action, type[5:]]
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
            return line_bot_api.reply_message(event.reply_token, user.begin_edit_string_field(event.source.user_id, type))

    elif action == "teaching":
        current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
        return line_bot_api.reply_message(event.reply_token, user.teaching())

    elif action == "contact_us":
        current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
        return line_bot_api.reply_message(event.reply_token, user.contact())

    elif action == "upload_book":

        if not models.user.is_profile_finished(event.source.user_id):
            
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Profile not finished"]))

        elif models.book.has_book(event.source.user_id, True):
            
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Already have book"]))

        elif models.book.has_accept_invitation(event.source.user_id):
            
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Finished"]))

        elif type == "begin":
            
            return book.begin_edit_book(event)

        elif type == "photo":
            
            return book.begin_edit_photo(event)
        
        elif type == "category" or type == "tag":
            
            return book.begin_edit_tag_or_category(event, type)

        elif type == "choose_category":
            category = data[2].split("=")[1]
            
            return book.insert_or_update_book(event, type, category)

        elif type == "choose_tag":
            tag = data[2].split("=")[1]
            
            return book.insert_or_delete_tag(event, tag)

        elif type == "begin_upload":
            
            return book.begin_upload(event)

        elif type == "upload":
            
            return book.upload_editting_book(event)

        else:
            
            return book.begin_edit(event, type)

    elif action == "act_info":

        
        return line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text_dict["Activity info"]),
            TextSendMessage(text_dict["Upload method"]), 
            TextSendMessage(text_dict["Find method"]), 
            TextSendMessage(text_dict["Invite and delete method"]), 
            TextSendMessage(text_dict["Activity warning"])
        ])

    elif action == "find_book":

        if models.book.has_accept_invitation(event.source.user_id):
            
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Finished"]))
        
        elif not models.book.has_book(event.source.user_id, True):
            
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Null information"].format(field = "書籍")))

        elif type == "begin":
            
            return book.begin_find_book(event)

        elif type == "tags" or type == "categories":
            
            return book.begin_choose_tags_or_categories(event, type)

        elif type == "choose_tags" or type == "choose_categories":
            tmp = data[2].split("=")[1]
            
            return book.add_chosen_tags_or_categories(event, type, tmp)
        
        elif type == "find":
            return book.find_books(event)

        elif type == "next_page":
            
            return book.next_search(event)

        elif type == "show_book_detail":
            return book.show_book_detail(event, data[2].split("=")[1].split("+")[0], data[2].split("=")[1].split("+")[1])

        elif type == "my_book":
            
            book.get_my_book(event)

        elif type == "random_find":
            
            return book.get_random_book(event)

    elif action == "delete":

        if models.book.has_accept_invitation(event.source.user_id):
            
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Finished so cannot delete"]))
 
        
        models.book.delete_book(data[2].split("=")[1].split("+")[0], data[2].split("=")[1].split("+")[1])
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Delete tag"].format(tag = "書籍")))

    elif action == "invite":

        if type == "my_invitation":
            return book.get_my_invitation(event, event.source.user_id)

        elif type == "next_page":
            
            return book.show_invitations(event, True)

        elif type == "invite":
            invitedID = data[2].split("=")[1].split("+")[0]
            invited_upload_time = data[2].split("=")[1].split("+")[1]
            my_book = models.book.get_newest_book(event.source.user_id)
            if models.book.has_accept_invitation(event.source.user_id):
                
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Finished"]))

            elif not models.book.is_not_blocked(invitedID, invited_upload_time):
                
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["The book is blocked"]))

            elif models.book.has_invitation(my_book[0], my_book[1], invitedID, invited_upload_time):
                
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Duplicate invitation"]))

            else:
                if models.book.is_not_blocked(my_book[0], my_book[1]):
                    models.book.insert_invitation(my_book[0], my_book[1], invitedID, invited_upload_time)
                    
                    return line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Send invitation successfully"]))
                else:
                    
                    return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Null information"].format(field = "書籍")))

        elif type == "accept":
            invitorID, invitor_upload_time = data[2].split("=")[1].split("+")
            my_book = models.book.get_newest_book(event.source.user_id)
            
            if models.book.has_accept_invitation(event.source.user_id):
                
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Finished"]))
            
            elif models.book.is_expired(invitorID, invitor_upload_time, my_book[0], my_book[1]):
                
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text_dict["Too late"]))

            else:
                models.book.accept_invitation(invitorID, invitor_upload_time, my_book[0], my_book[1])
                
                return book.get_my_invitation(event, event.source.user_id)

        elif type == "deny":
            if models.book.has_accept_invitation(event.source.user_id):
                
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
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, email: {event.message.text}")
            message, valid, code = user.send_verifying_email(event.message.text)
            if not valid:
                cache.pop(event.source.user_id, None)
                return line_bot_api.reply_message(event.reply_token, message)
            else:
                cache[event.source.user_id] = ["edit_profile", "verify_email", code, event.message.text]
                return line_bot_api.reply_message(event.reply_token, message)
        
        elif type == "verify_email":
            code = cache.get(event.source.user_id)[2]
            email = cache.get(event.source.user_id)[3]
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, code: {code}, email: {event.message.text}, entered_code: {event.message.text}")
            message, correct = user.verify_email(event.source.user_id, code, event.message.text, email)
            if not correct:
                return line_bot_api.reply_message(event.reply_token, message)
            else:
                cache.pop(event.source.user_id, None)
                return line_bot_api.reply_message(event.reply_token, message)

        elif type == "birth_year":
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, birth_year: {event.message.text}")
            message, valid = user.edit_birth_year(event.source.user_id, event.message.text)
            if not valid:
                return line_bot_api.reply_message(event.reply_token, message)
            else:
                cache.pop(event.source.user_id, None)
                return line_bot_api.reply_message(event.reply_token, message)

        elif type == "lineID":
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, lineID: {event.message.text}")
            cache.pop(event.source.user_id, None)
            return user.edit_lineID(event.source.user_id, event.message.text)

    elif action == "upload_book":
        return book.insert_or_update_book(event, type, event.message.text)

@handler.add(MessageEvent, message = ImageMessage)
def handle_image(event: MessageEvent):
    
    if cache.pop(event.source.user_id, None)[1] == "photo":
       return book.upload_photo(event)