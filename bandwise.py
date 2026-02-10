from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os
from datetime import datetime, timedelta
import speech_recognition as sr
from dotenv import load_dotenv

# backend/app.py

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///bandwise.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
db = SQLAlchemy(app)

# ===================== DATABASE MODELS =====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    subscription_plan = db.Column(db.String(20), default='free')  # free, basic, premium
    subscription_end = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    native_language = db.Column(db.String(50))
    
    speaking_tests = db.relationship('SpeakingTest', backref='user', lazy=True)
    writing_tests = db.relationship('WritingTest', backref='user', lazy=True)
    mistakes = db.relationship('MistakeLog', backref='user', lazy=True)

class SpeakingTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    audio_file = db.Column(db.String(255))
    transcript = db.Column(db.Text)
    fluency_score = db.Column(db.Float)
    grammar_score = db.Column(db.Float)
    vocabulary_score = db.Column(db.Float)
    pronunciation_score = db.Column(db.Float)
    overall_band = db.Column(db.Float)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WritingTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    essay_text = db.Column(db.Text)
    task_response = db.Column(db.Float)
    coherence = db.Column(db.Float)
    lexical_resource = db.Column(db.Float)
    grammar = db.Column(db.Float)
    overall_band = db.Column(db.Float)
    corrections = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MistakeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mistake_type = db.Column(db.String(50))  # grammar, vocabulary, pronunciation
    error_text = db.Column(db.String(255))
    correction = db.Column(db.String(255))
    frequency = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ===================== AUTHENTICATION ROUTES =====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        native_language=data.get('native_language', 'English')
    )
    db.session.add(user)
    db.session.commit()
    
    token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(days=30)}, app.config['SECRET_KEY'])
    return jsonify({'token': token, 'user_id': user.id}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(days=30)}, app.config['SECRET_KEY'])
    return jsonify({'token': token, 'user_id': user.id}), 200

# ===================== SUBSCRIPTION ROUTES =====================

@app.route('/api/subscription/upgrade', methods=['POST'])
def upgrade_subscription():
    data = request.json
    user_id = data['user_id']
    plan = data['plan']  # basic or premium
    
    user = User.query.get(user_id)
    user.subscription_plan = plan
    user.subscription_end = datetime.utcnow() + timedelta(days=365)
    db.session.commit()
    
    return jsonify({'message': f'Upgraded to {plan}', 'subscription_end': user.subscription_end}), 200

# ===================== SPEAKING ROUTES =====================

@app.route('/api/speaking/upload', methods=['POST'])
def upload_speaking():
    user_id = request.form.get('user_id')
    audio_file = request.files['audio']
    
    filename = f"speaking_{user_id}_{datetime.utcnow().timestamp()}.wav"
    audio_file.save(f"uploads/{filename}")
    
    # Speech to Text
    recognizer = sr.Recognizer()
    with sr.AudioFile(f"uploads/{filename}") as source:
        audio = recognizer.record(source)
        transcript = recognizer.recognize_google(audio)
    
    # Analyze and score
    speaking_test = SpeakingTest(
        user_id=user_id,
        audio_file=filename,
        transcript=transcript,
        fluency_score=7.5,  # TODO: Implement real analysis
        grammar_score=7.0,
        vocabulary_score=7.5,
        pronunciation_score=7.0,
        overall_band=7.2
    )
    db.session.add(speaking_test)
    db.session.commit()
    
    return jsonify({
        'test_id': speaking_test.id,
        'transcript': transcript,
        'band_scores': {
            'fluency': speaking_test.fluency_score,
            'grammar': speaking_test.grammar_score,
            'vocabulary': speaking_test.vocabulary_score,
            'pronunciation': speaking_test.pronunciation_score,
            'overall': speaking_test.overall_band
        }
    }), 200

# ===================== WRITING ROUTES =====================

@app.route('/api/writing/submit', methods=['POST'])
def submit_writing():
    data = request.json
    user_id = data['user_id']
    essay_text = data['essay_text']
    
    # TODO: Implement real IELTS essay scoring
    writing_test = WritingTest(
        user_id=user_id,
        essay_text=essay_text,
        task_response=7.0,
        coherence=7.5,
        lexical_resource=7.0,
        grammar=7.5,
        overall_band=7.2,
        corrections=[]
    )
    db.session.add(writing_test)
    db.session.commit()
    
    return jsonify({
        'test_id': writing_test.id,
        'scores': {
            'task_response': writing_test.task_response,
            'coherence': writing_test.coherence,
            'lexical_resource': writing_test.lexical_resource,
            'grammar': writing_test.grammar,
            'overall': writing_test.overall_band
        }
    }), 200

# ===================== DASHBOARD ROUTES =====================

@app.route('/api/dashboard/<int:user_id>', methods=['GET'])
def get_dashboard(user_id):
    user = User.query.get(user_id)
    speaking_tests = SpeakingTest.query.filter_by(user_id=user_id).all()
    writing_tests = WritingTest.query.filter_by(user_id=user_id).all()
    mistakes = MistakeLog.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'user': {'username': user.username, 'subscription': user.subscription_plan},
        'speaking_tests_count': len(speaking_tests),
        'writing_tests_count': len(writing_tests),
        'avg_speaking_band': sum([t.overall_band for t in speaking_tests]) / len(speaking_tests) if speaking_tests else 0,
        'avg_writing_band': sum([t.overall_band for t in writing_tests]) / len(writing_tests) if writing_tests else 0,
        'frequent_mistakes': [(m.error_text, m.frequency) for m in sorted(mistakes, key=lambda x: x.frequency, reverse=True)[:5]]
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)