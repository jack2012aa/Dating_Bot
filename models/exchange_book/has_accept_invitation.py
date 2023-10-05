from models import database
from flask import current_app

def has_accept_invitation(userID: str):
    '''Whether user has an today-accepted invitation.'''

    database.ping(True)
    sql = f"SELECT * FROM invitations WHERE (invitedID = '{userID}' OR invitorID = '{userID}') AND accept = 'T' AND DATE(checked_time) = current_date;"
    cursor = database.cursor()
    try:
        cursor.execute(sql)
        result = len(cursor.fetchall()) == 1
        cursor.close()
        current_app.logger.debug(f"userID: {userID}, sql: {sql}")
        return result
    except Exception as err:
        cursor.close()
        current_app.logger.error(f"{type(err)}, {str(err.args)}, userID: {userID}, sql: {sql}")
        return False