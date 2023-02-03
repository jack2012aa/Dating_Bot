from models import database

def has_editting_tag(userID: str, tag: str):
    '''Return whether user has already chosen the tag'''

    with database.cursor() as cursor:
        cursor.execute(f"SELECT * FROM editting_tags WHERE userID = '{userID}' AND tag = '{tag}';")
        exist = len(cursor.fetchall()) == 1
    return exist