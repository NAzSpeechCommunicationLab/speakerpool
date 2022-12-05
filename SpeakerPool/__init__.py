from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '379bdc5b2630afd64d21f03ca6e33e78'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/db/speakerpool.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from SpeakerPool import routes
