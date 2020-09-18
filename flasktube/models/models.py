from flask_login import UserMixin
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import (BooleanField, PasswordField, StringField, SubmitField)
from wtforms.validators import DataRequired


class User(UserMixin):
    def __init__(self, id_, fname, lname, nickname, gender, password_hash, email):
        self.id = id_
        self.fname = fname
        self.lname = lname
        self.nickname = nickname
        self.gender = gender
        self.password_hash = password_hash
        self.email = email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField()


class Post():
    def __init__(self, post_id, post_text, post_date, author_id, author_nickname):
        self.post_id = post_id
        self.post_text = post_text
        self.post_date = post_date
        self.author_id = author_id
        self.author_nickname = author_nickname


class Comment():
    def __init__(self, post_id, comment_text, comment_date, author_id, author_nickname, comment_id):
        self.post_id = post_id
        self.comment_text = comment_text
        self.comment_date = comment_date
        self.author_id = author_id
        self.author_nickname = author_nickname
        self.comment_id = comment_id
