import json
from flask import Flask
from flask import session, request
from flask_sqlalchemy import SQLAlchemy
from app.constants import SECRET_KEY
from collections import OrderedDict
from werkzeug.security import gen_salt
import datetime 
from sqlalchemy_utils import PasswordType, force_auto_coercion
from datetime import datetime, timedelta
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
import datetime
from sqlalchemy.dialects.mysql import INTEGER
force_auto_coercion() 
db = SQLAlchemy() 

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable = True)
    email = db.Column(db.String(75), nullable = False, unique = True)
    password = db.Column(
        PasswordType(
            schemes=[
                'pbkdf2_sha512',
            ]            
        ),
        unique=False,
        nullable=False,
    )
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    def verify_password(self, password):
        return self.password == password

    def generate_auth_token(self, expiration = 600):
      s = Serializer(SECRET_KEY, expires_in = expiration)
      return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SECRET_KEY) 
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None 
        except BadSignature:
            return None 
        user = User.query.get(data['id'])
        return user
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Client(db.Model):
    __tablename__ = "client"
    client_id = db.Column(db.String(40), primary_key=True, unique = True)
    client_secret = db.Column(db.String(55), nullable=False, unique = True)
    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)
    @property
    def client_type(self):
        return 'public'
    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []
    @property
    def default_redirect_uri(self):
        return ''
    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []
class Grant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')
    )
    user = db.relationship('User')
    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')
    code = db.Column(db.String(255), index=True, nullable=False)
    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id')
    )
    user = db.relationship('User')

    token_type = db.Column(db.String(40))
    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)
    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

class Room(db.Model):
    __tablename__ = "room"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable = True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
        
class RoomUser(db.Model):
    __tablename__ = "room_user"
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    __table_args__ = (db.UniqueConstraint('room_id', 'user_id', name='_room_user_uc'), )
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Message(db.Model):
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False) #stores the sender 
    room_id =  db.Column(db.Integer, db.ForeignKey('room.id', ondelete='CASCADE'), nullable=False)
    raw = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class WhiteList(db.Model):
    __tablename__ = "whitelist"
    id = db.Column(db.Integer, primary_key = True)
    host = db.Column(db.String(50), nullable = True)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class ImageSource(db.Model):
    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = True)
    path = db.Column(db.Text)
    width = db.Column(db.Integer, nullable = False)
    height = db.Column(db.Integer, nullable = False)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    def __repr__(self):
        return "<ImageSource(path = %s, width = %s, height = %s)>" % (self.path, self.width, self.height)

class VideoSource(db.Model):
    __tablename__ = "video"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = True)
    path = db.Column(db.Text)
    length =  db.Column(db.Integer, nullable = False)
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    def __repr__(self):
        return "<VideoSource(path = %s, length = %s)>" % (self.path, self.length)

class MessageMeta(db.Model):
    __tablename__ = "message_source"
    id = db.Column(db.Integer, primary_key = True)
    message_id  = db.Column(db.Integer, db.ForeignKey('message.id', ondelete='CASCADE'), nullable= False)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id', ondelete='CASCADE'), nullable=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id', ondelete='CASCADE'), nullable=True)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
