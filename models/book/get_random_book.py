from models import database
from flask import current_app
from datetime import datetime

def get_random_book(userID: str, gender: str, expect_gender: str):
    '''
    Get a random book for user. If no book exist return None.
    :param str gender: expect gender of the user.
    :param str expect_gender: gender of the user.
    '''

    sql = f"SELECT DISTINCT a.photo, a.name, a.category, a.userID, a.upload_time FROM books AS a JOIN friends AS b ON a.userID = b.userID WHERE a.blocked = 'F' AND a.userID != '{userID}' AND b.gender = '{gender}' AND b.expect_gender = '{expect_gender}' AND a.userID NOT IN (SELECT invitorID FROM invitations WHERE accept = 'T' AND invitedID = '{userID}') AND a.userID NOT IN (SELECT invitedID FROM invitations WHERE accept = 'T' AND invitorID = '{userID}') ORDER BY RAND() LIMIT 1;"
    try:
        cursor = database.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        if result == None:
            return None
        result = list(result)
        cursor.close()
        
        return result
    except Exception as err:
        cursor.close()
        
        return None