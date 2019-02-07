import os

class Config:
    SECRET_KEY = 'bcbb1632ad8f2ee65b1cb34d0cb54b69'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///kitabu.db'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'joe.onlineblog@gmail.com'
    MAIL_PASSWORD = '10405BERLIN'

    #os.environ.get('KITABU_SECRET_KEY')
    #os.environ.get('KITABU_DATABASE')
    #os.environ.get('E_USER')
    #os.environ.get('E_PASS')