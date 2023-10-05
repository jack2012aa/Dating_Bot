from models import database
from flask import current_app

def has_book(userID: str, unblocked: bool = True):
    '''
    Return whether user has a book in table 'books'.
    :param bool unblocked: If true, only search for unblocked book.
    '''

    sql = "SELECT * FROM books WHERE userID = '{userID}' {blocked};"

    if unblocked:
        blocked = "AND blocked = 'F'"
    else:
        blocked = ""

    sql = sql.format(userID = userID, blocked = blocked)

    database.ping(True)
    cursor = database.cursor()
    try:
        cursor.execute(sql)
        result = len(cursor.fetchall()) != 0
        cursor.close()
        current_app.logger.debug(f"userID: {userID}, unblocked: {unblocked}, sql: {sql}")
        return result
    except Exception as err:
        cursor.close()
        current_app.logger.info(f"{type(err)}, {str(err.args)}, userID: {userID}, unblocked: {unblocked}, sql: {sql}")
        return False