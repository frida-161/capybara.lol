import os

# Path where the Plugins are stored
CAPYBARA_PATH = os.getenv('CAPYBARA_PATH', '/upload')
# Secret key for the app
SECRET_KEY = os.getenv('SECRET_KEY','notasecret')

#DB Config
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI',
    'sqlite:////capybara.db')