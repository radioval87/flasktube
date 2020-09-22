import flask_login
from flask import Flask

import database.database as db
from API.routes import routes_bp

app = Flask(__name__)

app.config.from_pyfile('config.ini')

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

app.register_blueprint(routes_bp)

@login_manager.user_loader
def load_user(user_id):
    user = db.get_user_by_id(user_id)
    if user:
        return user
    return None

if __name__ == '__main__':
    db.init_db()
    app.run(host="0.0.0.0")
