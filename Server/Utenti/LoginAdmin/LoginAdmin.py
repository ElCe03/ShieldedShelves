from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf 
from flask_cors import CORS
from marshmallow import Schema, fields, validate, ValidationError
import logging
from logging.handlers import RotatingFileHandler
from redis import Redis
import os
import pyotp
from twilio.rest import Client
import base64


DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME2')
SECRET_KEY = os.environ.get('SECRET_KEY')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
SECRET_KEY_OTP=pyotp.random_base32()

assert all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, SECRET_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, SECRET_KEY_OTP]), "Environmental variables are not properly set"

app = Flask(__name__)
app.config['TESTING'] = os.environ.get('TESTING', False)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.config['WTF_CSRF_CHECK_DEFAULT'] = True
CORS(app, supports_credentials=True)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
redis_store = Redis(host='localhost', port=6379)
if not app.config['TESTING']:
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        storage_uri="redis://localhost:6379"
    )
else:
    limiter = Limiter(app, key_func=get_remote_address)
    limiter.enabled = False
csrf = CSRFProtect(app)
csrf.init_app(app)

handler = RotatingFileHandler('loginA_service.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

def create_admin(first_name, last_name, email, password, phone_number):
    try:
        with app.app_context():
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

            new_admin = Admin(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password_hash=password_hash,
                phone_number=phone_number
            )

            db.session.add(new_admin)
            db.session.commit()

        print("Amministratore registrato con successo!")
    except Exception as e:
        print(f"Si è verificato un errore durante la registrazione dell'amministratore: {str(e)}")

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)  

class LoginSchema(Schema):
    email = fields.Email(required=True, validate=validate.Email())
    password = fields.Str(required=True, validate=validate.Length(min=8))

class OtpSchema(Schema):
    email = fields.Email(required=True, validate=validate.Email())
    otp = fields.Str(required=True, validate=validate.Length(min=6, max=6))

login_schema = LoginSchema()
otp_schema = OtpSchema()

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
totp = pyotp.TOTP(base64.b32encode(SECRET_KEY_OTP.encode()).decode(), interval=180)

def send_otp_via_sms(user_phone_number, otp):
    try:
        message = client.messages.create(
            body=f'Your OTP code is {otp}',
            from_=TWILIO_PHONE_NUMBER,
            to=user_phone_number
        )
        app.logger.info("OTP message sent successfully!")
    except Exception as e:
        app.logger.error(f"Failed to send OTP message: {e}")
        raise

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
        
        login_schema.load(data)
        
        email = data.get('email')
        password = data.get('password')
        
        assert email is not None, "Email is missing"
        assert password is not None, "Password is missing"
        
        admin = Admin.query.filter_by(email=email).first()
        assert admin is not None, "User not found"
        
        assert bcrypt.check_password_hash(admin.password_hash, password), "Invalid credentials"
        
        otp = totp.now()
        send_otp_via_sms(admin.phone_number, otp)  
        
        app.logger.info('OTP sent to user: %s', email)
        return jsonify(message="OTP sent to your phone number"), 200
    except ValidationError as err:
        app.logger.warning('Validation error: %s', err.messages)
        return jsonify(err.messages), 400
    except AssertionError as e:
        app.logger.warning('Assertion error: %s', e)
        return jsonify(message=str(e)), 400
    except Exception as e:
        app.logger.error('Error logging in user: %s', e)
        return jsonify(message="Error: " + str(e)), 500


@app.route('/verify_otp', methods=['POST'])
@limiter.limit("5 per minute")
def verify_otp():
    try:
        data = request.get_json()
        assert data is not None, "No data provided"
        
        otp_schema.load(data)
        
        email = data.get('email')
        otp = data.get('otp')
        
        assert email is not None, "Email is missing"
        assert otp is not None, "OTP is missing"
        
        user = Admin.query.filter_by(email=email).first()
        assert user is not None, "User not found"
        assert totp.verify(otp), "Invalid OTP"
        
        token = f"token-{user.id}"
        
        app.logger.info('User verified with OTP: %s', email)
        return jsonify(message="Login successful", token=token), 200
    except ValidationError as err:
        app.logger.warning('Validation error: %s', err.messages)
        return jsonify(err.messages), 400
    except AssertionError as e:
        app.logger.warning('Assertion error: %s', e)
        return jsonify(message=str(e)), 400
    except Exception as e:
        app.logger.error('Error verifying OTP: %s', e)
        return jsonify(message="Error: " + str(e)), 500

@app.route('/get_csrf_token', methods=['GET'])
def get_csrf_token():
    token = generate_csrf()
    return jsonify({'csrf_token': token})

if __name__ == '__main__':
    create_admin("Nome", "Cognome", "esempio@email.com", "password123", "+393888086094")
    app.run(debug=True, port=5002)
