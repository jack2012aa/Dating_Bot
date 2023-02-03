from models import database

def get_books(userID: str, gender: str, expect_gender: str, categories: list = None, tags: list = None):
    '''Return books' [name, photo, upload_time, userID] which fulfill all requirements'''
    
    if len(categories) == 0:
        categories_string = ""
    else:
        for i in range(len(categories)):
            categories[i] = "a.category = '" + categories[i] + "'"
        categories_string = "AND (" + " OR ".join(categories) + ")"

    if len(tags) == 0:
        tags_string = ""
    else:
        for i in range(len(tags)):
            tags[i] = "c.tag = '" + tags[i] + "'"
        tags_string = "AND (" + " OR ".join(tags) + ")"

    query_string = "SELECT DISTINCT a.name, a.photo, a.upload_time, a.userID FROM books AS a JOIN friends AS b ON a.userID = b.userID JOIN book_tags AS c ON a.userID = c.userID AND a.upload_time = c.upload_time WHERE a.exchanged = 'F' AND a.blocked = 'F' AND a.userID != '{userID}' AND b.gender = '{gender}' AND b.expect_gender = '{expect_gender}' {categories} {tags} GROUP BY a.name, a.photo, a.upload_time, a.userID ORDER BY count(*) DESC;"
    query_string = query_string.format(categories = categories_string, tags = tags_string, userID = userID, gender = gender, expect_gender = expect_gender)

    with database.cursor() as cursor:
        cursor.execute(query_string)
        result = list(cursor.fetchall())
    return result