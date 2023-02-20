from models import database
from flask import current_app
from datetime import datetime

def has_empty_column(userID: str):
    '''Return whether user's editting book has a empty column(s).'''

    cursor = database.cursor()
    sql = f"SELECT count(*) FROM editting_books WHERE userID = '{userID}' AND name IS NOT NULL AND summary IS NOT NULL AND photo IS NOT NULL AND category IS NOT NULL;"
    cursor.execute(sql)
    result = cursor.fetchone()[0] == 0
    cursor.close()
    
    return result