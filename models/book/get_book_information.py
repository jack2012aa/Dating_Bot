from models import database

def get_book_information(userID: str, upload_time: str, fields: list):

    with database.cursor() as cursor:
        fields = ",".join(fields)
        cursor.execute(f"SELECT {fields} FROM books WHERE userID = '{userID}' AND upload_time = '{upload_time}';")
        result = list(cursor.fetchall()[0])
    
    if len(result) == 0:
        return None
    return result