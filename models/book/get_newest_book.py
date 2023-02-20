from models import database
from flask import current_app
from datetime import datetime

def get_newest_book(userID: str):
    '''Return user's newest book.[userID, upload_time], ignoring blocked'''

    cursor = database.cursor()
    sql = f"SELECT upload_time FROM books WHERE userID = '{userID}' ORDER BY upload_time DESC LIMIT 1;"
    cursor.execute(sql)
    result = [userID, cursor.fetchone()[0]]
    cursor.close()
    
    return result