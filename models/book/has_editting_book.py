from models import database
from flask import current_app
from datetime import datetime

def has_editting_book(userID: str):

    cursor = database.cursor()
    sql = f"SELECT count(*) FROM editting_books WHERE userID = '{userID}';"
    cursor.execute(sql)
    result = cursor.fetchone()[0] == 1
    cursor.close()
    
    return result