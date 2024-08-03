import os
import sqlalchemy
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import calendar
from sqlalchemy import func, case, cast, Time
from decimal import Decimal
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from babel.dates import format_datetime
from datetime import datetime, timedelta, time
from functools import wraps


UPLOAD_FOLDER = "app/static/uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('SQLALCHEMY_DATABASE_URL', 'mysql+pymysql://usuario:password@endereco/banco')
app.config["SECRET_KEY"] = "secretkey"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 28000,
    'pool_pre_ping': True
}
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

from app.models.models import *
from app.functions.functions import *
from app.routes.index import *
from app.routes.avarias import *
from app.routes.entregas import *
from app.routes.vencimentos import *
from app.routes.vendas import *
from app.routes.adm import *