from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import CSRFProtect
from flask_cors import CORS
from marshmallow import Schema, fields, validate, ValidationError
import logging
from logging.handlers import RotatingFileHandler
from redis import Redis
from flask_wtf.csrf import generate_csrf
import os

DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
SECRET_KEY = os.environ.get('SECRET_KEY')

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
        raise ValueError("variabili d'ambiente non configurate correttamente")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = {SECRET_KEY}
app.config['WTF_CSRF_CHECK_DEFAULT'] = True
CORS(app, supports_credentials=True)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
redis_store = Redis(host='localhost', port=6379)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)
csrf = CSRFProtect(app)
csrf.init_app(app)

handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
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
    first_name = fields.Str(required=True, validate=validate.Length(min=3))
    last_name = fields.Str(required=True, validate=validate.Length(min=3))
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

@app.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    try:
        data = request.get_json()
        assert data is not None, "No data provided"
        
        user_schema.load(data)
        
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')
        
        assert first_name is not None, "First name is missing"
        assert last_name is not None, "Last name is missing"
        assert email is not None, "Email is missing"
        assert password is not None, "Password is missing"
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify(message="User already exists"), 409  
        
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(first_name=first_name, last_name=last_name, email=email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
        
        app.logger.info('User registered: %s', email)
        return jsonify(message="User registered successfully!"), 201
    except ValidationError as err:
        app.logger.warning('Validation error: %s', err.messages)
        return jsonify(err.messages), 400
    except AssertionError as e:
        app.logger.warning('Assertion error: %s', e)
        return jsonify(message=str(e)), 400
    except Exception as e:
        db.session.rollback()  
        app.logger.error('Error registering user: %s', e)
        return jsonify(message="Error: " + str(e)), 500

@app.route('/get_csrf_token', methods=['GET'])
def get_csrf_token():
    token = generate_csrf()
    return jsonify({'csrf_token': token})

if __name__ == '__main__':
    app.run(debug=True)
