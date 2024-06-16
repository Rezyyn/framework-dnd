from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    profile_picture = db.Column(db.String(64), default='default.jpg')
    roles = db.relationship('Role', secondary='user_roles')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    answer = db.Column(db.Text)

class GeoJSONLayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    data = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    rooms = db.relationship('Room', secondary='room_layers', back_populates='active_layers')

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    active_layers = db.relationship('GeoJSONLayer', secondary='room_layers', back_populates='rooms')

class RoomLayers(db.Model):
    __tablename__ = 'room_layers'
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), primary_key=True)
    layer_id = db.Column(db.Integer, db.ForeignKey('geo_json_layer.id'), primary_key=True)
