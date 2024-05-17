from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from datetime import timedelta

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

CORS_ALLOW_ORIGIN="*,*"
CORS_EXPOSE_HEADERS="*,*,Set-Cookie"

CORS_ALLOW_HEADERS="content-type,*"
cors = CORS(app, origins=CORS_ALLOW_ORIGIN.split(","), allow_headers=CORS_ALLOW_HEADERS.split(",") , expose_headers= CORS_EXPOSE_HEADERS.split(","),   supports_credentials = True)

# Configure session cookie settings
app.config['SESSION_COOKIE_SAMESITE'] = 'None' 
#app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' 
#app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_COOKIE_SECURE'] = True

app.config['REMEMBER_COOKIE_SAMESITE'] = 'None'
#app.config['REMEMBER_COOKIE_SAMESITE'] = 'Lax' 
#app.config['REMEMBER_COOKIE_SAMESITE'] = 'Strict'
app.config['REMEMBER_COOKIE_SECURE'] = True


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///3DAssets.db'
app.config['SECRET_KEY'] = 'secret'  # Add this line
app.config["CORS_SUPPORTS_CREDENTIALS"] = True
app.config['REMEMBER_COOKIE_DURATION'] = 10 * 365 * 24 * 60 * 60  # 10 years in seconds


db = SQLAlchemy(app)


