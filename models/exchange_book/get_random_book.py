from . import Book, get_book_tags
from models import database
from flask import current_app

def get_random_book(userID: str, gender: str, expect_gender: str):
    '''
    Get a random book for user. If no book exist return None.
    :param str gender: expect gender of the user.
    :param str expect_gender: gender of the user.
    '''

    database.ping(True)
    cursor = database.cursor()
    sql = f"SELECT DISTINCT a.userID, a.upload_time, a.name, a.summary, a.photo, a.category FROM books AS a JOIN friends AS b ON a.userID = b.userID WHERE a.blocked = 'F' AND a.userID != '{userID}' AND b.gender = '{gender}' AND b.expect_gender = '{expect_gender}' AND a.userID NOT IN (SELECT invitorID FROM invitations WHERE accept = 'T' AND invitedID = '{userID}') AND a.userID NOT IN (SELECT invitedID FROM invitations WHERE accept = 'T' AND invitorID = '{userID}') ORDER BY RAND() LIMIT 1;"

    try:
        current_app.logger.debug(f"userID: {userID}, gender: {gender}, expect_gender: {expect_gender}, sql: {sql}")
        cursor.execute(sql)
        book = cursor.fetchone()
        cursor.close()
        if book == None:
            return None
        tags = get_book_tags.get_book_tags(book[0], book[1])
        return Book(book[0], book[1], book[2], book[3], book[4], book[5], tags)
    
    except Exception as err:
        cursor.close()
        current_app.logger.error(f"{type(err)}, {str(err.args)}, userID: {userID}, gender: {gender}, expect_gender: {expect_gender}, sql: {sql}")
        return None