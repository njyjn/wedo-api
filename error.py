from flask import Blueprint, jsonify

from auth import AuthError

error = Blueprint('error', __name__)


@error.app_errorhandler(400)
def bad_request(error):
    return jsonify({
                    'success': False,
                    'error': 400,
                    'message': 'bad request'
                    }), 400


@error.app_errorhandler(404)
def not_found(error):
    return jsonify({
                    'success': False,
                    'error': 404,
                    'message': 'not found'
                    }), 404


@error.app_errorhandler(422)
def unprocessable(error):
    return jsonify({
                    'success': False,
                    'error': 422,
                    'message': 'unprocessable entity'
                    }), 422


@error.app_errorhandler(500)
@error.app_errorhandler(Exception)
def internal_server_error(error):
    return jsonify({
                    'success': False,
                    'error': 500,
                    'message': f'internal server error: {error}'
                    }), 500


@error.app_errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
                    'success': False,
                    'error': error.status_code,
                    'message': error.error
                    }), error.status_code
