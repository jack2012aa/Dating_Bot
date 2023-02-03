from models import database

def has_empty_column(userID: str):
    '''Return whether user's editting book has a empty column(s).'''

    with database.cursor() as cursor:
        cursor.execute(f"SELECT * FROM editting_books WHERE userID = '{userID}' AND name IS NOT NULL AND summary IS NOT NULL AND photo IS NOT NULL AND exchange_method IS NOT NULL AND category IS NOT NULL;")
        result = len(cursor.fetchall()) == 0
    return result