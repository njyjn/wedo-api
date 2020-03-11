from flask import Blueprint, Flask
from flask_cors import CORS

from error import error
from events import events
from guests import guests
from invites import invites
from models import db, setup_db


app = Flask(__name__)
app.register_blueprint(error)
app.register_blueprint(events)
app.register_blueprint(guests)
app.register_blueprint(invites)

setup_db(app)

CORS(app, resources={r'/*': {'origins': '*'}})
