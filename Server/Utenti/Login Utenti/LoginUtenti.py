from flask import Flask, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy.exc import IntegrityError
import logging
from logging.handlers import RotatingFileHandler
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'PSS2024!'
app.config['WTF_CSRF_TIME_LIMIT'] = timedelta(minutes=15)
app.config['SESSION_COOKIE_HTTPONLY'] = True 
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  
app.config['REMEMBER_COOKIE_HTTPONLY'] = True 
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)  
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'  
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
csrf.init_app(app)
CORS(app,supports_credentials=True)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["5 per minute", "20 per hour"]
)

handler = RotatingFileHandler('login_app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class UserSchema(Schema):
    email = fields.Email(required=True, validate=validate.Email())
    password = fields.Str(required=True, validate=validate.Length(min=8))

user_schema = UserSchema()

@app.before_request
def log_request_info():
    app.logger.info('Request: %s %s %s', request.remote_addr, request.method, request.url)
    app.logger.info('Headers: %s', request.headers)
    app.logger.info('Body: %s', request.get_data())

@app.after_request
def log_response_info(response):
    app.logger.info('Response status: %s', response.status)
    app.logger.info('Response body: %s', response.get_data(as_text=True))
    return response

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    try:
        data = request.get_json()
        assert data is not None, "No data provided"
        
        email = data.get('email')
        password = data.get('password')
        
        assert email is not None, "Email is missing"
        assert password is not None, "Password is missing"
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify(message="User does not exist"), 404
        
        if not bcrypt.check_password_hash(user.password_hash, password):
            app.logger.warning('Login attempt failed for user: %s', email)
            return jsonify(message="Incorrect email or password"), 401
        
        session.permanent = True
        session['user_id'] = user.id
        
        app.logger.info('User logged in: %s', email)
        return jsonify(message="Login successful!"), 200
    except AssertionError as e:
        app.logger.warning('Assertion error: %s', e)
        return jsonify(message=str(e)), 400
    except Exception as e:
        app.logger.error('Error logging in user: %s', e)
        return jsonify(message="Error: " + str(e)), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify(message="Logged out successfully"), 200

@app.route('/get_csrf_token', methods=['GET'])
def get_csrf_token():
    token = generate_csrf()
    return jsonify({'csrf_token': token})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
