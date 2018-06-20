import sys
from .constants import DATABASE_URL, CLIENT_ID, CLIENT_SECRET, SECRET_KEY, WHITELIST, FAKE_NAME, FAKE_EMAIL, FAKE_PASSWORD
from .auth import oauth
from .socket import socketio
from .main import app as base_app
from .models import db, Client, WhiteList, User
from app.utils import create_user

def init_user():
    user = User.query.filter_by(email = FAKE_EMAIL).first()
    if not user:
        create_user(FAKE_NAME, FAKE_EMAIL, FAKE_PASSWORD)

def init_client():
    if not Client.query.filter_by(client_id = CLIENT_ID).first():
        client = Client(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            _redirect_uris='',
            _default_scopes='email'
        )
        db.session.add(client)
        try:
            db.session.commit()
        except Exception as e:
            sys.stderr.write('Error creating client')
            sys.stderr.write(e.__doc__)
def init_whitelist():
    hosts = WHITELIST.split(',')
    for host in hosts:
        if not WhiteList.query.filter_by(host = host).first():
            entry = WhiteList(host = host)
            db.session.add(entry)
            try:
                db.session.commit()
            except Exception as e:
                sys.stderr.write('Error creating whitelist')
                sys.stderr.write(e.__doc__)

def create_app():
    base_app.secret_key = SECRET_KEY
    base_app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    base_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    base_app.config['WTF_CSRF_ENABLED'] = False
    oauth.init_app(base_app)
    socketio.init_app(base_app)
    db.init_app(base_app)
    with base_app.app_context():
        db.create_all() 
        init_client() 
        init_whitelist() 
        init_user()
    return base_app
app = create_app()