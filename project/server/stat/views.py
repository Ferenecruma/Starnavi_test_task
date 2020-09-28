import datetime
from datetime import date

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from project.server import db
from project.server.models import User, Post, Likes

stat_blueprint = Blueprint('stat', __name__)


class UserAPI(MethodView):
    """
    User Resource
    """

    def get(self, user_id):
        # get the auth token
        auth_token = UserAPI.get_user_token(request)

        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                responseObject = UserAPI.get_user_by_id(resp)
                if responseObject['data']['is_superuser']:
                    responseObject = UserAPI.get_user_by_id(user_id)
                    # deleting unrequested data
                    del responseObject['data']['user_id']
                    del responseObject['data']['is_superuser']
                else:
                    responseObject = {
                        'status': 'fail',
                        'message': 'Access denied.'
                    }
                    return make_response(jsonify(responseObject)), 403
                return make_response(jsonify(responseObject)), 200
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401

    @staticmethod
    def get_user_token(rqst):
        auth_header = rqst.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        return auth_token

    @staticmethod
    def get_user_by_id(user_id):
        user = User.query.filter_by(id=user_id).first()
        responseObject = {
            'status': 'success',
            'data': {
                'user_id': user.id,
                'last_login': user.last_login,
                'last_request': user.last_request,
                'is_superuser': user.is_superuser
            }
        }
        return responseObject

class LikesStats(MethodView):
    def get(self):
        # get the post data
        auth_token = UserAPI.get_user_token(request)

        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user_info = UserAPI.get_user_by_id(resp)
                if user_info['data']['is_superuser']:
                    date_from, date_to = request.args.get('date_from'), request.args.get('date_to')
                    # check for posts in this interval
                    try:
                        start = self.query_stirng_to_date(date_from)
                        end = self.query_stirng_to_date(date_to)
                    except:
                        responseObject = {
                            'status': 'fail',
                            'message': 'Not valid time interval provided'
                        }
                        return make_response(jsonify(responseObject)), 404

                    valid_likes_counter = len(Likes.query.filter(Likes.date <= end).filter(Likes.date >= start).all())
                    responseObject = {
                        'status': 'success',
                        'likes_counter': valid_likes_counter,
                    }
                    return make_response(jsonify(responseObject)), 200
                else:
                    responseObject = {
                        'status': 'fail',
                        'message': 'Access denied.'
                    }
                    return make_response(jsonify(responseObject)), 404
        # invalid token
        responseObject = {
            'status': 'fail',
            'message': 'Provide valid token.'
        }
        return make_response(jsonify(responseObject)), 401

    def query_stirng_to_date(self, query_stirng):
        times = query_stirng.split('-')
        return date(year=int(times[0]), month=int(times[1]), day=int(times[2]))

# define the API resources
likes_analytics = LikesStats.as_view('likes_analytics')
user_view = UserAPI.as_view('user_api')

# add Rules for API Endpoints
stat_blueprint.add_url_rule(
    '/api/analitics/',
    view_func=likes_analytics,
    methods=['GET']
)

stat_blueprint.add_url_rule(
    '/api/status/<int:user_id>',
    view_func=user_view,
    methods=['GET']
)