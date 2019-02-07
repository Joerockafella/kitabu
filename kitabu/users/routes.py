from flask import render_template, request, redirect, url_for, flash, Blueprint
from kitabu import db, bcrypt
from kitabu.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from kitabu.main.forms import SearchForm
from kitabu.models import User, Review, Book
from flask_login import login_user, current_user, logout_user, login_required
from kitabu.users.utils import save_picture, send_reset_email


users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('users.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Hey {form.username.data}, your account has been created! You are now able to login.', 'success')
        return redirect(url_for('users.login'))
    return render_template("register.html", title='Register', form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome {current_user.username}! You are now successfully logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check your email or password', 'danger')
    return render_template("login.html", title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
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
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("account.html", title='Account', image_file=image_file, form=form)


@users.route("/books/<int:book_id>/users/<string:username>")
@login_required
def user_reviews(username, book_id):
    if current_user.is_authenticated:
        #to verify this form
        form = SearchForm()
        book = Book.query.get(book_id)
        user = User.query.filter_by(username=username).first_or_404()
        reviews = Review.query.filter_by(author=user) \
            .filter(
            Review.book_id.like(book_id)
        ).order_by(Review.date_posted.desc()).all()

        user_reviews_count = Review.query.filter_by(author=user) \
            .filter(
            Review.book_id.like(book_id)
        ).order_by(Review.date_posted.desc()).count()

        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        return render_template("user_reviews.html", reviews=reviews, user=user, book=book,
                               user_reviews_count=user_reviews_count, image_file=image_file, form=form)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    #if current_user.is_authenticated:
        #return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    if current_user.is_authenticated:
        logout_user()
        #image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        return render_template('reset_request.html', title='Reset Password', form=form)
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('This is an invalid or expired token', 'danger')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated! You are now able to login.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

