from models import database

def insert_editting_tag(userID: str, tag: str):
    '''Insert user's tag into editting_tag table'''

    with database.cursor() as cursor:
        cursor.execute(f"INSERT INTO editting_tags (userID, tag) VALUES ('{userID}', '{tag}')")
        database.commit()
    return 0