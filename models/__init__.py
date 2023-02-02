import pymysql
import json

with open("setting.json") as json_file:
    config = json.load(json_file)

database = pymysql.connect(
    host = config["DATABASE_HOST"],
    user = config["USER"],
    password = config["PASSWORD"],
    database = config["DATABASE"]
)

from . import user, book
