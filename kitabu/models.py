from datetime import datetime
from kitabu import db, login_manager, manager, migrate, migrate_command, app
from flask_login import UserMixin

manager.add_command('db', migrate_command)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Automatically creates a table wth the name 'user' small letter
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    user_reviews = db.relationship('Review', backref='author', lazy=True)

    def __repr__(self):
            return f"User('{self.username}', '{self.email}', '{self.image_file}' )" #this is what will be printed

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rating = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)

    def __repr__(self):
            return f"Review('{self.title}', '{self.date_posted}', '{self.rating}' )" 

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer)
    book_reviews = db.relationship('Review', lazy=True)


    def __repr__(self):
        return f"Book('{self.isbn}', '{self.title}', '{self.author}', '{self.year}', '{self.book_reviews}' )" 

