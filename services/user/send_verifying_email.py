import models
from services import line_bot_api, text_dict, cache, config, cancel_quick_reply_button
from linebot.models import MessageEvent, TextSendMessage, QuickReply
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import random

def send_verifying_email(event: MessageEvent):
    '''
    Get email address in the event.
    If it is duplicated or isn't an ntu mail, return error message.
    If it isn't, send a verifying email with verifying code to the address.
    '''

    address = event.message.text
    duplicated = models.user.is_email_duplicated(address)
    if duplicated:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Repeat email"]))
        cache.pop(event.source.user_id)
        return 0
    elif address.split("@")[1] != "ntu.edu.tw" or len(address.split("@")[0]) != 9:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Improper email"]))  
        cache.pop(event.source.user_id)
        return 0
    else:
        code = send_email(address)
        cache[event.source.user_id] = ["edit_profile", "verify_email", code, address]
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text_dict["Input verifying code"].format(email = address), quick_reply = QuickReply([cancel_quick_reply_button])))

def send_email(recipient: str):
    '''Send a email with verifying code to new updated emails and return the verifying code.'''

    content = MIMEMultipart()
    content["subject"] = text_dict["Verifying email title"]
    content["from"] = config["DOMAIN_MAIL_ACCOUNT"]
    content["to"] = recipient
    verifying_code = str(random.randint(100000, 999999))
    content.attach(MIMEText(text_dict["Verifying email content"].format(code = verifying_code)))
    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(config["DOMAIN_MAIL_ACCOUNT"], config["DOMAIN_MAIL_PASSWORD"])
            smtp.send_message(content)
        except Exception as e:
            print("Errpr message: ", e)

    return verifying_code