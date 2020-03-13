import sys

from flask import current_app, Blueprint, jsonify, request, abort
from flask_cors import cross_origin

from auth import requires_auth
from models import Guest, to_list_of_dicts, close, rollback

guests = Blueprint('guests', __name__)


@guests.route('/api/v1/guests', methods=['GET'])
@cross_origin()
@requires_auth(permission='read:guests')
# @requires_auth()
def get_guests(jwt):
    """
    Get guests

    GET /api/vi/guests
    """
    guests = Guest.query.all()
    response = {
        'success': True,
        'guests': to_list_of_dicts(guests)
    }
    return jsonify(response)


@guests.route('/api/v1/guests/<int:id>', methods=['GET'])
@cross_origin()
@requires_auth(permission='read:guests')
# @requires_auth()
def get_guest(jwt, id):
    """
    Get guest by id

    GET /api/vi/guests/<id>

    Keyword arguments:
    id -- the id of the guest
    """
    guest = Guest.query.get(id)
    if guest is None:
        abort(404)
    response = {
        'success': True,
        'guest': guest.to_dict()
    }
    return jsonify(response)


@guests.route('/api/v1/guests', methods=['POST'])
@cross_origin()
@requires_auth(permission='create:guests')
# @requires_auth()
def create_guests(jwt):
    """Create guest

    Invite must already exist in the database. It is optional.

    POST /api/v1/guests
    {
        "name": "John Doe",
        "telegram_username": "john"
    }
    """
    payload = request.get_json()
    if payload is None:
        abort(400)
    guest = Guest(
        name=payload.get('name'),
        telegram_username=payload.get('telegram_username')
    )
    try:
        guest.insert()
        response = {
            'success': True,
            'guest': guest.to_dict()
        }
    except Exception:
        rollback()
        current_app.logger.info(sys.exc_info())
        abort(422)
    finally:
        close()
    return jsonify(response)


@guests.route('/api/v1/guests/<int:id>', methods=['PATCH'])
@cross_origin()
@requires_auth(permission='create:guests')
# @requires_auth()
def edit_guests(jwt, id):
    """
    Edit guest

    PATCH /api/v1/guests/<id>
    {
        "name": "Jane Doe",
    }

    Keyword arguments:
    id -- the id of the guest
    """
    payload = request.get_json()
    if payload is None:
        abort(400)
    guest = Guest.query.get(id)
    if guest is None:
        abort(404)
    try:
        for key in payload.keys():
            setattr(guest, key, payload.get(key))
    except Exception:
        current_app.logger.info(sys.exc_info())
        abort(400)
    try:
        guest.update()
        response = {
            'success': True,
            'guest': guest.to_dict()
        }
    except Exception:
        rollback()
        current_app.logger.info(sys.exc_info())
        abort(422)
    finally:
        close()
    return jsonify(response)


@guests.route('/api/v1/guests/<int:id>', methods=['DELETE'])
@cross_origin()
@requires_auth(permission='create:guests')
# @requires_auth()
def delete_guests(jwt, id):
    """
    Delete guest

    DELETE /api/v1/guests/<id>

    Keyword arguments:
    id -- the id of the guest
    """
    guest = Guest.query.get(id)
    if guest is None:
        abort(404)
    try:
        guest.delete()
        response = {
            'success': True,
        }
    except Exception:
        rollback()
        current_app.logger.info(sys.exc_info())
        abort(422)
    finally:
        close()
    return jsonify(response)


@guests.route('/api/v1/guests/<int:id>/invites', methods=['POST', 'PUT'])
@cross_origin()
@requires_auth(permission='create:guests')
# @requires_auth()
def create_guest_invites(jwt, id):
    """
    Link guest to invite

    Invite must already exist in the database

    POST /api/v1/guests/<id>/invites
    PUT /api/v1/guests/<id>/invites
    {
        "invite_id": 1
    }

    Keyword arguments:
    id -- the id of the guest
    """
    payload = request.get_json()
    if payload is None:
        abort(400)
    guest = Guest.query.get(id)
    if guest is None:
        abort(404)
    try:
        guest.invite_id = payload.get('invite_id')
        guest.update()
        response = {
            'success': True,
            'guest': guest.to_dict()
        }
    except Exception:
        rollback()
        current_app.logger.info(sys.exc_info())
        abort(422)
    finally:
        close()
    return jsonify(response)


@guests.route('/api/v1/guests/<int:id>/invites', methods=['DELETE'])
@cross_origin()
@requires_auth(permission='create:guests')
# @requires_auth()
def delete_guest_invites(jwt, id):
    """
    Unlink guest from invite

    DELETE /api/v1/guests/<id>/invites

    Keyword arguments:
    id -- the id of the guest
    """
    guest = Guest.query.get(id)
    if not guest:
        abort(404)
    try:
        guest.invite_id = None
        guest.update()
        response = {
            'success': True,
            'guest': guest.to_dict()
        }
    except Exception:
        rollback()
        current_app.logger.info(sys.exc_info())
        abort(422)
    finally:
        close()
    return jsonify(response)
