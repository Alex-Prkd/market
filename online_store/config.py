import os


class Config:
    DEBUG = True
    SECRET_KEY = 'SADPSADasdl343salSL'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    RECAPTCHA_PUBLIC_KEY = '6Ld47gEhAAAAAJF4uM99oHVN3cuPkOZTchgg9IPb'
    RECAPTCHA_PRIVATE_KEY = '6Ld47gEhAAAAAJTC2x6n9zbSQyGqYtsDl6v0lLV5'
    FLASK_ADMIN_SWATCH = 'cerulean'
    COOKIE_SECRET_KEY = 'YtsDl6v0F4uM99oHVN3cuPkOZTchgg9I'


