from models import database

def is_profile_finished(userID: str):
    '''Return whether all user profile is filled in.'''

    cursor = database.cursor()
    cursor.execute(
        f"SELECT * \
         FROM friends \
         WHERE userID = '{userID}' AND lineID IS NOT NULL AND gender IS NOT NULL AND expect_gender IS NOT NULL AND birth_year IS NOT NULL AND email IS NOT NULL;"
    )
    result = len(cursor.fetchall()) == 1
    cursor.close()

    return result