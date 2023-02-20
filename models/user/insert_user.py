from models import database
from flask import current_app

def insert_user(userID: str):
    '''
    Insert user with user id = userID into table friends. Ignoring whether the user is already exist or not.
    '''

    database.ping(True)
    cursor = database.cursor()
    sql = f"INSERT INTO friends (userID) VALUES ('{userID}');"
    try:
        cursor.execute(sql)
        database.commit()
        cursor.close()
    except:
        cursor.close()
    current_app.logger.debug(f"userID: {str}, sql: {sql}")
    return True