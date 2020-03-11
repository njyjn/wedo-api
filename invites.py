import sys

from flask import current_app, Blueprint, jsonify, request, abort
from flask_cors import cross_origin
from sqlalchemy.orm.exc import MultipleResultsFound

from auth import requires_auth
from models import Invite, to_list_of_dicts, close, rollback, Guest

invites = Blueprint('invites', __name__)


@invites.route('/api/v1/invites', methods=['GET'])
@cross_origin()
# @requires_auth(permission='read:invites')
@requires_auth()
def get_invites(jwt):
    """
    Get invites

    GET /api/v1/invites
    """
    invites = Invite.query.all()
    response = {
        'success': True,
        'invites': to_list_of_dicts(invites)
    }
    return jsonify(response)


@invites.route('/api/v1/invites/<int:id>', methods=['GET'])
@cross_origin()
# @requires_auth(permission='read:invites')
@requires_auth()
def get_invite(jwt, id):
    """
    Get invite by id

    GET /api/v1/invites/<id>

    Keyword arguments:
    id -- the id of the invite
    """
    invite = Invite.query.get(id)
    if invite is None:
        abort(404)
    response = {
        'success': True,
        'invite': invite.to_dict()
    }
    return jsonify(response)


@invites.route('/api/v1/invites', methods=['POST'])
@cross_origin()
# @requires_auth(permission='create:invites')
@requires_auth()
def create_invites(jwt):
    """
    Create invite

    - Event must already exist in the database
    - Use Guests API to add guests to invite

    POST /api/v1/invites
    {
        "accepted": false,
        "event_id": 1
    }
    """
    payload = request.get_json()
    if payload is None:
        abort(400)
    invite = Invite(
        accepted=payload.get('accepted'),
        event_id=payload.get('event_id')
    )
    invite_code = invite.generate_invite_code()
    try:
        invite.insert()
        response = {
            'success': True,
            'invite': invite.to_dict(),
            'invite_code': invite_code
        }
    except Exception:
        rollback()
        current_app.logger.info(sys.exc_info())
        abort(422)
    finally:
        close()
    return jsonify(response)


@invites.route('/api/v1/invites/<int:id>', methods=['PATCH'])
@cross_origin()
# @requires_auth(permission='create:invites')
@requires_auth()
def edit_invites(jwt, id):
    """
    Edit invite

    - Event must already exist in the database
    - Use Guests API to modify guests on invite
    - It is not recommended to use this endpoint to regenerate invite codes,
      instead, use /api/v1/invites/regenerate

    PATCH /api/v1/invites/<id>
    {
        "accepted": False,
        "event_id": 2
    }

    Keyword arguments:
    id -- the id of the invite
    """
    payload = request.get_json()
    if payload is None:
        abort(400)
    invite = Invite.query.get(id)
    if invite is None:
        abort(404)
    try:
        for key in payload.keys():
            if key == 'invite_code':
                raise
            setattr(invite, key, payload.get(key))
    except Exception:
        current_app.logger.info(sys.exc_info())
        abort(400)
    try:
        invite.update()
        response = {
            'success': True,
            'invite': invite.to_dict()
        }
    except Exception:
        rollback()
        current_app.logger.info(sys.exc_info())
        abort(422)
    finally:
        close()
    return jsonify(response)


@invites.route('/api/v1/invites/<int:id>', methods=['DELETE'])
@cross_origin()
# @requires_auth(permission='create:invites')
@requires_auth()
def delete_invites(jwt, id):
    """
    Delete invite

    DELETE /api/v1/invites/<id>

    Keyword arguments:
    id -- the id of the invite
    """
    invite = Invite.query.get(id)
    if invite is None:
        abort(404)
    try:
        invite.delete()
        response = {
            'success': True
        }
    except Exception:
        rollback()
        current_app.logger.info(sys.exc_info())
        abort(422)
    finally:
        close()
    return jsonify(response)


@invites.route('/api/v1/invites/verify', methods=['GET'])
@cross_origin()
# @requires_auth(permission='read:invites')
@requires_auth()
def verify_invites(jwt):
    """
    Verify invite

    In this context the guestKey is the user's Telegram handle

    GET /api/v1/invites/verify?guestKey={guestKey}&inviteCode={inviteCode}
    """
    guest_key = request.args.get('guestKey', None)
    invite_code = request.args.get('inviteCode', None)
    if not guest_key or not invite_code:
        abort(400)
    # TODO: Separate guest concern
    invite = Invite.query.join(Invite.guests).filter(
        Guest.telegram_username == guest_key).one_or_none()
    if not invite:
        abort(404)
    valid = False
    if invite.invite_code == invite_code:
        valid = True
    response = {
        'success': True,
        'valid': valid
    }
    return jsonify(response)
