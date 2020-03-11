import sys

from flask import Blueprint, jsonify, request, abort
from flask_cors import cross_origin

from auth import requires_auth
from models import Event, to_list_of_dicts, close, rollback

events = Blueprint('events', __name__)


@events.route('/api/v1/events', methods=['GET'])
@cross_origin()
# @requires_auth(permission='read:events')
@requires_auth()
def get_events(jwt):
    """Get events

    GET /api/v1/events
    """
    events = Event.query.all()
    response = {
        'success': True,
        'events': to_list_of_dicts(events)
    }
    return jsonify(response)


@events.route('/api/v1/events/<int:id>', methods=['GET'])
@cross_origin()
# @requires_auth(permission='read:events')
@requires_auth()
def get_event(jwt, id):
    """Get event by ID

    GET /api/v1/events/<id>

    Keyword arguments:
    id -- the id of the event
    """
    event = Event.query.get(id)
    if event is None:
        abort(404)
    response = {
        'success': True,
        'event': event.to_dict()
    }
    return jsonify(response)


@events.route('/api/v1/events', methods=['POST'])
@cross_origin()
# @requires_auth(permission='create:events')
@requires_auth()
def create_events(jwt):
    """Create event

    Use /api/v1/guests/<id>/invites to add invites

    POST /api/v1/events

    {
        "name": "Wedding Lunch",
        "address": "123 Main St, Aurora, CO 80011",
        "start_datetime": "2050-01-01T12:00:00-06:00",
        "end_datetime": "2050-01-01T14:00:00-06:00",
    }
    """
    payload = request.get_json()
    if payload is None:
        abort(400)
    event = Event(
        name=payload.get('name'),
        address=payload.get('address'),
        start_datetime=payload.get('start_datetime'),
        end_datetime=payload.get('end_datetime')
    )
    try:
        event.insert()
        response = {
            'success': True,
            'event': event.to_dict()
        }
    except Exception:
        rollback()
        current_app.logger.info(sys.exc_info())
        abort(422)
    finally:
        close()
    return jsonify(response)
