from models import database

def insert_editting_tag(userID: str, tag: str):
    '''Insert user's tag into editting_tag table'''

    cursor = database.cursor()
    cursor.execute(f"INSERT INTO editting_tags (userID, tag) VALUES ('{userID}', '{tag}')")
    database.commit()
    cursor.close()
    return 0