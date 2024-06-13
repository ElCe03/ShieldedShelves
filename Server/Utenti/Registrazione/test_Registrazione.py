import unittest
import json
from flask import Flask
from Registrazione import app, db, User
from unittest.mock import patch

class RegistrazioneTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_users.db'
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def setUp(self):
        self.client = self.app.test_client()
        self.client.testing = True

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()

    def get_csrf_token(self):
        response = self.client.get('/get_csrf_token')
        data = json.loads(response.data)
        return data['csrf_token']

    @patch('flask_limiter.extension.Limiter._check_request_limit')
    def test_register_success(self, mock_rate_limit):
        mock_rate_limit.return_value = True
        csrf_token = self.get_csrf_token()
        headers = {'X-CSRFToken': csrf_token, 'Content-Type': 'application/json'}
        response = self.client.post('/register', 
                                    data=json.dumps({
                                        'first_name': 'John',
                                        'last_name': 'Doe',
                                        'email': 'john0@example.com',
                                        'password': 'password123'
                                    }), headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertIn('User registered successfully!', str(response.data))

    @patch('flask_limiter.extension.Limiter._check_request_limit')
    def test_register_missing_fields(self, mock_rate_limit):
        mock_rate_limit.return_value = True
        csrf_token = self.get_csrf_token()
        headers = {'X-CSRFToken': csrf_token, 'Content-Type': 'application/json'}
        response = self.client.post('/register', 
                                    data=json.dumps({
                                        'first_name': 'John',
                                        'email': 'john@example.com',
                                        'password': 'password123'
                                    }), headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing data for required field', str(response.data))

    @patch('flask_limiter.extension.Limiter._check_request_limit')
    def test_register_existing_user(self, mock_rate_limit):
        mock_rate_limit.return_value = True
        with self.app.app_context():
            user = User(first_name='Jane', last_name='Doe', email='jane@example.com', password_hash='hashedpassword')
            db.session.add(user)
            db.session.commit()

        csrf_token = self.get_csrf_token()
        headers = {'X-CSRFToken': csrf_token, 'Content-Type': 'application/json'}
        response = self.client.post('/register', 
                                    data=json.dumps({
                                        'first_name': 'Jane',
                                        'last_name': 'Doe',
                                        'email': 'jane@example.com',
                                        'password': 'password123'
                                    }), headers=headers)
        self.assertEqual(response.status_code, 409)
        self.assertIn('User already exists', str(response.data))

    def test_rate_limit(self):
        csrf_token = self.get_csrf_token()
        headers = {'X-CSRFToken': csrf_token, 'Content-Type': 'application/json'}
        for _ in range(5):
            response = self.client.post('/register', 
                                        data=json.dumps({
                                            'first_name': 'John',
                                            'last_name': 'Doe',
                                            'email': 'john{}@example.com'.format(_),
                                            'password': 'password123'
                                        }), headers=headers)
        response = self.client.post('/register', 
                                    data=json.dumps({
                                        'first_name': 'John',
                                        'last_name': 'Doe',
                                        'email': 'john6@example.com',
                                        'password': 'password123'
                                    }), headers=headers)
        self.assertEqual(response.status_code, 429)
        self.assertIn('5 per 1 minute', str(response.data))

    def test_csrf_protection(self):
        response = self.client.post('/register', 
                                    data=json.dumps({
                                        'first_name': 'John',
                                        'last_name': 'Doe',
                                        'email': 'john@example.com',
                                        'password': 'password123'
                                    }), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('The CSRF token is missing.', str(response.data))
    @patch('flask_limiter.extension.Limiter._check_request_limit')
    def test_register_with_weak_password(self, mock_rate_limit):
        mock_rate_limit.return_value = True
        csrf_token = self.get_csrf_token()
        headers = {'X-CSRFToken': csrf_token, 'Content-Type': 'application/json'}
        response = self.client.post('/register', 
                                    data=json.dumps({
                                        'first_name': 'John',
                                        'last_name': 'Doe',
                                        'email': 'john7@example.com',
                                        'password': '123'
                                    }), headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Shorter than minimum length 8.', str(response.data))

    @patch('flask_limiter.extension.Limiter._check_request_limit')
    def test_register_with_invalid_email(self, mock_rate_limit):
        mock_rate_limit.return_value = True
        csrf_token = self.get_csrf_token()
        headers = {'X-CSRFToken': csrf_token, 'Content-Type': 'application/json'}
        response = self.client.post('/register', 
                                    data=json.dumps({
                                        'first_name': 'John',
                                        'last_name': 'Doe',
                                        'email': 'not-an-email',
                                        'password': 'password123'
                                    }), headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Not a valid email address', str(response.data))

if __name__ == '__main__':
    unittest.main()
