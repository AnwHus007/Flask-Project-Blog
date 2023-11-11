from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from pymongo import MongoClient
from datetime import datetime

# db = SQLAlchemy()
# DB_NAME = "database.db"

client = MongoClient('mongodb+srv://anwarhussainkp007:Anwar8547@cluster0.f148a5t.mongodb.net/?retryWrites=true&w=majority')
db = client['Flask']  
users = db['users']
posts = db['posts']
comments = db['comments']
likes = db['likes']

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "hello world"
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    # db.init_app(app)

    from .views import views
    from .auth import auth
    from .models import User
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    # from .models import User, Post, Comment, Like

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        # return User.query.get(int(id))
        if users.find_one({"email": id}):
            user=User()
            user.id=id
            return user
        return {}

    # with app.app_context():
    #     db.create_all()

    return app