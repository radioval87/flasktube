import datetime
import os
import uuid

import flask_login
from flask import (Blueprint, current_app, flash, redirect,
                   render_template, request, session, url_for)
from werkzeug.utils import secure_filename

import database.database as db
from models.models import Comment, LoginForm, Post, User

routes_bp = Blueprint('routes_bp', __name__,
                      template_folder='templates', url_prefix='',
                      static_folder='static')

#=====================AUX FUNCTIONS==========================

def allowed_file(filename):
    ALLOWED_EXTENSIONS = current_app.config["ALLOWED_EXTENSIONS"]
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def check_ava(nickname):
    UPLOAD_DIR = current_app.config["UPLOAD_DIR"]
    ava_set = False
    if os.path.isfile(os.path.join(UPLOAD_DIR+nickname, 'ava_'+ nickname +'.jpg')):
        ava_set = True
    return ava_set

def get_avas_by_nicknames(nicknames):
    avas = {}
    for nickname in nicknames:
        if check_ava(nickname):
            src = os.path.join(
                '/static/uploaded/'+nickname, 'ava_'+ nickname +'.jpg')
        else:
            src = '/static/default_ava.png'
        avas.update({nickname:src})
    return avas

def admin_login(func):
    def wrapper(*args, **kwargs):
        if flask_login.current_user.nickname == 'admin':
            result = func(*args, **kwargs)
            return result
        return render_template('errors/405.html')
    wrapper.__name__ = func.__name__
    return wrapper

#===================ROUTES===========================

@routes_bp.route("/", methods=['GET', 'POST'])
def login():
    if flask_login.current_user.is_authenticated:
        return redirect(url_for('routes_bp.profile',
                                nickname=flask_login.current_user.nickname))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = db.get_user_by_email(form.email.data)
            if user and user.check_password(form.password.data):
                flask_login.login_user(user, remember=form.remember.data)
                return redirect(url_for('routes_bp.profile',
                                        nickname=user.nickname))
            session.pop('_flashes', None)
            flash("Invalid e-mail/password", 'error')
            return redirect(url_for('routes_bp.login'))
    return render_template('login.html', form=form)

@routes_bp.route('/logout/')
@flask_login.login_required
def logout():
    session.pop('_flashes', None)
    flask_login.logout_user()
    flash("You have been logged out.")
    return redirect(url_for('routes_bp.login'))

@routes_bp.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    if request.method == 'POST':
        id_ = str(uuid.uuid4())
        fname = request.form['fname']
        lname = request.form['lname']
        nickname = request.form['nickname']
        gender = request.form['gender']
        password = request.form['password']
        email = request.form['email']
        new_user = User(id_, fname, lname, nickname, gender, '', email)
        new_user.set_password(password)
        db.create_user(new_user)
        session.pop('_flashes', None)
        flash('Profile is created', 'message')
        return redirect(url_for('routes_bp.login'))

@routes_bp.route('/profile/<nickname>', methods=['GET', 'POST'])
def profile(nickname):
    current_user = flask_login.current_user
    if request.method == 'GET':
        try:
            profile_ = db.get_user_by_nickname(nickname)
            auth = flask_login.current_user.is_authenticated
            posts = db.get_all_posts_by_author_id(profile_.id)
            comments = db.get_all_comments_by_posts_ids(posts)
            likes = db.get_all_likes_by_posts_ids(posts)
            nol = db.get_all_number_of_likes_by_posts_ids(posts)
            followed_ids = []
            if current_user.is_authenticated:
                followed_ids = db.get_all_followed_ids_by_id(current_user.id)
            ava_set = check_ava(nickname)
            return render_template("posts.html",
                                   current_user=current_user,
                                   profile=profile_, auth=auth,
                                   posts=posts, comments=comments,
                                   ava_set=ava_set,
                                   followed_ids=followed_ids,
                                   likes=likes, nol=nol)
        except TypeError:
            return render_template('errors/404.html')
    if request.method == 'POST':
        profile_ = db.get_user_by_nickname(nickname)
        post_id = str(uuid.uuid4())
        post_text = request.form['new_post']
        post_date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        author_id = profile_.id
        author_nickname = profile_.nickname
        new_post = Post(post_id, post_text, post_date, author_id,
                        author_nickname)
        db.add_post(new_post)
        return redirect(url_for('routes_bp.profile', nickname=current_user.nickname))

