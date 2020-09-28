import datetime
from datetime import datetime as dtm
import jwt

from project.server import app, db, bcrypt
from project.server.config import MNTS_FOR_TOKEN_EXPR


class Likes(db.Model):
    """ Model for storing likes """
    __tablename__ = "likes"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    date = db.Column(db.DateTime, index=True, default=dtm.now)

    def __init__(self, user_id, post_id, **kwargs):
        super(Likes, self).__init__(**kwargs)
        self.user_id = user_id
        self.post_id = post_id


class User(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    is_superuser = db.Column(db.Boolean, nullable=False, default=False)
    last_login = db.Column(db.DateTime)
    last_request = db.Column(db.DateTime, nullable=False)

    def __init__(self, email, password, is_superuser=False, **kwargs):
        super(User, self).__init__(**kwargs)
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.last_request = datetime.datetime.now()
        self.registered_on = datetime.datetime.now()
        self.is_superuser = is_superuser

    @staticmethod
    def encode_auth_token(user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=MNTS_FOR_TOKEN_EXPR),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class Post(db.Model):
    """Model for storing posts related details """
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_text = db.Column(db.String(300), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False)

    def __init__(self, post_text, user_id, **kwargs):
        super(Post, self).__init__(**kwargs)
        self.post_text = post_text
        self.created_on = datetime.datetime.now()
        self.user_id = user_id
