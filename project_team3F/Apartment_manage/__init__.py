# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager
# import cloudinary
#
# db = SQLAlchemy()
# login = LoginManager()
#
#
# def create_app():
#     app = Flask(__name__, template_folder="templates")
#     app.secret_key = '&(^&*^&*^U*HJBJKHJLHKJHK&*%^&5786985646858'
#
#     app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost/chungcudb?charset=utf8mb4"
#     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
#
#     db.init_app(app)
#     login.init_app(app)
#     login.login_view = "login"
#
#     cloudinary.config(
#         cloud_name='dxxwcby8l',
#         api_key='792844686918347',
#         api_secret='T8ys_Z9zaKSqmKWa4K1RY6DXUJg'
#     )
#
#     return app

# Apartment_manage/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

db = SQLAlchemy()
login = LoginManager()

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.secret_key = "super-secret-key"

    app.config["SQLALCHEMY_DATABASE_URI"] = \
        "mysql+pymysql://root:root@localhost/chungcudb?charset=utf8mb4"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login.init_app(app)
    login.login_view = "login_process"

    cloudinary.config(
        cloud_name='dxxwcby8l',
        api_key='792844686918347',
        api_secret='T8ys_Z9zaKSqmKWa4K1RY6DXUJg'
    )

    return app

