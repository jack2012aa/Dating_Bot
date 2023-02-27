from flask import abort, current_app
from linebot import (LineBotApi, WebhookHandler)
from linebot.models import FollowEvent, PostbackEvent, MessageEvent, TextMessage, ImageMessage
from linebot.exceptions import (InvalidSignatureError)
from . import config, user_actions_manager, upload_book_actions_manager

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
    return line_bot_api.reply_message(event.reply_token, user_actions_manager.add_new_user(event.source.user_id))

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
            return line_bot_api.reply_message(event.reply_token, user_actions_manager.begin_modify(event.source.user_id))

        elif type == "begin_gender" or type == "begin_expect_gender":
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
            return line_bot_api.reply_message(event.reply_token, user_actions_manager.begin_edit_gender(event.source.user_id, type))

        elif type == "choose_gender":
            field = data[2].split("=")[1]
            value = data[3].split("=")[1]
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, field: {field}, value: {value}")
            return line_bot_api.reply_message(event.reply_token, user_actions_manager.edit_user_profile(event.source.user_id, field, value))
        
        elif type in ["begin_birth_year", "begin_email", "begin_lineID"]:
            cache[event.source.user_id] = [action, type[6:]]
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
            return line_bot_api.reply_message(event.reply_token, user_actions_manager.begin_edit_string_field(event.source.user_id, type))

        elif type == "begin_edit_all":
            cache
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
            return line_bot_api.reply_message(event.reply_token, user_actions_manager.begin_edit_all(event.source.user_id))

        elif type == "continuous_setting_gender":
            gender = data[2].split("=")[1]
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, gender: {gender}")
            messages, valid = user_actions_manager.continuous_setting_gender(event.source.user_id, gender)
            return line_bot_api.reply_message(event.reply_token, messages)

        elif type == "continuous_setting_expect_gender":
            expect_gender = data[2].split("=")[1]
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, expect_gender: {expect_gender}")
            messages, valid = user_actions_manager.continuous_setting_expect_gender(event.source.user_id, expect_gender)
            if valid:
                cache[event.source.user_id] = [action, "continuous_setting_lineID"]
            return line_bot_api.reply_message(event.reply_token, messages)

        elif type == "skip":
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
            user_cache = cache.get(event.source.user_id, None)
            if user_cache != None:
                type = user_cache[1]

                #if the user should set lineID originally, skip it and begin set birth_year
                if type == "continuous_setting_lineID":
                    cache[event.source.user_id] = [action, "continuous_setting_birth_year"]
                    return line_bot_api.reply_message(event.reply_token, user_actions_manager.continuous_setting_lineID(event.source.user_id, "skip")[0])

                #if the user should set birth_year originally, skip it and begin set email
                if type == "continuous_setting_birth_year":
                    cache[event.source.user_id] = [action, "continuous_setting_email"]
                    return line_bot_api.reply_message(event.reply_token, user_actions_manager.continuous_setting_birth_year(event.source.user_id, "skip")[0])

    elif action == "upload_book":

        message, valid = upload_book_actions_manager.is_valid(event.source.user_id)
        if not valid:
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
            return line_bot_api.reply_message(event.reply_token, message)

        if type == "begin":
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
            return line_bot_api.reply_message(event.reply_token, upload_book_actions_manager.choose_what_to_edit(event.source.user_id))
        
        elif type in ["begin_edit_category","begin_edit_tag"]:
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
            return line_bot_api.reply_message(event.reply_token, upload_book_actions_manager.begin_edit(event.source.user_id, type, False))
        
        elif type in ["begin_edit_name","begin_edit_summary","begin_edit_photo"]:
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
            cache[event.source.user_id] = [action, type[6:]]
            return line_bot_api.reply_message(event.reply_token, upload_book_actions_manager.begin_edit(event.source.user_id, type, False))

        elif type == "edit_category":
            category = data[2].split("=")[1]
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, category: {category}")
            message, valid = upload_book_actions_manager.edit_category(event.source.user_id, category)
            if not valid:
                return line_bot_api.reply_message(event.reply_token, message + upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_category", False))
            #Check whether it is in continuous edit mode
            status = cache.get(event.source.user_id, None)
            if status != None and status[1] == "edit_category_continuously":
                return line_bot_api.reply_message(event.reply_token, message + upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_tag", True))
            return line_bot_api.reply_message(event.reply_token, message)

        elif type == "edit_tag":
            tag = data[2].split("=")[1]
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, tag: {tag}")
            message, valid = upload_book_actions_manager.edit_tag(event.source.user_id, tag)
            return line_bot_api.reply_message(event.reply_token, message + upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_tag", False))

        elif type == "begin_edit_all":
            #begin from edit name
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
            cache[event.source.user_id] = [action, "edit_name_continuously"]
            return line_bot_api.reply_message(event.reply_token, upload_book_actions_manager.get_continuous_edit_order() + upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_name", True))

        elif type == "skip":

            #Get present status in cache
            status = cache.get(event.source.user_id, None)
            if status == None:
                return
            present = status[1]
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, present: {present}")

            #Skip present status and move to next step
            if present == "edit_name_continuously":
                cache[event.source.user_id] = [action, "edit_summary_continuously"]
                return line_bot_api.reply_message(event.reply_token, upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_summary", True))

            elif present == "edit_summary_continuously":
                cache[event.source.user_id] = [action, "edit_photo_continuously"]
                return line_bot_api.reply_message(event.reply_token, upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_photo", True))
            
            elif present == "edit_photo_continuously":
                cache[event.source.user_id] = [action, "edit_category_continuously"]
                return line_bot_api.reply_message(event.reply_token, upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_category", True))

            elif present == "edit_category_continuously":
                cache.pop(event.source.user_id, None)
                return line_bot_api.reply_message(event.reply_token, upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_tag", True))

        elif type == "finish":
            return line_bot_api.reply_message(event.reply_token, upload_book_actions_manager.finish())

        elif type == "begin_upload":
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
            return line_bot_api.reply_message(event.reply_token, upload_book_actions_manager.begin_upload(event.source.user_id))

        elif type == "upload":
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
            return line_bot_api.reply_message(event.reply_token, upload_book_actions_manager.upload(event.source.user_id)[0])

    elif action == "act_info":

        current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")

        if type == "act_info":
            return line_bot_api.reply_message(event.reply_token, upload_book_actions_manager.act_info())

        elif type == "upload_book":
            return line_bot_api.reply_message(event.reply_token, upload_book_actions_manager.how_to_upload())

        elif type in ["how_to_edit_name","how_to_edit_summary","how_to_edit_photo","how_to_edit_category","how_to_edit_tag"]:
            return line_bot_api.reply_message(event.reply_token, upload_book_actions_manager.how_to_edit(type))
        
    elif action == "teaching":

        current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")

        if type == "teaching":
            return line_bot_api.reply_message(event.reply_token, user_actions_manager.teaching())

        elif type == "contract":
            return line_bot_api.reply_message(event.reply_token, user_actions_manager.contract())
        
        elif type in ["lineID", "gender", "birth_year", "email"]:
            return line_bot_api.reply_message(event.reply_token, user_actions_manager.teach(type))

    elif action == "contact_us":
        current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
        return line_bot_api.reply_message(event.reply_token, user_actions_manager.contact())

    elif action == "cancel":
        cache.pop(event.source.user_id, None)
        current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}")
        return line_bot_api.reply_message(event.reply_token, user_actions_manager.cancel())
    
@handler.add(MessageEvent, message = TextMessage)
def handle_text_message(event: MessageEvent):
    '''Handle message used for editting'''

    status = cache.get(event.source.user_id, None)
    if status == None:
        return
    action = status[0]
    type = status[1]
    
    if action == "edit_profile":
        
        if type == "email":
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, email: {event.message.text}")
            message, valid, code = user_actions_manager.send_verifying_email(event.message.text)
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
            message, correct = user_actions_manager.verify_email(event.source.user_id, code, event.message.text, email)
            if not correct:
                return line_bot_api.reply_message(event.reply_token, message)
            else:
                cache.pop(event.source.user_id, None)
                return line_bot_api.reply_message(event.reply_token, message)

        elif type == "birth_year":
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, birth_year: {event.message.text}")
            message, valid = user_actions_manager.edit_birth_year(event.source.user_id, event.message.text)
            if not valid:
                return line_bot_api.reply_message(event.reply_token, message)
            else:
                cache.pop(event.source.user_id, None)
                return line_bot_api.reply_message(event.reply_token, message)

        elif type == "lineID":
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, lineID: {event.message.text}")
            cache.pop(event.source.user_id, None)
            return line_bot_api.reply_message(event.reply_token, user_actions_manager.edit_lineID(event.source.user_id, event.message.text))

        elif type == "continuous_setting_lineID":
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, lineID: {event.message.text}")
            message, valid = user_actions_manager.continuous_setting_lineID(event.source.user_id, event.message.text)
            if valid:
                cache[event.source.user_id] = [action, "continuous_setting_birth_year"]
            return line_bot_api.reply_message(event.reply_token, message)

        elif type == "continuous_setting_birth_year":
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, birth_year: {event.message.text}")
            message, valid = user_actions_manager.continuous_setting_birth_year(event.source.user_id, event.message.text)
            if valid:
                cache[event.source.user_id] = [action, "continuous_setting_email"]
            return line_bot_api.reply_message(event.reply_token, message)

        elif type == "continuous_setting_email":
            current_app.logger.info(f"action: {action}, type: {type}, user: {event.source.user_id}, email: {event.message.text}")
            message, valid, code = user_actions_manager.send_verifying_email(event.message.text)
            if not valid:
                message = user_actions_manager.append_repeat_message(message)
            else:
                cache[event.source.user_id] = ["edit_profile", "verify_email", code, event.message.text]
            return line_bot_api.reply_message(event.reply_token, message)

    elif action == "upload_book":

        if type == "edit_name":
            current_app.logger.info(f"action:{action}, type:{type}, user: {event.source.user_id}, name: {event.message.text}")
            message, valid = upload_book_actions_manager.edit_name(event.source.user_id, event.message.text)
            if not valid:
                return line_bot_api.reply_message(event.reply_token, message + upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_name", False))
            cache.pop(event.source.user_id, None)
            return line_bot_api.reply_message(event.reply_token, message)
        
        elif type == "edit_name_continuously":
            current_app.logger.info(f"action:{action}, type:{type}, user: {event.source.user_id}, name: {event.message.text}")
            message, valid = upload_book_actions_manager.edit_name(event.source.user_id, event.message.text)
            if not valid:
                return line_bot_api.reply_message(event.reply_token, message + upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_name", False))
            #Turn to edit summary
            cache[event.source.user_id] = [action, "edit_summary_continuously"]
            return line_bot_api.reply_message(event.reply_token, message + upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_summary", True))

        elif type == "edit_summary":
            current_app.logger.info(f"action:{action}, type:{type}, user: {event.source.user_id}, name: {event.message.text}")
            message, valid = upload_book_actions_manager.edit_summary(event.source.user_id, event.message.text)
            if not valid:
                return line_bot_api.reply_message(event.reply_token, message + upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_summary", False))
            cache.pop(event.source.user_id, None)
            return line_bot_api.reply_message(event.reply_token, message)

        elif type == "edit_summary_continuously":
            current_app.logger.info(f"action:{action}, type:{type}, user: {event.source.user_id}, name: {event.message.text}")
            message, valid = upload_book_actions_manager.edit_summary(event.source.user_id, event.message.text)
            if not valid:
                return line_bot_api.reply_message(event.reply_token, message + upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_summary", False))
            #Turn to edit photo
            cache[event.source.user_id] = [action, "edit_photo_continuously"]
            return line_bot_api.reply_message(event.reply_token, message + upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_photo", True))

@handler.add(MessageEvent, message = ImageMessage)
def handle_image(event: MessageEvent):
    
    status = cache.get(event.source.user_id, None)
    if status == None:
        return
    action = status[0]
    type = status[1]

    if action == "upload_book":

        if type == "edit_photo":
            current_app.logger.info(f"action:{action}, type:{type}, user: {event.source.user_id}")
            message, valid = upload_book_actions_manager.edit_photo(event.source.user_id, line_bot_api.get_message_content(event.message.id))
            if not valid:
                return line_bot_api.reply_message(event.reply_token, message + upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_photo", False))
            cache.pop(event.source.user_id, None)
            return line_bot_api.reply_message(event.reply_token, message)

        elif type == "edit_photo_continuously":
            current_app.logger.info(f"action:{action}, type:{type}, user: {event.source.user_id}")
            message, valid = upload_book_actions_manager.edit_photo(event.source.user_id, line_bot_api.get_message_content(event.message.id))
            if not valid:
                return line_bot_api.reply_message(event.reply_token, message + upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_photo", False))
            #Turn to edit category
            cache[event.source.user_id] = [action, "edit_category_continuously"]
            return line_bot_api.reply_message(event.reply_token, message + upload_book_actions_manager.begin_edit(event.source.user_id, "begin_edit_category", True))