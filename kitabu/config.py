import os

class Config:
    SECRET_KEY = os.environ.get('KITABU_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('KITABU_DATABASE', 'DATABASE_URL')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('E_USER')
    MAIL_PASSWORD = os.environ.get('E_PASS')
