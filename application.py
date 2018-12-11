import os
import requests
import json

from flask import Flask, session, render_template, request, redirect, url_for, Markup
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'SECRET_KEY'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
@app.route("/home")
def index():
    books = db.execute("SELECT isbn, title, author, year FROM books").fetchall()
    return render_template("index.html", title='Home', books=books)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    return render_template("register.html", title='Register', form=form)

@app.route("/login")
def login():
    form = LoginForm()
    return render_template("login.html", title='Login', form=form)

if __name__ == "__main__":
    app.run(debug=True)