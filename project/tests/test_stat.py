# project/tests/test_stat.py
import json

from project.server import db
from project.server.models import User, Post, Likes
from project.tests.base import BaseTestCase


class TestAuthBlueprint(BaseTestCase):
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
        
    def test_user_status_superuser(self):
        """ Test for user status """
        with self.client:

            user = User('test@email.com', 'nopassword', is_superuser=True)
            db.session.add(user)
            db.session.flush()
            aut_token = user.encode_auth_token(user.id)
        
            # Dummy user for access test
            super_user = User(
                email='joe1@gmail.com',
                password='test'
            )
            db.session.add(super_user)
            db.session.commit()

            # Superuser makes request for user data 
            response = self.client.get(
                '/api/status/2',
                headers=dict(
                    Authorization='Bearer ' + str(aut_token, 'UTF-8')
                )
            )
            data = json.loads(response.data.decode())

            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['data'] is not None)
            self.assertTrue(isinstance(data['data']['last_request'], str))
            self.assertEqual(response.status_code, 200)

    def test_user_status_default_user(self):
        """ 
        Test for user status 
        if request is from default user
        """
        with self.client:
            user = User(
                email='joe1@gmail.com',
                password='test'
            )
            # Dummy user1 for access test
            user1 = User(
                email='joe2@gmail.com',
                password='test1'
            )
            db.session.add(user)
            db.session.add(user1)
            db.session.commit()

            #Getting token for user
            aut_token = user.encode_auth_token(user.id)

            # Default user makes request for user data 
            response = self.client.get(
                '/api/status/2',
                headers=dict(
                    Authorization='Bearer ' + str(aut_token, 'UTF-8')
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Access denied.')