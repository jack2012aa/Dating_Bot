from models import database

def has_editting_book(userID: str):

    with database.cursor() as cursor:
        cursor.execute(f"SELECT * FROM editting_books WHERE userID = '{userID}';")
        result = len(cursor.fetchall()) == 1
    return result