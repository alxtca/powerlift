from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
# is someone that is not logged in try to access page that require to be logged in
# that unknown user will be send to login page/function.
login.login_view = 'login'


# app package is folder named app
from app import routes, models