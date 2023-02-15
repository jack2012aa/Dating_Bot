from models import database

def insert_user(userID: str):
    '''Insert user with user id = userID into table friends'''

    cursor = database.cursor()
    cursor.execute(f"INSERT INTO friends (userID) VALUES ('{userID}');")
    database.commit()
    cursor.close()
    return