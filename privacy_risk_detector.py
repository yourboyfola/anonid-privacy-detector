from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app) 

# ============================================
# PRIVACY RISK DETECTION ENGINE
# ============================================

class PrivacyRiskDetector:
    def __init__(self):
        # High-risk data points (very sensitive)
        self.high_risk_keywords = [
            'full name', 'complete name', 'real name',
            'home address', 'residential address', 'street address', 'physical address',
            'phone number', 'mobile number', 'telephone',
            'email address', 'email',
            'nin', 'national identification number',
            'bvn number', 'bank verification number',
            'passport number', 'driver license',
            'social security', 'tax id',
            'bank account', 'account number',
            'credit card', 'debit card',
            'date of birth', 'dob', 'birthday',
            'exact location', 'gps coordinates',
            'fingerprint', 'biometric', 'facial recognition',
            'medical record', 'health information', 'cvv', 'pin code', 'OTP'
        ]
        
        # Medium-risk keywords (somewhat sensitive)
        self.medium_risk_keywords = [
            'first name', 'last name', 'surname',
            'city', 'state', 'country',
            'workplace', 'employer', 'company name',
            'education', 'school attended',
            'marital status', 'gender',
            'income level', 'salary',
            'religion', 'tribe', 'ethnicity'
        ]
        
        # Safe keywords (non-sensitive verifications)
        self.safe_keywords = [
            'age verification', 'over 18', 'over 21', 'adult verification',
            'nigerian citizen', 'citizenship status',
            'bvn verified', 'nin verified', 'identity verified',
            'is registered', 'account exists',
            'eligible', 'qualified'
        ]
    
    def analyze_request(self, request_text):
        """
        Analyze a verification request and return risk level
        
        Returns:
            dict: {
                'risk_level': 'Safe'|'Medium'|'High',
                'risk_score': 0-100,
                'flags': [...],
                'recommendation': '...'
            }
        """
        request_text = request_text.lower()
        
        # Check for safe patterns first
        safe_matches = [kw for kw in self.safe_keywords if kw in request_text]
        high_risk_matches = [kw for kw in self.high_risk_keywords if kw in request_text]
        medium_risk_matches = [kw for kw in self.medium_risk_keywords if kw in request_text]
        
        # Calculate risk score
        risk_score = 0
        flags = []
        
        # High risk: 30 points each
        if high_risk_matches:
            risk_score += len(high_risk_matches) * 30
            flags.extend([f"🚨 Requesting: {match}" for match in high_risk_matches])
        
        # Medium risk: 15 points each
        if medium_risk_matches:
            risk_score += len(medium_risk_matches) * 15
            flags.extend([f"⚠️ Requesting: {match}" for match in medium_risk_matches])
        
        # Safe patterns reduce score
        if safe_matches and not high_risk_matches:
            risk_score = max(0, risk_score - 20)
        
        # Cap at 100
        risk_score = min(100, risk_score)
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "High"
            color = "red"
            recommendation = "⛔ DENY - This request is highly intrusive and compromises user privacy."
        elif risk_score >= 30:
            risk_level = "Medium"
            color = "orange"
            recommendation = "⚠️ CAUTION - Review carefully. Consider if this data is truly necessary."
        else:
            risk_level = "Safe"
            color = "green"
            recommendation = "✅ APPROVED - This verification respects user privacy."
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'color': color,
            'flags': flags if flags else ["✅ No privacy concerns detected"],
            'recommendation': recommendation,
            'safe_matches': safe_matches,
            'analysis': {
                'high_risk_items': len(high_risk_matches),
                'medium_risk_items': len(medium_risk_matches),
                'safe_items': len(safe_matches)
            }
        }

# Initialize detector
detector = PrivacyRiskDetector()

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/')
def home():
    return jsonify({
        'service': 'AnonID Privacy Risk Detection API',
        'version': '1.0',
        'status': 'active',
        'endpoints': {
            '/check_risk': 'POST - Analyze privacy risk of a verification request',
            '/batch_check': 'POST - Analyze multiple requests',
            '/risk_stats': 'GET - Get system statistics'
        }
    })

