"""
Main Flask Backend Server for AnonID Privacy-First Identity System
Integrates all components: privacy risk detector, AnonID core, and database
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional

# Add the AnonID module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ANNON_ID E-D-V Files'))

# Import AnonID core functions
try:
    from anonid_core_aes import register_user_from_nin, decrypt_sensitive  # pyright: ignore[reportMissingImports]
except ImportError:
    print("Warning: Could not import anonid_core_aes. Make sure all dependencies are installed.")
    register_user_from_nin = None
    decrypt_sensitive = None

# Import privacy risk detector
from privacy_risk_detector import PrivacyRiskDetector

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# Initialize components
detector = PrivacyRiskDetector()

# Database setup
DB_PATH = 'anonid_database.db'

def init_database():
    """Initialize SQLite database for storing user identities"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table - stores encrypted identities mapped to NIN
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nin TEXT UNIQUE NOT NULL,
            anon_id TEXT UNIQUE NOT NULL,
            public_profile TEXT NOT NULL,
            encrypted_sensitive TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create api_access_logs table - tracks API access attempts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nin TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            requested_fields TEXT,
            access_granted BOOLEAN,
            risk_level TEXT,
            risk_score INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (nin) REFERENCES users(nin)
        )
    ''')
    
    # Create organizations table - for tracking which organizations access data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            org_name TEXT UNIQUE NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_user_by_nin(nin: str) -> Optional[Dict[str, Any]]:
    """Retrieve user record from database by NIN"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE nin = ?', (nin,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_user_by_anon_id(anon_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve user record from database by anon_id"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE anon_id = ?', (anon_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def save_user(nin: str, anon_id: str, public_profile: Dict, encrypted_sensitive: Dict, salt: str):
    """Save or update user identity in database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    public_profile_json = json.dumps(public_profile)
    encrypted_json = json.dumps(encrypted_sensitive)
    
    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (nin, anon_id, public_profile, encrypted_sensitive, salt, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (nin, anon_id, public_profile_json, encrypted_json, salt))
    
    conn.commit()
    conn.close()

def log_api_access(nin: str, endpoint: str, requested_fields: list, 
                   access_granted: bool, risk_level: str = None, risk_score: int = None):
    """Log API access attempts for audit trail"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    requested_fields_json = json.dumps(requested_fields) if requested_fields else None
    
    cursor.execute('''
        INSERT INTO api_access_logs 
        (nin, endpoint, requested_fields, access_granted, risk_level, risk_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nin, endpoint, requested_fields_json, access_granted, risk_level, risk_score))
    
    conn.commit()
    conn.close()

def mask_nin(nin: str) -> str:
    """Mask NIN for display (show first 2 and last 2 digits)"""
    if len(nin) <= 4:
        return '*' * len(nin)
    return f"{nin[:2]}{'*' * (len(nin) - 4)}{nin[-2:]}"

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/')
def index():
    """Serve frontend"""
    return send_from_directory('frontend', 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AnonID Backend API',
        'version': '1.0.0',
        'database': 'connected'
    }), 200

