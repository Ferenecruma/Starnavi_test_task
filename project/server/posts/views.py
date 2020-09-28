import datetime
from datetime import date

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from project.server import db
from project.server.models import User, Post, Likes
from project.server.stat.views import UserAPI

posts_blueprint = Blueprint('posts', __name__)


class PostAPI(MethodView):
    """
    Create New Post
    """

    def post(self):
        # get the post data
        auth_token = UserAPI.get_user_token(request)
        post_data = request.get_json()

        if auth_token:
            user_id = User.decode_auth_token(auth_token)
            if not isinstance(user_id, str):
                try:
                    self.add_post_to_database(post_data, user_id)
                    responseObject = {
                        'status': 'success',
                        'message': 'Added new post.'
                    }
                    return make_response(jsonify(responseObject)), 200
                except:
                    responseObject = {
                        'status': 'fail',
                        'message': 'Could not create post.'
                    }
                    return make_response(jsonify(responseObject)), 401

        responseObject = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return make_response(jsonify(responseObject)), 401

    def add_post_to_database(self, post_data, user_id):
        post = Post(
            post_text=post_data.get('post_text'),
            created_on=datetime.datetime.now(),
            user_id=user_id
        )
        db.session.add(post)
        db.session.commit()


class PostLikeToggle(MethodView):
    def post(self):
        # get the post data
        auth_token = UserAPI.get_user_token(request)
        post_id = request.get_json().get('post_id')

        if auth_token:
            user_id = User.decode_auth_token(auth_token)
            if not isinstance(user_id, str):
                post = Post.query.get(post_id)
                if post:
                    like = Likes.query.get((user_id, post_id))
                    if like:
                        db.session.delete(like)
                    else:
                        like = Likes(user_id=user_id, post_id=post_id)
                        db.session.add(like)

                    db.session.commit()
                    responseObject = {
                        'status': 'success',
                        'message': 'Post liked/disliked'
                    }
                    return make_response(jsonify(responseObject)), 200
                else:
                    # If post doesnt exit
                    responseObject = {
                        'status': 'fail',
                        'message': 'Post doesn\'t exist'
                    }
                    return make_response(jsonify(responseObject)), 404

        # invalid token
        responseObject = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return make_response(jsonify(responseObject)), 401

# define the API resources
post_creation_view = PostAPI.as_view('post_api')
post_like_view = PostLikeToggle.as_view('post_like')

# add Rules for API Endpoints
posts_blueprint.add_url_rule(
    '/post/create',
    view_func=post_creation_view,
    methods=['POST']
)

posts_blueprint.add_url_rule(
    '/post/like',
    view_func=post_like_view,
    methods=['POST']
)