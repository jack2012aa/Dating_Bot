from models import database

def get_book_tags(userID: str, upload_time: str):
    '''Return all tags of the book. If it doesn't have tag return None'''

    with database.cursor() as cursor:
        cursor.execute(f"SELECT tag FROM book_tags WHERE userID = '{userID}' AND upload_time = '{upload_time}';")
        tags = list(map(lambda x: x[0], cursor.fetchall()))
    if len(tags) == 0:
        return None
    else:
        return tags