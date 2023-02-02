from .image import image_bp
from .bot import bot_bp
import json

with open("setting.json") as json_file:
    config = json.load(json_file)

def init_app(app):
    app.register_blueprint(image_bp)
    app.register_blueprint(bot_bp)