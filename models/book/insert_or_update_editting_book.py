from models import database
from flask import current_app
from datetime import datetime

def insert_or_update_editting_book(userID: str, field: str, value: str):
    '''
    Insert book info into table 'editting_books'.
    If the user already has a editting book, update it information.
    '''

    sql = f"INSERT INTO editting_books (userID, {field}) VALUES ('{userID}', '{value}') ON DUPLICATE KEY UPDATE {field} = '{value}';"
    cursor = database.cursor()
    try:
        cursor.execute(sql)
        database.commit()
        cursor.close()
        current_app.logger.debug(f"[{datetime.now()}] Call: insert_or_update_editting_book({userID}, {field}, {value}), sql = {sql}")
        return True
    except:
        cursor.close()
        current_app.logger.error(f"[{datetime.now()}] SQL error. Call: insert_or_update_editting_book({userID}, {field}, {value}), sql = {sql}")
        return False