@app.route('/api/register', methods=['POST'])
def register_user():
    """
    Register a new user using their NIN
    Request: { "nin": "12345678901" }
    Response: { "anon_id": "...", "masked_nin": "12*******01", "message": "..." }
    """
    try:
        data = request.json
        if not data or 'nin' not in data:
            return jsonify({'error': 'NIN is required'}), 400
        
        nin = data['nin'].strip()
        
        if not nin:
            return jsonify({'error': 'NIN cannot be empty'}), 400
        
        # Check if user already exists
        existing = get_user_by_nin(nin)
        if existing:
            return jsonify({
                'anon_id': existing['anon_id'],
                'masked_nin': mask_nin(nin),
                'message': 'User already registered',
                'status': 'existing'
            }), 200
        
        # Register new user using AnonID core
        if not register_user_from_nin:
            return jsonify({'error': 'AnonID core module not available'}), 500
        
        try:
            record = register_user_from_nin(nin)
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        
        # Save to database
        save_user(
            nin=nin,
            anon_id=record['anon_id'],
            public_profile=record['public_profile'],
            encrypted_sensitive=record['encrypted_sensitive'],
            salt=record['salt']
        )
        
        return jsonify({
            'anon_id': record['anon_id'],
            'masked_nin': mask_nin(nin),
            'message': 'User registered successfully',
            'status': 'new'
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/verify', methods=['POST'])
def verify_identity():
    """
    Verify identity without exposing sensitive data
    Request: { "nin": "12345678901", "verification_request": "Verify age over 18" }
    Response: { "verified": true/false, "public_data": {...}, "risk_analysis": {...} }
    """
    try:
        data = request.json
        if not data or 'nin' not in data:
            return jsonify({'error': 'NIN is required'}), 400
        
        nin = data['nin'].strip()
        verification_request = data.get('verification_request', '')
        
        # Get user from database
        user = get_user_by_nin(nin)
        if not user:
            return jsonify({'error': 'NIN not found. Please register first.'}), 404
        
        # Analyze privacy risk of the verification request
        risk_analysis = None
        if verification_request:
            risk_analysis = detector.analyze_request(verification_request)
        
        # Return only public profile (no sensitive data)
        public_profile = json.loads(user['public_profile'])
        
        log_api_access(
            nin=nin,
            endpoint='/api/verify',
            requested_fields=['public_profile'],
            access_granted=True,
            risk_level=risk_analysis['risk_level'] if risk_analysis else None,
            risk_score=risk_analysis['risk_score'] if risk_analysis else None
        )
        
        return jsonify({
            'verified': True,
            'anon_id': user['anon_id'],
            'public_data': public_profile,
            'risk_analysis': risk_analysis,
            'message': 'Identity verified (public data only)'
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Verification failed: {str(e)}'}), 500

@app.route('/api/check_privacy_risk', methods=['POST'])
def check_privacy_risk():
    """
    Check privacy risk of a verification request
    Request: { "request_text": "Provide your full name and address" }
    Response: Privacy risk analysis
    """
    try:
        data = request.json
        if not data or 'request_text' not in data:
            return jsonify({'error': 'request_text is required'}), 400
        
        request_text = data['request_text']
        result = detector.analyze_request(request_text)
        result['original_request'] = request_text
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/access_data', methods=['POST'])
def access_data():
    """
    Access user data through API (with privacy risk check)
    Request: { 
        "nin": "12345678901",
        "requested_fields": ["full name", "date of birth"],
        "verification_request": "Provide full name for verification"
    }
    Response: { "access_granted": true/false, "data": {...}, "risk_analysis": {...} }
    """
    try:
        data = request.json
        if not data or 'nin' not in data:
            return jsonify({'error': 'NIN is required'}), 400
        
        nin = data['nin'].strip()
        requested_fields = data.get('requested_fields', [])
        verification_request = data.get('verification_request', '')
        
        # Get user
        user = get_user_by_nin(nin)
        if not user:
            return jsonify({'error': 'NIN not found'}), 404
        
        # Analyze privacy risk
        risk_analysis = None
        if verification_request:
            risk_analysis = detector.analyze_request(verification_request)
        elif requested_fields:
            # Create a request text from requested fields
            request_text = f"Provide {' and '.join(requested_fields)}"
            risk_analysis = detector.analyze_request(request_text)
        
        # Check if access should be granted based on risk
        access_granted = False
        returned_data = {}
        
        if risk_analysis:
            # Only grant access if risk is Safe or Medium
            if risk_analysis['risk_level'] in ['Safe', 'Medium']:
                access_granted = True
                # Decrypt sensitive data if needed
                if requested_fields:
                    try:
                        if decrypt_sensitive:
                            sensitive_data = decrypt_sensitive({
                                'encrypted_sensitive': json.loads(user['encrypted_sensitive']),
                                'salt': user['salt']
                            })
                            
                            # Only return requested fields
                            for field in requested_fields:
                                if field in sensitive_data:
                                    returned_data[field] = sensitive_data[field]
                                elif field in json.loads(user['public_profile']):
                                    returned_data[field] = json.loads(user['public_profile'])[field]
                    except Exception as e:
                        return jsonify({'error': f'Data decryption failed: {str(e)}'}), 500
            else:
                # High risk - deny access
                access_granted = False
        else:
            # No risk analysis - return public data only
            access_granted = True
            public_profile = json.loads(user['public_profile'])
            for field in requested_fields:
                if field in public_profile:
                    returned_data[field] = public_profile[field]
        
        # Log access attempt
        log_api_access(
            nin=nin,
            endpoint='/api/access_data',
            requested_fields=requested_fields,
            access_granted=access_granted,
            risk_level=risk_analysis['risk_level'] if risk_analysis else None,
            risk_score=risk_analysis['risk_score'] if risk_analysis else None
        )
        
        return jsonify({
            'access_granted': access_granted,
            'data': returned_data,
            'risk_analysis': risk_analysis,
            'message': 'Access granted' if access_granted else 'Access denied - High privacy risk'
        }), 200 if access_granted else 403
    
    except Exception as e:
        return jsonify({'error': f'Data access failed: {str(e)}'}), 500

@app.route('/api/user/<anon_id>', methods=['GET'])
def get_user_by_anon_id_endpoint(anon_id):
    """Get user public data by anon_id"""
    try:
        user = get_user_by_anon_id(anon_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        public_profile = json.loads(user['public_profile'])
        
        return jsonify({
            'anon_id': user['anon_id'],
            'masked_nin': mask_nin(user['nin']),
            'public_profile': public_profile,
            'created_at': user['created_at']
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve user: {str(e)}'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Total API accesses
        cursor.execute('SELECT COUNT(*) FROM api_access_logs')
        total_accesses = cursor.fetchone()[0]
        
        # Access granted vs denied
        cursor.execute('SELECT COUNT(*) FROM api_access_logs WHERE access_granted = 1')
        granted = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM api_access_logs WHERE access_granted = 0')
        denied = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total_users': total_users,
            'total_api_accesses': total_accesses,
            'access_granted': granted,
            'access_denied': denied,
            'grant_rate': f"{(granted/total_accesses*100):.1f}%" if total_accesses > 0 else "0%"
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500

# ============================================
# SERVER STARTUP
# ============================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 STARTING ANONID BACKEND SERVER")
    print("="*60)
    print("\nAPI will be available at: http://localhost:5000")
    print("Frontend will be available at: http://localhost:5000/")
    print("\nEndpoints:")
    print("  POST /api/register - Register user with NIN")
    print("  POST /api/verify - Verify identity")
    print("  POST /api/check_privacy_risk - Check privacy risk")
    print("  POST /api/access_data - Access user data via API")
    print("  GET  /api/user/<anon_id> - Get user by anon_id")
    print("  GET  /api/stats - Get system statistics")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')

