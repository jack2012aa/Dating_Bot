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
cursor.execute("SELECT userID FROM friends ORDER BY userID ASC LIMIT 40;")
userIDs = list(map(lambda x: x[0],cursor.fetchall()))
cursor.close()

'''
categories = ["傳記","小說","工具書","教科書","散文","漫畫","童書","詩詞戲曲","週刊雜誌"]
cursor = database.cursor()
for user in userIDs:
    cursor.execute(f"INSERT INTO books (userID, name, summary, photo, exchange_method, category) VALUES \
        ('{user}', '{str(random.randint(1000,9999))}', '{str(random.randint(1000,9999))}', '1675159214.479361.jpeg', '面交', '{categories[random.randint(0,8)]}');")
database.commit()
cursor.close()
'''

cursor = database.cursor()
cursor.execute("SELECT userID, upload_time FROM books ORDER BY userID ASC LIMIT 41;")
books = list(map(lambda x: [x[0],x[1]],cursor.fetchall()))
cursor.close()

cursor = database.cursor()
for book in books:
    tags = ["偵探","其它","外文","愛情","抒情治癒勵志","投資理財","烹飪手作","社會/心理學","科學","科幻","經典","藝文影劇"]
    for i in range(random.randint(1,4)):
        cursor.execute(f"INSERT INTO book_tags (userID, upload_time, tag) VALUES \
            ('{book[0]}','{book[1]}','{tags.pop(random.randint(0,len(tags)-1))}');")
database.commit()
cursor.close()
