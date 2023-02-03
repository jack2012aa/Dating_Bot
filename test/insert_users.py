import pymysql
import random
import json

with open("../setting.json") as json_file:
    config = json.load(json_file)

database = pymysql.connect(
    host = config["DATABASE_HOST"],
    user = config["USER"],
    password = config["PASSWORD"],
    database = config["DATABASE"]
)
cursor = database.cursor()

gender = ["男","女"]
for i in range(500):
    cursor.execute(
        f"INSERT INTO friends (userID, lineID, gender, expect_gender, birth_year, email) \
        VALUES ('{str(random.randint(1000, 99999999))}','{str(random.randint(1000, 9999))}','{gender[random.randint(0,1)]}','{gender[random.randint(0,1)]}','1999','{str(random.randint(1000, 99999999))}');")

cursor.close()
database.commit()