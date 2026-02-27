from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import math

app = Flask(__name__)
CORS(app)

def load_weak_passwords():
    try:
        with open('weak_passwords.txt', 'r') as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        return set()

weak_passwords = load_weak_passwords()

def calculate_entropy(password):
    """Calculate password entropy"""
    charset_size = 0
    if re.search(r'[a-z]', password):
        charset_size += 26
    if re.search(r'[A-Z]', password):
        charset_size += 26
    if re.search(r'[0-9]', password):
        charset_size += 10
    if re.search(r'[^a-zA-Z0-9]', password):
        charset_size += 32
    
    if charset_size == 0:
        return 0
    
    entropy = len(password) * math.log2(charset_size)
    return entropy

def check_password_strength(password):
    """Check password strength and return detailed feedback"""
    
    if not password:
        return {
            'strength': 'None',
            'score': 0,
            'entropy': 0,
            'feedback': ['Password cannot be empty'],
            'details': {
                'length': 0,
                'has_lowercase': False,
                'has_uppercase': False,
                'has_numbers': False,
                'has_special': False,
                'is_common': False
            }
        }
    
    score = 0
    feedback = []
    details = {
        'length': len(password),
        'has_lowercase': bool(re.search(r'[a-z]', password)),
        'has_uppercase': bool(re.search(r'[A-Z]', password)),
        'has_numbers': bool(re.search(r'[0-9]', password)),
        'has_special': bool(re.search(r'[^a-zA-Z0-9]', password)),
        'is_common': password.lower() in weak_passwords
    }
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append('Password should be at least 8 characters long')
    
    if len(password) >= 12:
        score += 1
    else:
        feedback.append('Consider using 12+ characters for better security')
    
    if details['has_lowercase']:
        score += 1
    else:
        feedback.append('Add lowercase letters')
    
    if details['has_uppercase']:
        score += 1
    else:
        feedback.append('Add uppercase letters')
    
    if details['has_numbers']:
        score += 1
    else:
        feedback.append('Add numbers')
    
    if details['has_special']:
        score += 1
    else:
        feedback.append('Add special characters')
    
    if details['is_common']:
        score = max(0, score - 2)
        feedback.append('This is a commonly used password')
    
    entropy = calculate_entropy(password)
    
    if score <= 2:
        strength = 'Weak'
    elif score <= 4:
        strength = 'Medium'
    elif score <= 5:
        strength = 'Strong'
    else:
        strength = 'Very Strong'
    
    return {
        'strength': strength,
        'score': score,
        'entropy': round(entropy, 2),
        'feedback': feedback if feedback else ['Password is strong!'],
        'details': details
    }

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Password Strength Checker API',
        'version': '1.0',
        'endpoints': {
            'POST /api/check': 'Check password strength',
            'GET /api/status': 'API status'
        }
    })

@app.route('/api/check', methods=['POST'])
def check_password():
    try:
        data = request.get_json()
        
        if not data or 'password' not in data:
            return jsonify({'error': 'Missing password field'}), 400
        
        password = data['password']
        result = check_password_strength(password)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'running',
        'message': 'API is working correctly'
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)