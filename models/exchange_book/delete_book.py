from models import database
from flask import current_app

def delete_book(userID: str, upload_time: str):
    '''Block the book and expire all related invitations'''

    database.ping(True)
    cursor = database.cursor()
    sql = f"CALL delete_book('{userID}', '{upload_time}');"

    try:
        cursor.execute(sql)
        database.commit()
        cursor.close()
        current_app.logger.debug(f"userID: {userID}, upload_time: {upload_time}, sql: {sql}")
        return True
    except Exception as err:
        cursor.close()
        current_app.logger.error(f"{type(err)}, {str(err.args)}, userID: {userID}, upload_time: {upload_time}, sql: {sql}")
        return False