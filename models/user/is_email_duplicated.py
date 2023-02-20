from models import database

def is_email_duplicated(email: str):
    '''Check whether the email address is in the table.'''

    database.ping(True)
    cursor = database.cursor()
    cursor.execute(f"SELECT * FROM friends WHERE email = '{email}';")
    result = len(cursor.fetchall()) == 1
    cursor.close()

    return result