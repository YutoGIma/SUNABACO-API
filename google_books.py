import requests
import json
from models import Book

# def get(isbn):
#     url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}'.format(isbn)
#     response = requests.get(url)
#     data = json.loads(response.text)
#     try:
#         data = dict(
#             title = data['items'][0]['volumeInfo']['title'],
#             authors = ','.join(data['items'][0]['volumeInfo']['authors']),
#             publishDate = data['items'][0]['volumeInfo']['publishedDate'],
#             description = data['items'][0]['volumeInfo']['description'],
#             thumbnail=data['items'][0]['volumeInfo']['imageLinks']['thumbnail']
#         )
#     except:
#         data = dict(detail='指定されたISBNの本は見つかりませんでした')
#     return data

# APIつくる2日目 モデルを使う
def get(isbn: str) -> Book:
    url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}'.format(isbn)
    response = requests.get(url)
    data = json.loads(response.text)
    
    # title が tupleになっている時があるので判定する
    title = data['items'][0]['volumeInfo']['title']
    if type(title) is tuple:
        title = data['items'][0]['volumeInfo']['title'][0]

    try:
        # 問題として複数見つかった場合は最初のものしか取得しないバグになっている
        book = Book(
            title = title,
            authors = ','.join(data['items'][0]['volumeInfo']['authors']),
            publishDate = data['items'][0]['volumeInfo']['publishedDate'],
            description = data['items'][0]['volumeInfo']['description'],
            image = data['items'][0]['volumeInfo']['imageLinks']['thumbnail']
        )
    except:
        book =  None
    return book