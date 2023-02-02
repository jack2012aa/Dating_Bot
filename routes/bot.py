'''Line messaging API. Can be used in different acitivity by changing handlers. '''

from flask import Blueprint, request
from services import line_message_handler
bot_bp = Blueprint("bot_bp", __name__)

@bot_bp.route("/bot", methods=["POST"])
def callback():
    line_message_handler.line_message_handler(request)
    return "OK"

