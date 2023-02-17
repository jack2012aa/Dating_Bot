from models import database
from flask import current_app
from datetime import datetime

def get_books(userID: str, gender: str, expect_gender: str, categories: list = None, tags: list = None):
    '''Return books' [photo, name, category, userID, upload_time] which fulfill all requirements. If no book exists return None'''
    
    if len(categories) == 0:
        categories_string = ""
    else:
        for i in range(len(categories)):
            categories[i] = "a.category = '" + categories[i] + "'"
        categories_string = "AND (" + " OR ".join(categories) + ")"

    if len(tags) == 0:
        tags_string = ""
    else:
        for i in range(len(tags)):
            tags[i] = "c.tag = '" + tags[i] + "'"
        tags_string = "AND (" + " OR ".join(tags) + ")"

    sql = "SELECT DISTINCT a.photo, a.name, a.category, a.userID, a.upload_time FROM books AS a JOIN friends AS b ON a.userID = b.userID JOIN book_tags AS c ON a.userID = c.userID AND a.upload_time = c.upload_time WHERE a.blocked = 'F' AND a.userID != '{userID}' AND b.gender = '{gender}' AND b.expect_gender = '{expect_gender}' AND a.userID NOT IN (SELECT invitorID FROM invitations WHERE accept = 'T' AND invitedID = '{userID}') AND a.userID NOT IN (SELECT invitedID FROM invitations WHERE accept = 'T' AND invitorID = '{userID}') {categories_string} {tags_string} GROUP BY a.name, a.photo, a.upload_time, a.userID, a.category ORDER BY count(*) DESC;"
    sql = sql.format(categories = categories_string, tags = tags_string, userID = userID, gender = gender, expect_gender = expect_gender)
    current_app.logger.debug(f"[{datetime.now()}] Call: get_books({userID}, {gender}, {expect_gender}, {categories}, {tags}), sql = {sql}")

    try:
        cursor = database.cursor()
        cursor.execute(sql)
        tmp = list(cursor.fetchall())
        result = []
        for i in range(len(tmp)):
            result.append(list(tmp[i]))
        cursor.close()
        if len(result) == 0:
            return None
        return result
    except Exception as err:
        current_app.logger.error(f"[{datetime.now()}] SQL error. Call: get_books({userID}, {gender}, {expect_gender}, {categories}, {tags}),sql = {sql}, {type(err), {str(err.args)}}")
        cursor.close()
        return False