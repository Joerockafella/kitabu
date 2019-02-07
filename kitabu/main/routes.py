import requests
from flask import render_template, request, Blueprint, redirect, url_for, flash, jsonify
from kitabu.models import Book, Review
from flask_login import current_user, login_required
from kitabu.main.forms import SearchForm
from kitabu.reviews.forms import ReviewForm
from kitabu import db
from sqlalchemy import or_


main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    if current_user.is_authenticated:
        form = SearchForm()
        page = request.args.get('page', 1, type=int)
        books = Book.query.paginate(page=page, per_page=16)
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        return render_template("home.html", title='Home', books=books, image_file=image_file, form=form)
    else:
        page = request.args.get('page', 1, type=int)
        books = Book.query.paginate(page=page, per_page=16)
        return render_template("home.html", title='Home', books=books)


# to update
@main.route("/home", methods=['POST'])
@main.route("/", methods=['POST'])
@login_required
def search():
    """ Search for books """
    form = SearchForm()
    if form.validate_on_submit():
        #page = request.args.get('page', 1, type=int)
        search_key = request.form.get('search')
        #book_query = Book.query
        search_query = Book.query.filter(
            or_(
                Book.title.like(search_key),
                Book.author.like(search_key),
                Book.isbn.like(search_key)
            )
        )
        book_results = search_query.all()
        #paginate = Book.query.paginate(page=page, per_page=16)
        if not book_results:
            flash('Could not found that book, Sorry!', 'danger')
            return redirect(url_for('main.home'))
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        return render_template('home.html', book_results=book_results, image_file=image_file, form=form)


@main.route("/books/<int:book_id>", methods=['GET', 'POST'])
@login_required
def book(book_id):
    """List details about a single Book."""
    if current_user.is_authenticated:
        form = ReviewForm()
        book = Book.query.get(book_id)
        reviews = Review.query.filter(
            Review.book_id.like(book_id)
        ).order_by(Review.date_posted.desc()).all()
        review_count = Review.query.filter(
            Review.book_id.like(book_id)
        ).count()
        # TODO: still need to update rate_count and average
        rating_count_query = Review.query.filter_by(rating=Review.rating) \
            .filter(
            Review.book_id.like(book_id)
        )
        rating_count = rating_count_query.count()
        rating = request.form.get("rating")
        if form.validate_on_submit():
            review = Review(title=form.title.data, content=form.content.data, author=current_user, book_id=book_id,
                            rating=rating)
            db.session.add(review)
            db.session.commit()
            flash('Your review has been submited!', 'success')
            return redirect(url_for('main.book', book_id=book.id))

        goodreads = requests.get("https://www.goodreads.com/book/review_counts.json",
                                 params={"key": "Pan0ciQ093frutnmdDvug", "isbns": book.isbn})
        g_ratings = goodreads.json()["books"][0]["average_rating"]
        g_rating_counts = goodreads.json()["books"][0]["work_ratings_count"]
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        return render_template("book.html", title='Book detail', book=book, rating_count=rating_count, reviews=reviews,
                               review_count=review_count, g_rating_counts=g_rating_counts, g_ratings=g_ratings,
                               image_file=image_file, form=form)


@main.route("/api/<string:isbn>", methods=["GET"])
def api(isbn):

    book = Book.query.filter(
        Book.isbn.like(isbn)
    ).first()

    if book is None:
        return jsonify({"error": "Invalid ISBN"}), 404

    response = requests.get("https://www.goodreads.com/book/review_counts.json",
                            params={"key": "Pan0ciQ093frutnmdDvug", "isbns": book.isbn})
    data = response.json()['books'][0]

    return jsonify({
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "review_count": data['reviews_count'],
        "average_rating": data['average_rating']
    })

