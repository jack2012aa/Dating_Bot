from . import Book, get_book_tags
from models import database
from flask import current_app

def find_books(userID: str, gender: str, expect_gender: str, categories: list = None, tags: list = None):
    '''
    Return books which fulfill all requirements. If no book exists return None.
    :param str userID: line user id
    :param str gender: user's expect_gender
    :param str expect_gender: user's gender
    :param list categories: search fields
    :param list tags: search fields
    :return Book object
    '''
    
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

    sql = "SELECT DISTINCT a.photo, a.name, a.category, a.userID, a.upload_time, a.summary FROM books AS a JOIN friends AS b ON a.userID = b.userID JOIN book_tags AS c ON a.userID = c.userID AND a.upload_time = c.upload_time WHERE a.blocked = 'F' AND a.userID != '{userID}' AND b.gender = '{gender}' AND b.expect_gender = '{expect_gender}' AND a.userID NOT IN (SELECT invitorID FROM invitations WHERE accept = 'T' AND invitedID = '{userID}') AND a.userID NOT IN (SELECT invitedID FROM invitations WHERE accept = 'T' AND invitorID = '{userID}') {categories} {tags} GROUP BY a.name, a.photo, a.upload_time, a.userID, a.category ORDER BY count(*) DESC;"
    sql = sql.format(categories = categories_string, tags = tags_string, userID = userID, gender = gender, expect_gender = expect_gender)
    
    database.ping(True)
    cursor = database.cursor()
    try:
        cursor.execute(sql)
        current_app.logger.debug(f"userID: {userID}, gender: {gender}, expect_gender: {expect_gender}, categories: {categories}, tags: {tags}, sql: {sql}")
        books = cursor.fetchall()
        result = []
        if len(books) == 0:
            cursor.close()
            return None
        for i in range(len(books)):
            tags = get_book_tags.get_book_tags(books[i][3], books[i][4])
            result.append(Book(books[i][3], books[i][4], books[i][1], books[i][5], books[i][0], books[i][2], tags))
        cursor.close()
        return result
        
    except Exception as err:
        current_app.logger.error(f"{type(err)}, {str(err.args)}, userID: {userID}, gender: {gender}, expect_gender: {expect_gender}, categories: {categories}, tags: {tags}, sql: {sql}")
        cursor.close()
        return False