from models import database

def update_user_profile(userID: str, profile_type: str, profile_value: str):
    '''Update existing user's profile in table friends.'''

    cursor = database.cursor()
    cursor.execute(f"UPDATE friends SET {profile_type} = '{profile_value}' WHERE userID = '{userID}';")
    database.commit()
    cursor.close()
    return