import os
import requests
import json

from flask import Flask, session, render_template, request, redirect, url_for, Markup, flash
from flask_session import Session
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from forms import RegistrationForm, LoginForm
from helpers import bcrypt, login_manager
from flask_login import login_user

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
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        username = form.username.data 
        email = form.email.data
        password = hashed_password
        db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)",
                {"username": username, "email": email, "password": password})
        db.commit()
        flash(f'Hey {form.username.data}, your account has been created! You are now able to login.', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.execute(
            "SELECT * FROM users WHERE email = :email",
            { "email": form.email.data }
        ).fetchone()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check your email or password', 'danger')
    return render_template("login.html", title='Login', form=form)

if __name__ == "__main__":
    app.run(debug=True)