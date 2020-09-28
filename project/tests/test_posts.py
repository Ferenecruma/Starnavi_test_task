# project/tests/test_posts.py

import json
from datetime import datetime as dtm

from project.server import db
from project.server.models import User, Post, Likes
from project.tests.base import BaseTestCase


class TestAuthBlueprint(BaseTestCase):
    def test_post_creation(self):
        """ Test for post creation """
        with self.client:
            user = User(
                email='joe1@gmail.com',
                password='test'
            )
            db.session.add(user)
            db.session.flush()

            aut_token = user.encode_auth_token(user.id)

            response = self.client.post(
                '/post/create',
                headers=dict(
                    Authorization='Bearer ' +str(aut_token, 'UTF-8')),
                data=json.dumps(dict(
                    post_text="Testing post creation"
                )),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())

            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Added new post.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

            test_post = Post.query.filter_by(id=1).first()
            self.assertTrue(test_post.post_text == "Testing post creation")
            self.assertTrue(isinstance(test_post.created_on, dtm))

    def test_post_like(self):
        """ Test for like/dislike """

        with self.client:
            # like adding test
            user = User('test@email.com', 'nopassword')
            db.session.add(user)
            db.session.flush()

            post = Post('some text', user.id)
            db.session.add(post)
            db.session.flush()

            aut_token = user.encode_auth_token(user.id)

            response = self.client.post(
                '/post/like-unlike',
                headers=dict(
                    Authorization='Bearer ' + str(aut_token, 'UTF-8')
                ),
                data=json.dumps(dict(
                    post_id=post.id
                )),
                content_type='application/json'
            )

            like = Likes.query.get((user.id, post.id))

            self.assertTrue(isinstance(like.date, dtm))
            self.assertTrue(like.user_id == user.id)
            self.assertTrue(like.post_id == post.id)

            # like deleting test
            self.client.post(
                '/post/like-unlike',
                headers=dict(
                    Authorization='Bearer ' + str(aut_token, 'UTF-8')
                ),
                data=json.dumps(dict(
                    post_id=post.id
                )),
                content_type='application/json'
            )

            like = Likes.query.get((user.id, post.id))
            self.assertIsNone(like)

    
