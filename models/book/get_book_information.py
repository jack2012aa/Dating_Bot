from models import database
from flask import current_app

def get_book_information(userID: str, upload_time: str = None, fields = [], all = False):
    '''
    Return information of book of user in list.
    Return all fields (name, summary, photo, category) if all == True.
    Return [None] if the field is NULL.
    '''

    cursor = database.cursor()
    if all:
        sql = f"SELECT name, summary, photo, category FROM books WHERE userID = '{userID}' AND upload_time = '{upload_time}';"
    else:
        fields = ",".join(fields)
        sql = f"SELECT {fields} FROM books WHERE userID = '{userID}' AND upload_time = '{upload_time}';"
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    
    if result == None:
        return [None]
    return list(result)