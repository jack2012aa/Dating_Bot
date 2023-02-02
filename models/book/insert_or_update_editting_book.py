from models import database

def insert_or_update_editting_book(userID: str, field_type: str, field_value: str):
    '''Insert book information into table editting_books. If the user already has a editting book, update it information.'''

    cursor = database.cursor()
    cursor.execute(
        f"INSERT INTO editting_books (userID, {field_type}) \
         VALUES ('{userID}', '{field_value}') \
         ON DUPLICATE KEY UPDATE {field_type} = '{field_value}';"
    )
    database.commit()
    cursor.close()
    return