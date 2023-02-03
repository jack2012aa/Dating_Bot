from models import database

def has_unexchanged_book(userID: str):
    '''Return whether user has an unexchanged book in table.'''

    cursor = database.cursor()
    cursor.execute(f"SELECT * FROM books WHERE userID = '{userID}' AND exchanged = 'F';")
    result = len(cursor.fetchall()) == 1
    cursor.close()
    return result