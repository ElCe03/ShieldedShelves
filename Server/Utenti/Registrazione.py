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

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'PSS2024!'
app.config['WTF_CSRF_CHECK_DEFAULT'] = False
CORS(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
redis_store = Redis(host='localhost', port=6379)
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="redis://localhost:6379"
)
csrf = CSRFProtect(app)

handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class UserSchema(Schema):
    first_name = fields.Str(required=True, validate=validate.Length(min=1))
    last_name = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True, validate=validate.Email())
    password = fields.Str(required=True, validate=validate.Length(min=8))

user_schema = UserSchema()

@app.route('/register', methods=['POST'])
@csrf.exempt
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
        db.session.rollback()  # Rollback in case of error
        app.logger.error('Error registering user: %s', e)
        return jsonify(message="Error: " + str(e)), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
