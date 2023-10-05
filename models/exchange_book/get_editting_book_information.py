from models import database
from flask import current_app
from datetime import datetime

def get_editting_book_information(userID: str, fields = [], all = False):
    '''
    Return information of editting book of user in list.
    Return all fields if all == True.
    Return [None] if the field is NULL.
    '''

    fields = ",".join(fields)
    cursor = database.cursor()
    if all:
        sql = f"SELECT * FROM editting_books WHERE userID = '{userID}';"
    else:
        sql = f"SELECT {fields} FROM editting_books WHERE userID = '{userID}';"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    
    if len(result) == 0:
        return [None]
    return list(result[0])