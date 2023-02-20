from models import database
from flask import current_app
from datetime import datetime

def is_profile_finished(userID: str):
    '''Return whether all user profile is filled in.'''

    sql = f"SELECT * FROM friends WHERE userID = '{userID}' AND lineID IS NOT NULL AND gender IS NOT NULL AND expect_gender IS NOT NULL AND birth_year IS NOT NULL AND email IS NOT NULL;"
    
    database.ping(True)
    cursor = database.cursor()
    try:
        cursor.execute(sql)
        result = len(cursor.fetchall()) == 1
        cursor.close()
        
        return result
    except:
        
        cursor.close()
        return False