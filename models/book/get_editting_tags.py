from models import database

def get_editting_tags(userID: str):
    '''Return editting tags of user in list'''

    with database.cursor() as cursor:
        cursor.execute(f"SELECT tag FROM editting_tags WHERE userID = '{userID}';")
        result = cursor.fetchall()
        if len(result) == 0:
            return [None]
        tags = list(map(lambda x: x[0], result))
    return tags