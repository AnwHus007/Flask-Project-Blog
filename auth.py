from flask import Blueprint, render_template, redirect, url_for, request, flash,session
from . import users
# from .models import User
from flask_login import login_user, logout_user, login_required, current_user
import flask_login
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User

auth = Blueprint("auth", __name__)



@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        # user = User.query.filter_by(email=email).first()
        user = users.find_one({"email": email})
        if user:
            # if check_password_hash(user.password, password):
            if check_password_hash(user["password"], password):
                flash("Logged in!", category='success')
                user = User()
                user.id = email
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        # email_exists = User.query.filter_by(email=email).first()
        # username_exists = User.query.filter_by(username=username).first()
        email_exists = users.find_one({"email": email})
        username_exists = users.find_one({"username": username})

        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Password don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            # new_user = User(email=email, username=username, password=generate_password_hash(
            #     password1, method='sha256'))
            # db.session.add(new_user)
            # db.session.commit()
            new_user = {
                "email": email,
                "username": username,
                "password": generate_password_hash(password1, method='sha256')
            }
            users.insert_one(new_user)
            # login_user(new_user, remember=True)
            session['email'] = new_user.email
            flash('User created!')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))
