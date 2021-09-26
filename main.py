from fastapi import FastAPI,HTTPException 
from fastapi.params import Query,Body
import google_books
import sqlite3
from models import Book,Isbn
# from pydantic import BaseModel
# from typing import Optional

# class B(BaseModel):
#     b:Optional[str]

DATABASE_URL="./fastapi_sample.db"

app = FastAPI()


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str = None, b:B="text"):
#     return {"item_id": item_id, "q": q ,'b':b}

# @app.get("/books/{isbn}")
# def books(isbn:str):
#     book = google_books.get(isbn)
#     return{"books":book}

@app.get("/books")
def get_books_list():
    """本の一覧を取得する"""
    connect=sqlite3.connect(DATABASE_URL)
    c=connect.cursor()
    c.execute("select * from books")
    books=c.fetchall()
    result=[]
    for book in books:
        result.append(
             Book(
                id=book[0],
                title=book[1],
                authors=book[2],
                publishDate=book[3],
                description=book[4],
                stock=book[5],
                image=book[6],
                isbn=book[7],
            )
        )
    c.close()
    connect.close()
    return dict(result=result)

@app.get('/books/{id}')
def get_book_detail(id: int):
    # データベースへ接続
    connect = sqlite3.connect(DATABASE_URL)
    c = connect.cursor()
    c.execute('SELECT * FROM books where id = ?', (id,))
    book = c.fetchone()
    if not book:
        raise HTTPException(status_code=404, detail='本は見つかりませんでした')
    result = Book(
                id=book[0],
                title=book[1],
                authors=book[2],
                publishDate=book[3],
                description=book[4],
                stock=book[5],
                image=book[6],
                isbn=book[7],
            )
    c.close()
    connect.close()
    return dict(result=result) 

@app.post("/books")
def post_books(isbn:Isbn):
    book=google_books.get(isbn.id)
    book.isbn=isbn.id
    # SQLの変数として使うためにtuppleに加工する
    book_value = (
        None, book.title, book.authors, book.publishDate,
        book.description, book.stock, book.image, book.isbn
    )
    select_isbn=()
    select_isbn=book_value[7]
    # データベースへ接続
    connect = sqlite3.connect(DATABASE_URL)
    c = connect.cursor()
    # SQL文が長いので変数として作成
    c.execute("select id,stock from books where isbn = ?",(select_isbn,))
    have_id=[]
    have_id=c.fetchall()
    if have_id[0]==None:
        sql = 'INSERT INTO books(id,title,authors,publishDate,description,stock,image,isbn) VALUES(?,?,?,?,?,?,?,?)'
        # SQL実行
        c.execute(sql, book_value)
        # 書き込み結果を保存
        connect.commit()
        # 上記でDBに保存したレコードを取得する
        sql = 'SELECT * FROM books ORDER BY id DESC LIMIT 1'
        c.execute(sql)
        book_tuple = c.fetchone()
        # DBから取得したレコードをBookモデルのインスタンスに置き換える
        book = Book(
            id=book_tuple[0],
            title=book_tuple[1],
            authors=book_tuple[2],
            publishDate=book_tuple[3],
            description=book_tuple[4],
            stock=book_tuple[5],
            image=book_tuple[6],
            isbn=book_tuple[7],
        )
        # DB接続を切る
        c.close()
        connect.close()
    else:
        book_stock=have_id[0][1]+1
        book_id=have_id[0][0]
        c.execute('update books set stock=? where id=?',(book_stock,book_id))
        # 書き込み結果を保存
        connect.commit()
        # DB接続を切る
        c.close()
        connect.close()
    
    return dict(result=book)

@app.put("/books")
def put_book(book:Book):
    book_value = ( # book.id が後ろになっているので注意！
        book.title, book.authors, book.publishDate,
        book.description, book.stock, book.image, book.isbn, book.id
    )
    # データベースへ接続
    connect = sqlite3.connect(DATABASE_URL)
    c = connect.cursor()
    # SQL文が長いので変数として作成
    sql = 'UPDATE books SET title=?,authors=?,publishDate=?,description=?,stock=?,image=?,isbn=? WHERE id = ?'
    # SQL実行
    c.execute(sql, book_value)
    # 書き込み結果を保存
    connect.commit()
    # DB接続を切る
    c.close()
    connect.close()
    return dict(result=book)

@app.delete('/books')
def delete_book(book: Book):
    book_value = ( # book.id が後ろになっているので注意！
         book.id,
    )
    # データベースへ接続
    connect = sqlite3.connect(DATABASE_URL)
    c = connect.cursor()
    c.execute('select stock from books where id=?',book_value)
    select_stock=c.fetchone()
    select_stock=select_stock[0]
    if select_stock ==1:
        # SQL文が長いので変数として作成
        sql = 'DELETE from books WHERE id = ?'
        # SQL実行
        c.execute(sql, book_value)
        # 書き込み結果を保存
        connect.commit()
        # DB接続を切る
        c.close()
        connect.close()
        result = dict(detail='削除されました')
    else:
        print(select_stock)
        select_stock =select_stock - 1
        print(select_stock)
        c.execute('update books set stock=? where id=?',(select_stock,book_value[0]))
        # 書き込み結果を保存
        connect.commit()
        # DB接続を切る
        c.close()
        connect.close()
        result = dict(detail='在庫が一つ減りました。')

    return dict(result=result)
