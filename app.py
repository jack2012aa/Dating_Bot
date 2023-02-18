from flask import Flask
from logging import FileHandler, StreamHandler
import routes
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import models

app = Flask(__name__)
app.logger.addHandler(FileHandler("log.txt"))
app.logger.addHandler(StreamHandler())
app.logger.setLevel(logging.DEBUG)
routes.init_app(app)

scheduler = BackgroundScheduler()
scheduler.add_job(func = models.book.revert_books_and_invitations, trigger = "cron", hour = "0", minute = "0")
scheduler.start()


if __name__ == "__main__":
    app.run()