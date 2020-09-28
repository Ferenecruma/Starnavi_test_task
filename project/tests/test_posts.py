# project/tests/test_posts.py

import unittest
import json
import datetime

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
            self.assertTrue(isinstance(test_post.created_on, datetime.datetime))

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
                '/post/like',
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
                '/post/like',
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

    def test_stat_api(self):
        with self.client:
            # like adding test
            user = User('test@email.com', 'nopassword', is_superuser=True)
            db.session.add(user)
            default_user = User('user@email.com', 'diff_pas', False)
            db.session.add(default_user)
            db.session.flush()

            # creating test posts
            posts = []
            for i in range(3):
                posts.append(Post('some text' + str(i), user.id))
            db.session.add_all(posts)
            db.session.flush()

            likes = []
            for i in range(3):
                likes.append(Likes(user.id, posts[i].id))

            db.session.add_all(likes)
            db.session.flush()

            aut_token = user.encode_auth_token(user.id)
            aut_token_non_admin = user.encode_auth_token(default_user.id)

            # Test analytics for admin user
            response = self.client.get(
                'api/analitics/?date_from=2020-01-15&date_to=2020-02-15',
                headers=dict(
                    Authorization='Bearer ' + str(aut_token, 'UTF-8')
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertEqual(response.status_code, 200)

            # Test for 3 posts 
            response = self.client.get(
                'api/analitics/?date_from=2020-01-15&date_to=2022-02-15',
                headers=dict(
                    Authorization='Bearer ' + str(aut_token, 'UTF-8')
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['likes_counter'] == len(likes))
            self.assertEqual(response.status_code, 200)

            # Test analytics for non admin user
            response = self.client.get(
                'api/analitics/?date_from=2020-01-15&date_to=2020-02-15',
                headers=dict(
                    Authorization='Bearer ' + str(aut_token_non_admin, 'UTF-8')
                ),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Access denied.')
            self.assertEqual(response.status_code, 404)
