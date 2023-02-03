from models import database

def delete_editting_tag(userID: str, tag: str):
    '''Delete user's tag in editting_tag table'''

    with database.cursor() as cursor:
        cursor.execute(f"DELETE FROM editting_tags WHERE userID = '{userID}' AND tag = '{tag}';")
        database.commit()
    return 0