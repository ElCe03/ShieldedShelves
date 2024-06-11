from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import CSRFProtect
from flask_cors import CORS
from marshmallow import Schema, fields, validate
import logging
from logging.handlers import RotatingFileHandler
from redis import Redis
from flask_wtf.csrf import generate_csrf
import os
from sqlalchemy.exc import SQLAlchemyError

DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
SECRET_KEY = os.environ.get('SECRET_KEY')

assert all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]), "Variabili d'ambiente non configurate correttamente"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
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

@app.route('/get_csrf_token', methods=['GET'])
def get_csrf_token():
    token = generate_csrf()
    return jsonify({'csrf_token': token})

@app.route('/users', methods=['GET'])
@limiter.limit("10 per minute")
def get_users():
    try:
        users = User.query.all()
        return jsonify([{"id": user.id, "first_name": user.first_name, "last_name": user.last_name, "email": user.email} for user in users]), 200
    except SQLAlchemyError as se:
        app.logger.error('Errore durante il recupero degli utenti: %s', se)
        return jsonify(message="Errore durante il recupero degli utenti"), 500

@app.route('/users/<int:user_id>', methods=['PUT'])
@limiter.limit("5 per minute")
@csrf.exempt
def update_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify(message="Utente non trovato"), 404

        data = request.get_json()

        unauthorized_fields = set(data.keys()) - {'id', 'first_name', 'last_name', 'email'}
        if unauthorized_fields:
            return jsonify(message=f"Campi non consentiti: {', '.join(unauthorized_fields)}"), 400

        data.pop('id', None)

        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)

        db.session.commit()
        app.logger.info('Utente aggiornato: %s', user.email)
        return jsonify(message="Utente aggiornato con successo!"), 200
    except SQLAlchemyError as se:
        db.session.rollback()
        app.logger.error('Errore durante l\'aggiornamento dell\'utente: %s', se)
        return jsonify(message="Errore durante l'aggiornamento dell'utente"), 500
    except Exception as e:
        db.session.rollback()
        app.logger.error('Errore durante l\'aggiornamento dell\'utente: %s', e)
        return jsonify(message="Errore durante l'aggiornamento dell'utente"), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
@csrf.exempt
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify(message="Utente non trovato"), 404

        db.session.delete(user)
        db.session.commit()
        app.logger.info('Utente eliminato: %s', user.email)
        return jsonify(message="Utente eliminato con successo!"), 200
    except SQLAlchemyError as se:
        db.session.rollback()
        app.logger.error('Errore durante l\'eliminazione dell\'utente: %s', se)
        return jsonify(message="Errore durante l'eliminazione dell'utente"), 500
    except Exception as e:
        db.session.rollback()
        app.logger.error('Errore durante l\'eliminazione dell\'utente: %s', e)
        return jsonify(message="Errore durante l'eliminazione dell'utente"), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)
