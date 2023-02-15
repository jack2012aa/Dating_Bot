from models import database

def get_all_tags():
    '''Return all tags defined in the database.'''
    
    cursor = database.cursor()
    cursor.execute("SELECT tag FROM tags ORDER BY sort ASC;")
    tags = list(map(lambda x: x[0], cursor.fetchall()))
    cursor.close()
    return tags