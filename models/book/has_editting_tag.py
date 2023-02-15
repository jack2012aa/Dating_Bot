from models import database
from flask import current_app
from datetime import datetime

def has_editting_tag(userID: str, tag: str):
    '''Return whether user has already chosen the tag'''

    cursor = database.cursor()
    sql = f"SELECT count(*) FROM editting_tags WHERE userID = '{userID}' AND tag = '{tag}';"
    cursor.execute(sql)
    exist = cursor.fetchone()[0] == 1
    cursor.close()
    current_app.logger.debug(f"[{datetime.now()}] Call: has_editting_tag({userID}, {tag}), sql = {sql}")
    return exist