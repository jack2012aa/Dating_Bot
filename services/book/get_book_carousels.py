import boto3
from services import config, text_dict
from linebot.models import CarouselColumn, CarouselTemplate, PostbackTemplateAction

def get_book_carousels(books: list, invite: bool):
    '''
    Return a line carousel template containing at most 10 books and remain books.
    :param list books: a list contain books' [photo, name, category, userID, upload_time, tags]
    :param bool invite: if true, carousel will have a button to send invitation, else it will have accept and deny buttons for accept and deny invitations.
    '''

    books_carouel = []
    if invite:
        for i in range(min(10, len(books))):
            book = books.pop(0)
            if book[5] != None:
                tags_string = " ".join(book[5])
            else:
                tags_string = "無"
            s3 = boto3.client("s3", aws_access_key_id = config["aws_access_key_id"], aws_secret_access_key = config["aws_secret_access_key"])
            url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": book[0]})
            books_carouel.append(
                CarouselColumn(
                    thumbnail_image_url = url,
                    title = book[1],
                    text = "分類：" + book[2] + "\n標籤：" + tags_string,
                    actions = [
                        PostbackTemplateAction(label = text_dict["More"], data = f"action=find_book&type=show_book_detail&data={book[3]}+{book[4]}", display_text = text_dict["More"]),
                        PostbackTemplateAction(label = text_dict["Send invitation"], data = f"action=invite&type=invite&data={book[3]}+{book[4]}", display_text = text_dict["Send invitation"])
                        ]
                )
            )
    else:
        for i in range(min(10, len(books))):
            book = books.pop(0)
            if book[5] != None:
                    tags_string = " ".join(book[5])
            else:
                tags_string = "無"
            s3 = boto3.client("s3", aws_access_key_id = config["aws_access_key_id"], aws_secret_access_key = config["aws_secret_access_key"])
            url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": book[0]})
            books_carouel.append(
                CarouselColumn(
                    thumbnail_image_url = url,
                    title = book[1],
                    text = "分類：" + book[2] + "\n標籤：" + tags_string,
                    actions = [
                        PostbackTemplateAction(label = text_dict["More"], data = f"action=find_book&type=show_book_detail&data={book[3]}+{book[4]}", display_text = text_dict["More"]),
                        PostbackTemplateAction(label = text_dict["Accept invitation"], data = f"action=invite&type=accept&data={book[3]}+{book[4]}", display_text = text_dict["Accept invitation"]),
                        PostbackTemplateAction(label = text_dict["Deny invitation"], data = f"action=invite&type=deny&data={book[3]}+{book[4]}", display_text = text_dict["Deny invitation"])
                    ]
                )
            )
    print(len(books_carouel))
    return CarouselTemplate(columns = books_carouel), books