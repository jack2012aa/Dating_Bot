from models import database

def get_all_categories():
    '''Return all categories defined in the database.'''
    
    cursor = database.cursor()
    cursor.execute("SELECT category FROM categories;")
    categories = list(map(lambda x: x[0], cursor.fetchall()))
    cursor.close()
    return categories