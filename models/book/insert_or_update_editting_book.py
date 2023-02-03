from models import database

def insert_or_update_editting_book(userID: str, field: str, value: str):
    '''Insert book information into table editting_books. If the user already has a editting book, update it information.'''

    cursor = database.cursor()
    cursor.execute(
        f"INSERT INTO editting_books (userID, {field}) \
         VALUES ('{userID}', '{value}') \
         ON DUPLICATE KEY UPDATE {field} = '{value}';"
    )
    database.commit()
    cursor.close()
    return