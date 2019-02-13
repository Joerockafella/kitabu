from flask import render_template, request, redirect, url_for, flash, abort, Blueprint
from kitabu import db
from kitabu.reviews.forms import ReviewForm
from kitabu.models import Review, Book
from flask_login import current_user, login_required


reviews = Blueprint('reviews', __name__)


@reviews.route("/books/<int:book_id>/reviews/<int:review_id>")
@login_required
def review(book_id, review_id):
    book = Book.query.get(book_id)
    review = Review.query.get_or_404(review_id)
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('review.html', title=review.title, review=review, book=book, image_file=image_file)


@reviews.route("/books/<int:book_id>/reviews/<int:review_id>/update", methods=['GET', 'POST'])
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
        return redirect(url_for('main.book', book_id=book.id))
    elif request.method == 'GET':
        form.title.data = review.title
        form.content.data = review.content
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("update_review.html", title='Update Review', image_file=image_file,
                            form=form, legend='Update Review')


@reviews.route("/books/<int:book_id>/reviews/<int:review_id>/delete", methods=['POST'])
@login_required
def delete_review(book_id, review_id):
    book = Book.query.get(book_id)
    review = Review.query.get_or_404(review_id)
    if review.author != current_user:
        abort(403)
    db.session.delete(review)
    db.session.commit()
    flash('Your review has been deleted!', 'success')
    return redirect(url_for('main.book', book_id=book.id))
