import boto3, json

with open("setting.json") as json_file:
    config = json.load(json_file)

class Book:
    '''Define what is a book in database.'''

    def __init__(self, userID: str, upload_time: str, name: str, summary: str, photo: str, category: str, tags: list):
        self._USERID = userID
        self._UPLOAD_TIME = upload_time
        self._NAME = name
        self._SUMMARY = summary
        self._PHOTO = photo
        self._CATEGORY = category
        if type(tags) == str:
            self._TAGS = tags.split("、")
        self._TAGS = tags

    def __str__(self):

        return f"{self.USERID},{self.UPLOAD_TIME},{self.NAME},{self.SUMMARY},{self.PHOTO},{self.CATEGORY},{self.TAGS}"

    @property
    def USERID(self):
        return self._USERID

    @property
    def UPLOAD_TIME(self):
        return self._UPLOAD_TIME

    @property
    def NAME(self):
        return self._NAME

    @property
    def SUMMARY(self):
        return self._SUMMARY

    @property
    def PHOTO(self):
        return self._PHOTO

    @property
    def CATEGORY(self):
        return self._CATEGORY

    @property
    def TAGS(self):
        return self._TAGS

    def get_photo_url(self):
        '''
        Return a S3 url.
        '''
        s3 = boto3.client("s3", aws_access_key_id = config["aws_access_key_id"], aws_secret_access_key = config["aws_secret_access_key"])
        url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": self.PHOTO})
        return url

    def get_tags_string(self):
        '''
        Return tags seperated by comma. If no tags return empty string.
        '''

        if self.TAGS[0] != None or self.TAGS[0] != '':
            return "、".join(self.TAGS)
        else:
            return ""

    def serialize(self):
        '''
        Return a serialize string. Must be deserialized by models.exchange_book.get_book().
        '''

        return f"{self.USERID}%%%{self.UPLOAD_TIME}"

from . import find_books, get_exchanged_book_and_lineID, has_book, insert_or_update_editting_book, get_editting_book_information, get_all_categories, get_all_tags, get_editting_tags, has_editting_tag, is_not_blocked
from . import insert_editting_tag, delete_editting_tag, has_empty_column, upload_book, has_editting_book, get_book_tags, get_book_information, insert_invitation, has_invitation, get_all_invitations, has_accept_invitation, accept_invitation, get_newest_book, is_expired, deny_invitation, delete_book, exist_book, revert_books_and_invitations, get_random_book, get_book

insert_or_update_editting_book = insert_or_update_editting_book.insert_or_update_editting_book
has_book = has_book.has_book
get_editting_book_information = get_editting_book_information.get_editting_book_information
get_all_categories= get_all_categories.get_all_categories
get_all_tags = get_all_tags.get_all_tags
get_editting_tags = get_editting_tags.get_editting_tags
has_editting_tag = has_editting_tag.has_editting_tag
insert_editting_tag = insert_editting_tag.insert_editting_tag
delete_editting_tag = delete_editting_tag.delete_editting_tag
has_empty_column = has_empty_column.has_empty_column
upload_book = upload_book.upload_book
has_editting_book = has_editting_book.has_editting_book
find_books = find_books.find_books
get_book_tags = get_book_tags.get_book_tags
get_book_information = get_book_information.get_book_information
insert_invitation = insert_invitation.insert_invitation
has_invitation = has_invitation.has_invitation
get_all_invitations = get_all_invitations.get_all_invitations
has_accept_invitation = has_accept_invitation.has_accept_invitation
get_exchanged_book_and_lineID = get_exchanged_book_and_lineID.get_exchanged_book_and_lineID
accept_invitation = accept_invitation.accept_invitation
get_newest_book = get_newest_book.get_newest_book
is_expired = is_expired.is_expired
deny_invitation = deny_invitation.deny_invitation
delete_book = delete_book.delete_book
exist_book = exist_book.exist_book
is_not_blocked = is_not_blocked.is_not_blocked
revert_books_and_invitations = revert_books_and_invitations.revert_books_and_invitations
get_random_book = get_random_book.get_random_book
get_book = get_book.get_book