@app.route('/check_risk', methods=['POST'])
def check_risk():
    """
    Analyze a single verification request
    
    Request body:
    {
        "request_text": "Please provide your full name and address"
    }
    """
    try:
        data = request.json
        
        if not data or 'request_text' not in data:
            return jsonify({
                'error': 'Missing request_text field'
            }), 400
        
        request_text = data['request_text']
        
        if not request_text or len(request_text.strip()) == 0:
            return jsonify({
                'error': 'request_text cannot be empty'
            }), 400
        
        # Analyze the request
        result = detector.analyze_request(request_text)
        result['original_request'] = request_text
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/batch_check', methods=['POST'])
def batch_check():
    """
    Analyze multiple verification requests at once
    
    Request body:
    {
        "requests": [
            "Verify age over 18",
            "Provide full name and phone number"
        ]
    }
    """
    try:
        data = request.json
        
        if not data or 'requests' not in data:
            return jsonify({
                'error': 'Missing requests field'
            }), 400
        
        requests = data['requests']
        
        if not isinstance(requests, list):
            return jsonify({
                'error': 'requests must be a list'
            }), 400
        
        # Analyze each request
        results = []
        for req_text in requests:
            result = detector.analyze_request(req_text)
            result['original_request'] = req_text
            results.append(result)
        
        # Calculate summary stats
        high_risk_count = sum(1 for r in results if r['risk_level'] == 'High')
        medium_risk_count = sum(1 for r in results if r['risk_level'] == 'Medium')
        safe_count = sum(1 for r in results if r['risk_level'] == 'Safe')
        
        return jsonify({
            'results': results,
            'summary': {
                'total': len(results),
                'high_risk': high_risk_count,
                'medium_risk': medium_risk_count,
                'safe': safe_count
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Batch analysis failed: {str(e)}'
        }), 500

@app.route('/risk_stats', methods=['GET'])
def risk_stats():
    """Get information about the detection system"""
    return jsonify({
        'system': 'Privacy Risk Detection Engine',
        'version': '1.0',
        'methodology': 'Heuristic keyword-based scoring',
        'metrics': {
            'high_risk_keywords_count': len(detector.high_risk_keywords),
            'medium_risk_keywords_count': len(detector.medium_risk_keywords),
            'safe_patterns_count': len(detector.safe_keywords)
        },
        'scoring': {
            'high_risk_weight': 30,
            'medium_risk_weight': 15,
            'safe_pattern_bonus': -20,
            'thresholds': {
                'high_risk': '≥60',
                'medium_risk': '30-59',
                'safe': '<30'
            }
        }
    })

# ============================================
# TEST FUNCTION (Run this to verify it works)
# ============================================

def run_tests():
    """Test the detector with sample requests"""
    print("\n" + "="*60)
    print("🧪 TESTING PRIVACY RISK DETECTOR")
    print("="*60 + "\n")
    
    test_cases = [
        "Verify user is over 18 years old",
        "Confirm BVN exists and is verified",
        "Please provide your full name and phone number",
        "Share your home address, email, and date of birth",
        "Verify Nigerian citizenship status",
        "Request: Full name, NIN, phone number, bank account number, and residential address"
    ]
    
    for i, test_request in enumerate(test_cases, 1):
        print(f"Test {i}: {test_request}")
        result = detector.analyze_request(test_request)
        print(f"  Risk Level: {result['risk_level']} ({result['risk_score']}/100)")
        print(f"  Flags: {len(result['flags'])}")
        for flag in result['flags'][:3]:  # Show first 3 flags
            print(f"    - {flag}")
        print(f"  Recommendation: {result['recommendation']}")
        print()

if __name__ == '__main__':
    # Run tests first
    run_tests()
    
    # Start the API server
    print("\n" + "="*60)
    print("🚀 STARTING API SERVER")
    print("="*60)
    print("\nAPI will be available at: http://localhost:5000")
    print("Test it with: curl -X POST http://localhost:5000/check_risk -H 'Content-Type: application/json' -d '{\"request_text\":\"Verify age over 18\"}'")
    print("\n")
    
    app.run(debug=True, port=5000)