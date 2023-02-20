import routes, models
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from logging.config import dictConfig

app = Flask(__name__)

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
    }
}
dictConfig(log_config)

#Add route into app
routes.init_app(app)

#Define schedular to revert expired books
revert_scheduler = BackgroundScheduler()
def revert():
    models.database.ping(True)
    models.book.revert_books_and_invitations()
revert_scheduler.add_job(func = revert, trigger = "cron", hour = "0", minute = "0")
revert_scheduler.start()

#Define schedular to reconnect database
reconnect_schedular = BackgroundScheduler()
reconnect_schedular.add_job(func = models.database.ping, trigger = "cron", args = [True], minute = "*/1")
reconnect_schedular.start()

if __name__ == "__main__":
    app.run()