import unittest
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import CSRFProtect
from flask_cors import CORS
from marshmallow import Schema, fields, validate, ValidationError
from redis import Redis
from flask_wtf.csrf import generate_csrf
import logging
from logging.handlers import RotatingFileHandler
import os
from LoginUtenti import app, db, User, bcrypt, redis_store

class FlaskAppTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = True  
        cls.client = app.test_client()
        with app.app_context():
            db.create_all()
            user = User(
                first_name='John',
                last_name='Doe',
                email='john.doe@example.com',
                password_hash=bcrypt.generate_password_hash('password123').decode('utf-8')
            )
            db.session.add(user)
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.drop_all()

    def setUp(self):
        redis_store.flushall()

    def get_csrf_token(self):
        response = self.client.get('/get_csrf_token')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        return data['csrf_token']

    def test_successful_login(self):
        csrf_token = self.get_csrf_token()
        response = self.client.post('/login', json={
            'email': 'john.doe@example.com',
            'password': 'password123'
        }, headers={'X-CSRFToken': csrf_token})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertEqual(data['message'], 'Login successful')

    def test_login_user_not_found(self):
        csrf_token = self.get_csrf_token()
        response = self.client.post('/login', json={
            'email': 'notfound@example.com',
            'password': 'password123'
        }, headers={'X-CSRFToken': csrf_token})
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User not found')

    def test_login_invalid_credentials(self):
        csrf_token = self.get_csrf_token()
        response = self.client.post('/login', json={
            'email': 'john.doe@example.com',
            'password': 'wrongpassword'
        }, headers={'X-CSRFToken': csrf_token})
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Invalid credentials')

    def test_login_validation_error(self):
        csrf_token = self.get_csrf_token()
        response = self.client.post('/login', json={
            'email': 'invalid-email',
            'password': 'short'
        }, headers={'X-CSRFToken': csrf_token})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('email', data)
        self.assertIn('password', data)

    def test_login_missing_data(self):
        csrf_token = self.get_csrf_token()
        response = self.client.post('/login', json={}, headers={'X-CSRFToken': csrf_token})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('email', data)
        self.assertIn('password', data)

    def test_get_csrf_token(self):
        response = self.client.get('/get_csrf_token')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('csrf_token', data)

    def test_csrf_protection(self):
        csrf_token = self.get_csrf_token()
        response = self.client.post('/login', 
                                   json={'email': 'john.doe@example.com', 'password': 'password123'},
                                   headers={'X-CSRFToken': csrf_token})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertEqual(data['message'], 'Login successful')

    def test_rate_limiting(self):
        csrf_token = self.get_csrf_token()
        for _ in range(5):
            response = self.client.post('/login', json={
                'email': 'john.doe@example.com',
                'password': 'password123'
            }, headers={'X-CSRFToken': csrf_token})
            self.assertEqual(response.status_code, 200)
        
        response = self.client.post('/login', json={
            'email': 'john.doe@example.com',
            'password': 'password123'
        }, headers={'X-CSRFToken': csrf_token})
        self.assertEqual(response.status_code, 429)

if __name__ == '__main__':
    unittest.main()
