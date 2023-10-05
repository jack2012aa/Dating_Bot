import routes, models
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from logging.config import dictConfig

#Set logger config
log_config = {
    "version": 1,
    "formatters":{
        "simple":{
            "format": "[%(asctime)s] {%(filename)s %(lineno)d} %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers":{
        "fileHandler":{
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "mylog/log.txt",
            "when": "MIDNIGHT",
            "interval": 1,
            "formatter": "simple",
            "level": "DEBUG"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["fileHandler"]
    }
}
dictConfig(log_config)

app = Flask(__name__)

#Add route into app
routes.init_app(app)

#Define schedular to revert expired books
revert_scheduler = BackgroundScheduler()
def revert():
    models.database.ping(True)
    models.exchange_book.revert_books_and_invitations()
revert_scheduler.add_job(func = revert, trigger = "cron", hour = "0", minute = "0")
revert_scheduler.start()

if __name__ == "__main__":
    app.run()