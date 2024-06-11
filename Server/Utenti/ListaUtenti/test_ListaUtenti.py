import unittest
from flask import Flask, json
from ListaUtenti import app, db, User

class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_csrf_token(self):
        with app.app_context():
            response = self.app.get('/get_csrf_token')
            self.assertEqual(response.status_code, 200)

    def test_get_users(self):
        with app.app_context():
            user = User(first_name="John", last_name="Doe", email="john@example.com", password_hash="fake_hash")
            db.session.add(user)
            db.session.commit()

            response = self.app.get('/users')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.get_data(as_text=True))
            self.assertTrue(len(data) > 0)

    def test_update_user(self):
        with app.app_context():
            user = User(first_name="John", last_name="Doe", email="john@example.com", password_hash="fake_hash")
            db.session.add(user)
            db.session.commit()

            new_data = {'first_name': 'Jane'}
            response = self.app.put('/users/1', json=new_data)
            self.assertEqual(response.status_code, 200)

    def test_delete_user(self):
        with app.app_context():
            user = User(first_name="John", last_name="Doe", email="john@example.com", password_hash="fake_hash")
            db.session.add(user)
            db.session.commit()

            response = self.app.delete('/users/1')
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
