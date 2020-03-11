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
# @requires_auth(permission='create:guests')
@requires_auth()
def create_invites(jwt):
    """
    Create invite

    Event must already exist in the database

    POST /api/v1/invites
    {
        "guests": [1,2,3],
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


@invites.route('/api/v1/invites/verify', methods=['GET'])
@cross_origin()
# @requires_auth(permission='create:guests')
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
