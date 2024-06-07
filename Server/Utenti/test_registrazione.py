from datetime import time
import unittest
import json
from Registrazione import app, db, User

class UserRegistrationTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['RATELIMIT_ENABLED'] = False  
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def get_csrf_token(self):
        response = self.app.get('/get_csrf_token')
        data = json.loads(response.data)
        return data['csrf_token']

    def test_register_user_success(self):
        csrf_token = self.get_csrf_token()
        response = self.app.post('/register', data=json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123',
            'csrf_token': csrf_token
        }), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertIn('User registered successfully!', response.get_data(as_text=True))

        user = User.query.filter_by(email='john.doe@example.com').first()
        self.assertIsNotNone(user)
        self.assertNotEqual(user.password_hash, 'password123')  

    def test_register_user_missing_first_name(self):
        csrf_token = self.get_csrf_token()
        response = self.app.post('/register', data=json.dumps({
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123',
            'csrf_token': csrf_token
        }), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('first_name', response.get_data(as_text=True))

    def test_register_user_invalid_email(self):
        csrf_token = self.get_csrf_token()
        response = self.app.post('/register', data=json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'not-an-email',
            'password': 'password123',
            'csrf_token': csrf_token
        }), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.get_data(as_text=True))

    def test_register_user_short_password(self):
        csrf_token = self.get_csrf_token()
        response = self.app.post('/register', data=json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'short',
            'csrf_token': csrf_token
        }), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.get_data(as_text=True))

    def test_register_user_duplicate_email(self):
        user = User(first_name='Jane', last_name='Doe', email='jane.doe@example.com', password_hash='passwordhash')
        with app.app_context():
            db.session.add(user)
            db.session.commit()

        csrf_token = self.get_csrf_token()
        response = self.app.post('/register', data=json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
            'password': 'password123',
            'csrf_token': csrf_token
        }), content_type='application/json')

        self.assertEqual(response.status_code, 500)
        self.assertIn('Error', response.get_data(as_text=True))

    def test_register_user_no_data(self):
        csrf_token = self.get_csrf_token()
        response = self.app.post('/register', data={}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('No data provided', response.get_data(as_text=True))

    def test_csrf_protection(self):
        with app.app_context():
            csrf_token = self.get_csrf_token()
            response = self.app.post('/register', data=json.dumps({
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'password': 'password123',
                'csrf_token': csrf_token
            }), content_type='application/json')

            self.assertEqual(response.status_code, 201)

            response = self.app.post('/register', data=json.dumps({
                'first_name': 'Jane',
                'last_name': 'Doe',
                'email': 'jane.doe@example.com',
                'password': 'password123'
            }), content_type='application/json')

            self.assertEqual(response.status_code, 400)
            self.assertIn('The CSRF token is missing.', response.get_data(as_text=True))

    def test_rate_limiting(self):
        for _ in range(5):
            csrf_token = self.get_csrf_token()
            response = self.app.post('/register', data=json.dumps({
                'first_name': 'John',
                'last_name': 'Doe',
                'email': f'john.doe@example.com',
                'password': 'password123',
                'csrf_token': csrf_token
            }), content_type='application/json')
            self.assertNotEqual(response.status_code, 429)

        csrf_token = self.get_csrf_token()
        response = self.app.post('/register', data=json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe6@example.com',
            'password': 'password123',
            'csrf_token': csrf_token
        }), content_type='application/json')
        self.assertEqual(response.status_code, 429)
        self.assertIn('rate limit exceeded', response.get_data(as_text=True))

    def test_performance(self):
        start_time = time.time()
        csrf_token = self.get_csrf_token()
        response = self.app.post('/register', data=json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe.performance@example.com',
            'password': 'password123',
            'csrf_token': csrf_token
        }), content_type='application/json')
        end_time = time.time()

        self.assertEqual(response.status_code, 201)
        duration = end_time - start_time
        app.logger.info(f'Registration request duration: {duration} seconds')
        self.assertLess(duration, 1)  

if __name__ == '__main__':
    unittest.main()
