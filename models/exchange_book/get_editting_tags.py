from models import database
from flask import current_app
from datetime import datetime

def get_editting_tags(userID: str):
    '''Return editting tags of user in list. If no tags exist return [None]'''

    cursor = database.cursor()
    sql = f"SELECT tag FROM editting_tags WHERE userID = '{userID}';"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    result = list(map(lambda x: x[0], result))
    
    if len(result) == 0:
        return [None]
    return result