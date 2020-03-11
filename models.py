from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property

from auth import generate_random_string_with_digits
from config import SQLALCHEMY_DATABASE_URI

db = SQLAlchemy()


def setup_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    db.create_all()
    migrate = Migrate(app, db)


def to_list_of_dicts(list_of_obj):
    return [obj.to_dict() for obj in list_of_obj]


def rollback():
    db.session.rollback()


def close():
    db.session.close()


class Guest(db.Model):
    __tablename__ = 'guests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    invite_id = db.Column(db.Integer, db.ForeignKey('invites.id'),
                          nullable=True)
    telegram_username = db.Column(db.String(32), nullable=True)

    def __repr__(self):
        return f'<Guest {self.id} {self.name}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def to_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            invite_id=self.invite_id,
            telegram_username=self.telegram_username
        )


class Invite(db.Model):
    __tablename__ = 'invites'

    id = db.Column(db.Integer, primary_key=True)
    guests = db.relationship('Guest', backref='invite', lazy=False)
    accepted = db.Column(db.Boolean, nullable=False, default=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'),
                         nullable=False)
    invite_code = db.Column(db.String(6), unique=True, nullable=False)

    def __repr__(self):
        return f'<Invite {self.id}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def to_dict(self):
        return dict(
            id=self.id,
            guests=to_list_of_dicts(self.guests),
            accepted=self.accepted,
            event_id=self.event_id
        )

    def generate_invite_code(self):
        self.invite_code = generate_random_string_with_digits(6)
        return self.invite_code

    def verify_invite_code(self, plaintext):
        pass


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=True)
    start_datetime = db.Column(db.DateTime, nullable=True)
    end_datetime = db.Column(db.DateTime, nullable=True)
    invites = db.relationship('Invite', backref='list', lazy=True)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def to_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            address=self.address,
            start_datetime=self.start_datetime,
            end_datetime=self.end_datetime,
            invites=to_list_of_dicts(self.invites)
        )
