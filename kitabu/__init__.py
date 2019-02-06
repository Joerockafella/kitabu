from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_script import Manager 
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail
from kitabu.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
migrate = Migrate(db)
manager = Manager()
migrate_command = MigrateCommand

mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app)

    mail.init_app(app)

    from kitabu.users.routes import users
    from kitabu.reviews.routes import reviews
    from kitabu.main.routes import main
    app.register_blueprint(users)
    app.register_blueprint(reviews)
    app.register_blueprint(main)


    return app