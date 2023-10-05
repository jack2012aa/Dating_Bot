from models import database

def revert_books_and_invitations():
    '''Revert books and invitations expired last day'''

    try:
        database.ping(True)
        cursor = database.cursor()
        cursor.execute("UPDATE books SET blocked = 'F' WHERE (userID, upload_time) IN (SELECT userID, upload_time FROM revert_books_list);")
        cursor.execute("UPDATE invitations SET expired = 'F' WHERE (invitorID, invitor_upload_time, invitedID, invited_upload_time) IN (SELECT invitorID, invitor_upload_time, invitedID, invited_upload_time FROM revert_invitations_list);")
        cursor.execute("DELETE FROM revert_books_list;")
        cursor.execute("DELETE FROM revert_invitations_list;")
        database.commit()
        cursor.close()
        return True
    except Exception as err:
        print(err)
        cursor.close()
        return False