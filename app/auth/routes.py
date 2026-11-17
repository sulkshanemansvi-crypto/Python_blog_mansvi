from urllib.parse import urlsplit

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..forms import LoginForm, ProfileForm, RegisterForm
from ..models import User
from . import bp


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Welcome to Mansvi! Your account is ready ✿", "success")
        return redirect(url_for("main.index"))
    return render_template("auth/register.html", form=form, title="Join")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        ident = form.username.data.strip()
        user = User.query.filter(
            (db.func.lower(User.username) == ident.lower()) | (User.email == ident.lower())
        ).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            nxt = request.args.get("next", "")
            parts = urlsplit(nxt)
            if not nxt or parts.netloc or parts.scheme or not nxt.startswith("/"):
                nxt = url_for("main.index")
            return redirect(nxt)
        flash("Invalid username or password.", "danger")
    return render_template("auth/login.html", form=form, title="Log in")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out. See you soon!", "info")
    return redirect(url_for("main.index"))


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.bio = form.bio.data
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("main.profile", username=current_user.username))
    return render_template("auth/settings.html", form=form, title="Edit profile")
