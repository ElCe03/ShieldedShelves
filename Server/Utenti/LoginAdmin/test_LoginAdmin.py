import unittest
import json
from flask_testing import TestCase
from LoginAdmin import app, db, Admin, create_admin, totp

class BaseTestCase(TestCase):
    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['TESTING'] = True 
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        db.create_all()
        create_admin("Nome", "Cognome", "esempio@email.com", "password123", "+393888086094")

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class AdminModelTestCase(BaseTestCase):
    def test_create_admin(self):
        admin = Admin.query.filter_by(email="esempio@email.com").first()
        self.assertIsNotNone(admin)
        self.assertEqual(admin.first_name, "Nome")
        self.assertEqual(admin.last_name, "Cognome")
        self.assertEqual(admin.phone_number, "+393888086094")

class LoginTestCase(BaseTestCase):
    def test_login_success(self):
        response = self.client.post('/login', data=json.dumps({
            'email': 'esempio@email.com',
            'password': 'password123'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('OTP sent to your phone number', response.json['message'])

    def test_login_invalid_email(self):
        response = self.client.post('/login', data=json.dumps({
            'email': 'wrong@email.com',
            'password': 'password123'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('User not found', response.json['message'])

    def test_login_invalid_password(self):
        response = self.client.post('/login', data=json.dumps({
            'email': 'esempio@email.com',
            'password': 'wrongpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid credentials', response.json['message'])

class VerifyOtpTestCase(BaseTestCase):
    def test_verify_otp_success(self):
        self.client.post('/login', data=json.dumps({
            'email': 'esempio@email.com',
            'password': 'password123'
        }), content_type='application/json')

        otp = totp.now()
        response = self.client.post('/verify_otp', data=json.dumps({
            'email': 'esempio@email.com',
            'otp': otp
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Login successful', response.json['message'])

    def test_verify_otp_invalid(self):
        response = self.client.post('/verify_otp', data=json.dumps({
            'email': 'esempio@email.com',
            'otp': '123456'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid OTP', response.json['message'])

    def test_verify_otp_invalid_user(self):
        response = self.client.post('/verify_otp', data=json.dumps({
            'email': 'wrong@email.com',
            'otp': '123456'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('User not found', response.json['message'])

class CsrfTokenTestCase(BaseTestCase):
    def test_get_csrf_token(self):
        response = self.client.get('/get_csrf_token')
        self.assertEqual(response.status_code, 200)
        self.assertIn('csrf_token', response.json)

if __name__ == '__main__':
    unittest.main()