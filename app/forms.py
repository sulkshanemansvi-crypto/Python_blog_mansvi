from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError

from .models import User


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(), Length(3, 30),
        Regexp(r"^[A-Za-z0-9_]+$", message="Letters, numbers and underscores only.")])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(6, 128)])
    confirm = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password", "Passwords must match.")])
    submit = SubmitField("Create account")

    def validate_username(self, field):
        if User.query.filter(User.username.ilike(field.data)).first():
            raise ValidationError("That username is taken.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("That email is already registered.")


class LoginForm(FlaskForm):
    username = StringField("Username or email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(3, 150)])
    category = StringField("Category", validators=[Length(max=50)])
    tags = StringField("Tags (comma separated)", validators=[Length(max=200)])
    body = TextAreaField("Story", validators=[DataRequired()])
    submit = SubmitField("Publish")


class CommentForm(FlaskForm):
    body = TextAreaField("Add a comment", validators=[DataRequired(), Length(1, 1000)])
    submit = SubmitField("Post comment")


class ProfileForm(FlaskForm):
    bio = TextAreaField("About you", validators=[Length(max=300)])
    submit = SubmitField("Save")
