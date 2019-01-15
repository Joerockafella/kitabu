import os
import csv

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from kitabu import db
from kitabu.models import Book


def main():
    f=open("books.csv")
    reader =csv.reader(f)
    for isbn, title, author, year in reader:
        if year == "year":
            print('skipped first line')
        else:
            books = Book(isbn=isbn, title=title, author=author, year=year)
            db.session.add(books)
            db.session.commit()
    print('done')        

if __name__ == "__main__":
    main()