@routes_bp.route('/profile/ava_upload/<nickname>', methods=['POST'])
@flask_login.login_required
def ava_upload(nickname):
    UPLOAD_DIR = current_app.config["UPLOAD_DIR"]
    UPLOAD_FOLDER = UPLOAD_DIR+nickname
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    file = request.files['file']
    file.filename = 'ava_'+ nickname +'.jpg'

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
    return redirect(url_for('routes_bp.profile',
                            nickname=flask_login.current_user.nickname))

@routes_bp.route('/profile/<nickname>/followed/', methods=['GET'])
def fetch_followed(nickname):
    try:
        profile_ = db.get_user_by_nickname(nickname)
        current_user = flask_login.current_user
        followed_users = db.get_all_followed_by_nickname(nickname)
        followed_ids = []
        if current_user.is_authenticated:
            followed_ids = db.get_all_followed_ids_by_id(current_user.id)
        auth = flask_login.current_user.is_authenticated
        ava_set = check_ava(nickname)
        return render_template("followed.html",
                               followed_users=followed_users,
                               followed_ids=followed_ids,
                               ava_set=ava_set,
                               current_user=current_user,
                               profile=profile_,
                               auth=auth)
    except TypeError:
        return render_template('errors/404.html')

@routes_bp.route('/profile/<nickname>/followers/', methods=['GET'])
def fetch_followers(nickname):
    try:
        profile_ = db.get_user_by_nickname(nickname)
        current_user = flask_login.current_user
        followed_ids = []
        if current_user.is_authenticated:
            followed_ids = db.get_all_followed_ids_by_id(current_user.id)
        followers = db.get_all_followers_by_nickname(nickname)
        auth = flask_login.current_user.is_authenticated
        ava_set = check_ava(nickname)
        return render_template("followers.html", followers=followers,
                               current_user=current_user,
                               profile=profile_, auth=auth,
                               followed_ids=followed_ids,
                               ava_set=ava_set)
    except TypeError:
        return render_template('errors/404.html')

@routes_bp.route('/profile/<nickname>/news/', methods=['GET'])
def fetch_news(nickname):
    try:
        profile_ = db.get_user_by_nickname(nickname)
        current_user = flask_login.current_user
        followed_ids = []
        if current_user.is_authenticated:
            followed_ids = db.get_all_followed_ids_by_id(current_user.id)
        auth = flask_login.current_user.is_authenticated
        news = db.get_news_by_nickname(nickname)
        ava_set = check_ava(nickname)
        likes = db.get_all_likes_by_posts_ids(news)
        nol = db.get_all_number_of_likes_by_posts_ids(news)
        return render_template("news.html", news=news,
                               current_user=current_user,
                               profile=profile_, auth=auth,
                               ava_set=ava_set,
                               followed_ids=followed_ids, likes=likes,
                               nol=nol)
    except TypeError:
        return render_template('errors/404.html')

@routes_bp.route('/follow/<profile_id>', methods=['POST'])
@flask_login.login_required
def add_followed(profile_id):
    current_user = flask_login.current_user
    followed_ids = db.get_all_followed_ids_by_id(current_user.id)
    if profile_id not in followed_ids:
        id_ = flask_login.current_user.id
        followed_id = profile_id
        db.add_followed(id_, followed_id)
    return ('', 204)

@routes_bp.route('/profile/<post_id>/add_comment', methods=['POST'])
@flask_login.login_required
def add_comment(post_id):
    post = db.get_post_by_post_id(post_id)
    comment_text = request.form['new_comment']
    comment_date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    comment_author_id = flask_login.current_user.id
    comment_author_nickname = flask_login.current_user.nickname
    comment_id = str(uuid.uuid4())
    new_comment = Comment(post_id, comment_text, comment_date,
                          comment_author_id, comment_author_nickname,
                          comment_id)
    db.add_comment(new_comment)
    current_user = db.get_user_by_id(post.author_id)
    return redirect(url_for('routes_bp.profile', nickname=current_user.nickname))

@routes_bp.route('/profile/<post_id>/like', methods=['POST'])
@flask_login.login_required
def add_like(post_id):
    post = db.get_post_by_post_id(post_id)
    like_date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    user_id = flask_login.current_user.id
    user_nickname = flask_login.current_user.nickname
    new_like = (post.post_id, like_date, user_id, user_nickname)
    db.add_like(new_like)
    return ('', 204)

@routes_bp.route('/profile/<post_id>/unlike', methods=['POST'])
@flask_login.login_required
def delete_like(post_id):
    user_id = flask_login.current_user.id
    db.delete_like(post_id, user_id)
    return ('', 204)

