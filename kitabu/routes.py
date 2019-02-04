import os, decimal
import secrets
import requests
from PIL import Image 
from sqlalchemy import or_, and_
from flask import session, render_template, request, redirect, url_for, Markup, flash, abort, jsonify
from kitabu import app, db, bcrypt
from kitabu.forms import RegistrationForm, LoginForm, UpdateAccountForm, SearchForm, ReviewForm
from kitabu.models import User, Review, Book
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        form = SearchForm()
        books = Book.query.all()
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        return render_template("home.html", title='Home', books=books, image_file=image_file, form=form)
    else:
        books = Book.query.all()
        return render_template("home.html", title='Home', books=books)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit() 
        flash(f'Hey {form.username.data}, your account has been created! You are now able to login.', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')  
            #user_name = current_user.username   
            flash('Hey {user_name}. You are now successfully logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check your email or password', 'danger')
    return render_template("login.html", title='Login', form=form)

#to update
@app.route("/", methods=['POST'])
@login_required
def search():
    """ Search for books based on user-supplied criteria """
    form = SearchForm()
    if form.validate_on_submit():
        search_key = request.form.get('search')
        book_query = Book.query
        search_query = book_query.filter(
            or_(
            Book.title.like(search_key),
            Book.author.like(search_key),
            Book.isbn.like(search_key)
            )
        ).all()

        books = search_query

        if not books:
            flash('Could not found that book, Sorry!', 'danger')
            return redirect(url_for('home'))
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        return render_template('home.html', books=books, image_file=image_file, form=form)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("account.html", title='Account', image_file=image_file, form=form)


@app.route("/books/<int:book_id>", methods=['GET', 'POST'])
@login_required
def book(book_id):
    """List details about a single Book."""
    if current_user.is_authenticated:
        # Making sure book exists.
        form = ReviewForm()
        book = Book.query.get(book_id)
        reviews = Review.query.filter(
            Review.book_id.like(book_id)
            ).all()
        rating = request.form.get("rating")
        if form.validate_on_submit():
            review = Review(title=form.title.data, content=form.content.data, author=current_user, book_id=book_id, rating=rating)
            db.session.add(review)
            db.session.commit()
            flash('Your review has been submited!', 'success')
            return redirect(url_for('book', book_id=book.id))
        
        goodreads = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Pan0ciQ093frutnmdDvug", "isbns": book.isbn})
        g_ratings = goodreads.json()["books"][0]["average_rating"]
        g_rating_counts = goodreads.json()["books"][0]["work_ratings_count"]
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        return render_template("book.html", title='Book detail', book=book, reviews=reviews, g_rating_counts=g_rating_counts, g_ratings=g_ratings, image_file=image_file, form=form)


@app.route("/books/<int:book_id>/reviews/<int:review_id>")
@login_required
def review(book_id, review_id):
    book = Book.query.get(book_id)
    review = Review.query.get_or_404(review_id)
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('review.html', title=review.title, review=review, book=book, image_file=image_file)


@app.route("/books/<int:book_id>/reviews/<int:review_id>/update", methods=['GET', 'POST'])
@login_required
def update_review(book_id, review_id):
    book = Book.query.get(book_id)
    review = Review.query.get_or_404(review_id)
    if review.author != current_user:
        abort(403)
    form = ReviewForm()
    if form.validate_on_submit():
        review.title = form.title.data 
        review.content = form.content.data
        db.session.commit()
        flash('Your review has been updated!', 'success')
        return redirect(url_for('book', book_id=book.id))
    elif request.method == 'GET':
        form.title.data = review.title
        form.content.data = review.content
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("create_review.html", title='Update Review', image_file=image_file, 
                            form=form, legend='Update Review')


@app.route("/books/<int:book_id>/reviews/<int:review_id>/delete", methods=['POST'])
@login_required
def delete_review(book_id, review_id):
    book = Book.query.get(book_id)
    review = Review.query.get_or_404(review_id)
    if review.author != current_user:
        abort(403)
    db.session.delete(review)
    db.session.commit()
    flash('Your review has been deleted!', 'success')
    return redirect(url_for('book', book_id=book.id))

@app.route("/api/<string:isbn>")
def api(isbn):
    book_isbn = Book.query.get(isbn)
    book = Book.query.filter(
            Book.isbn.like(isbn)
            ).first()
    #book = db.execute("SELECT * FROM books WHERE isbn = :q", {"q": isbn}).fetchone()
    
    if book is None:
        return jsonify({"error": "Invalid ISBN"}), 404

    reviews = Review.query.filter(
            Review.isbn.like(isbn)
            ).all()
    #reviews = db.execute("SELECT * FROM reviews WHERE book_id = :q1", {"q1": isbn}).fetchall()
    response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Pan0ciQ093frutnmdDvug", "isbns": isbn})
    data = response.json()['books'][0]
    
    return jsonify({
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "review_count": data['reviews_count'],
        "average_rating": data['average_rating']
    })



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

