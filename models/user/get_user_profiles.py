from models import database
from flask import current_app

def get_user_profiles(userID: str, profile_types: list = ["userID"], all = False):
    '''

    Return profiles of user with userID in list.
    Return all fields if all = True.
    Return [None] if the field is NULL or something wrong happen.
    :param str userID: line userID
    :param list profile_types: an array of set of "userID", "lineID", "gender", "expect_gender", "birth_year", "email", "department", "join_date"
    :param bool all: select all columns
    '''

    database.ping(True)
    fields = ",".join(profile_types)
    cursor = database.cursor()
    if all:
        sql = f"SELECT * FROM friends WHERE userID = '{userID}';"
    else:
        sql = f"SELECT {fields} FROM friends WHERE userID = '{userID}';"
    try:
        cursor.execute(sql)
        result = list(cursor.fetchall()[0])
        cursor.close()
        current_app.logger.debug(f"userID: {userID}, profile_types: {str(profile_types)}, all: {str(all)}, sql: {sql}, result: {str(result)}")
        return result
    except Exception as err:
        current_app.logger.error(f"{type(err)}, {str(err.args)}, userID: {userID}, profile_types: {str(profile_types)}, all: {str(all)}, sql: {sql}")
        return [None]