@routes_bp.route('/profile/<nickname>/news/<post_id>/n_like', methods=['POST'])
@flask_login.login_required
def n_add_like(post_id, nickname):
    like_date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    user_id = flask_login.current_user.id
    user_nickname = flask_login.current_user.nickname
    new_like = (post_id, like_date, user_id, user_nickname)
    db.add_like(new_like)
    return redirect(url_for('routes_bp.fetch_news', nickname=nickname))

@routes_bp.route('/profile/<nickname>/news/<post_id>/n_unlike', methods=['POST'])
@flask_login.login_required
def n_delete_like(post_id, nickname):
    user_id = flask_login.current_user.id
    db.delete_like(post_id, user_id)
    return redirect(url_for('routes_bp.fetch_news', nickname=nickname))

@routes_bp.route('/profile/<post_id>/who_liked', methods=['GET'])
def who_liked(post_id):
    post = db.get_post_by_post_id(post_id)
    current_user = flask_login.current_user
    auth = flask_login.current_user.is_authenticated
    likes = db.get_liked_users(post_id)
    avas = get_avas_by_nicknames(likes)
    return render_template("who_liked.html", current_user=current_user,
                           auth=auth, likes=likes, post=post, avas=avas)

@routes_bp.route('/profile/del/<post_id>', methods=['POST'])
@flask_login.login_required
def delete_post(post_id):
    db.delete_post(post_id)
    return redirect(url_for('routes_bp.profile',
                            nickname=flask_login.current_user.nickname))

@routes_bp.route('/del_followed/<followed_id>', methods=['POST'])
@flask_login.login_required
def delete_followed(followed_id):
    id_ = flask_login.current_user.id
    db.delete_followed(id_, followed_id)
    return redirect(url_for('routes_bp.fetch_followed',
                            nickname=flask_login.current_user.nickname))

@routes_bp.route('/del_follower/<follower_id>', methods=['POST'])
@flask_login.login_required
def delete_follower(follower_id):
    id_ = flask_login.current_user.id
    db.delete_followed(follower_id, id_)
    return redirect(url_for('routes_bp.fetch_followers',
                            nickname=flask_login.current_user.nickname))

#==================ADMIN ROUTES======================

@routes_bp.route("/admin", methods=["GET"])
@flask_login.login_required
@admin_login
def admin():
    return render_template("admin.html")

@routes_bp.route("/list", methods=['GET'])
@flask_login.login_required
@admin_login
def show_list():
    users = db.fetch_all_users()
    return render_template("list.html", users=users)

@routes_bp.route("/list/del/<user_id>", methods=['POST'])
@flask_login.login_required
@admin_login
def delete(user_id):
    db.delete_user(user_id)
    users = db.fetch_all_users()
    return render_template("list.html", users=users)

@routes_bp.route("/list/edit/<user_id>", methods=['GET', 'POST'])
@flask_login.login_required
@admin_login
def edit(user_id):
    try:
        if request.method == 'GET':
            user = db.get_user_by_id(user_id)
        if request.method == 'POST':
            id_ = user_id
            fname = request.form['fname']
            lname = request.form['lname']
            nickname = request.form['nickname']
            gender = request.form['gender']
            password_hash = db.get_user_by_id(id_).password_hash
            email = db.get_user_by_id(id_).email
            user = User(id_, fname, lname, nickname,
                        gender, password_hash, email)
            db.update_user(user)
        return render_template("edit.html", user=user)
    except TypeError:
        return render_template("admin.html")

@routes_bp.route("/add", methods=["POST"])
@flask_login.login_required
@admin_login
def add():
    id_ = str(uuid.uuid4())
    fname = request.form['fname']
    lname = request.form['lname']
    nickname = request.form['nickname']
    gender = request.form['gender']
    password = request.form['password']
    email = request.form['email']
    new_user = User(id_, fname, lname, nickname, gender, '', email)
    new_user.set_password(password)
    db.create_user(new_user)
    return render_template("admin.html")

#==================ERROR HANDLERS======================

@routes_bp.errorhandler(401)
def auth_required(err):
    if current_app.config['DEBUG']:
        print(err)
    return render_template('Errors/401.html'), 401

@routes_bp.errorhandler(404)
def not_found(err):
    if current_app.config['DEBUG']:
        print(err)
    return render_template('Errors/404.html'), 404

@routes_bp.errorhandler(405)
def not_allowed(err):
    if current_app.config['DEBUG']:
        print(err)
    return render_template('Errors/405.html'), 405

#======================================================
