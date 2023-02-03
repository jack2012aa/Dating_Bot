from models import database

def get_user_profiles(userID: str, profile_types = ["userID"], all = False):
    '''
    Return profiles of user with userID in list.
    Return all fields if all == True.
    Return [None] if the field is NULL.
    '''

    fields = ",".join(profile_types)
    cursor = database.cursor()
    if all:
        cursor.execute(f"SELECT * FROM friends WHERE userID = '{userID}';")
    else:
        cursor.execute(f"SELECT {fields} FROM friends WHERE userID = '{userID}';")
    result = cursor.fetchall()
    cursor.close()
    return list(result[0])