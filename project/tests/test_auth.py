# project/tests/test_auth.py

import unittest
import json
import datetime

from project.server import db
from project.server.models import User
from project.tests.base import BaseTestCase


class TestAuthBlueprint(BaseTestCase):
    def test_registration(self):
        """ Test for user registration """
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully registered.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_registered_with_already_registered_user(self):
        """ Test registration with already registered email"""
        user = User(
            email='joe@gmail.com',
            password='test'
        )
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'User already exists. Please Log in.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 202)
        
    def test_registered_user_login(self):
        """ Test for login of registered-user login """
        with self.client:
            
            # user registration
            resp_register = self.client.post(
                '/auth/register',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='123456'
                )),
                content_type='application/json',
            )
            data_register = json.loads(resp_register.data.decode())

            # registered user login
            response = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged in.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

            # wrond email or password
            response = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='654321'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Wrong email or password.')
            self.assertFalse(data.get('auth_token'))
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 401)
    
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
            self.assertTrue(data['data']['user_id'] == 2)
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


if __name__ == '__main__':
    unittest.main()