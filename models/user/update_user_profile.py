from models import database
from flask import current_app

def update_user_profile(userID: str, field: str, value: str):
    '''
    Update existing user's profile in table friends. Return True if everything ok, else return False.
    :param str userID: line userID
    :param str field: "lineID", "gender", "expect_gender", "birth_year" or "email"
    :param str value: value to be inserted
    '''

    database.ping(True)
    cursor = database.cursor()
    sql = f"UPDATE friends SET {field} = '{value}' WHERE userID = '{userID}';"
    try:
        cursor.execute(sql)
        database.commit()
        cursor.close()
        current_app.logger.debug(f"userID: {userID}, profile_type: {field}, profile_value: {value}, sql: {sql}")
        return True
    except Exception as err:
        cursor.close()
        current_app.logger.error(f"{type(err)}, {str(err.args), userID: {userID}, profile_type: {field}, profile_value: {value}, sql: {sql}}")
        return False