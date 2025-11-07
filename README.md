# 🔐 AnonID - Privacy-First Identity Authentication System

A complete privacy-preserving identity authentication system for Nigeria that allows organizations to verify user identities without exposing sensitive personal information. The system uses NIN (National Identification Number) as the primary identifier and provides encrypted storage with privacy risk detection.

---

## 🎯 What It Does

**AnonID** provides a complete identity authentication system that:

1. **Registers Users with NIN**: Maps NIN to encrypted identity records
2. **Privacy Risk Detection**: Analyzes verification requests for privacy violations
3. **Secure Data Access**: Allows organizations to access data only through API calls with privacy checks
4. **Encrypted Storage**: All sensitive data is encrypted using AES-256-GCM
5. **Access Control**: Automatically denies high-risk data requests

**Examples:**
- ✅ "Verify age over 18" → **Safe** (not intrusive) - Access granted
- ⚠️ "Provide your first name and city" → **Medium Risk** - Access granted with caution
- 🚨 "Share full name, address, and phone number" → **High Risk** - Access denied

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Backend Server
```bash
python app.py
```

The server will start at: `http://localhost:5000`

### 3. Access the Frontend
Open your browser and navigate to: `http://localhost:5000/`

### 4. Register a User
1. Enter a NIN (e.g., `12345678901`) in the registration form
2. Click "Register" to create an encrypted identity record
3. You'll receive an AnonID and masked NIN

### 5. Test Privacy Risk Detection
1. Upload a document or enter text in the privacy scanner
2. The system will analyze and display privacy risks

---

## 📁 Project Structure

```
anonid-privacy-detector/
├── app.py                          # Main Flask backend server ⭐
├── privacy_risk_detector.py       # Privacy risk analysis engine
├── requirements.txt                # Python dependencies
├── anonid_database.db              # SQLite database (auto-created)
├── frontend/                       # Frontend web interface
│   ├── index.html
│   ├── app.js                      # Updated with backend integration
│   └── style.css
└── ANNON_ID E-D-V Files/          # AnonID core encryption module
    ├── anonid_core_aes.py         # Core encryption logic
    ├── aes_utils.py                # AES-GCM encryption utilities
    ├── nimc_mock.py                # Mock NIMC database
    └── Demo.py
```

## 📡 How to Use the API

### Test with Python
```python
import requests

response = requests.post('http://localhost:5000/check_risk', 
    json={'request_text': 'Verify user is over 18'})

print(response.json())
```

### Test with cURL
```bash
curl -X POST http://localhost:5000/check_risk \
  -H "Content-Type: application/json" \
  -d '{"request_text":"Verify age over 18"}'
```

---

## 📊 API Endpoints

### 1. `POST /api/register` – Register User with NIN
**Request:**
```json
{
  "nin": "12345678901"
}
```
**Response:**
```json
{
  "anon_id": "af92b45f2d9e",
  "masked_nin": "12*******01",
  "message": "User registered successfully",
  "status": "new"
}
```

### 2. `POST /api/verify` – Verify Identity
**Request:**
```json
{
  "nin": "12345678901",
  "verification_request": "Verify age over 18"
}
```
**Response:**
```json
{
  "verified": true,
  "anon_id": "af92b45f2d9e",
  "public_data": { "country": "Nigeria", "gender": "Female" },
  "risk_analysis": { "risk_level": "Safe", "risk_score": 0 }
}
```

### 3. `POST /api/check_privacy_risk` – Analyze Single Request
**POST**
```json
{
  "request_text": "Provide your full name and email"
}
```

**Response**
```json
{
  "risk_level": "High",
  "risk_score": 60,
  "color": "red",
  "flags": [
    "🚨 Requesting: full name",
    "🚨 Requesting: email address"
  ],
  "recommendation": "⛔ DENY - This request is highly intrusive..."
}
```

---

### 4. `POST /api/access_data` – Access User Data (with Privacy Check)
**Request:**
```json
{
  "nin": "12345678901",
  "requested_fields": ["full name"],
  "verification_request": "Provide full name for verification"
}
```
**Response:**
```json
{
  "access_granted": true,
  "data": { "full name": "Fatima Adeleke" },
  "risk_analysis": { "risk_level": "Medium", "risk_score": 30 }
}
```

### 5. `GET /api/user/<anon_id>` – Get User by AnonID
### 6. `GET /api/stats` – Get System Statistics

### Legacy Endpoints (from privacy_risk_detector.py):

### `/batch_check` – Analyze Multiple Requests
**POST**
```json
{
  "requests": [
    "Verify age over 18",
    "Provide full name and phone number"
  ]
}
```

**Response**
```json
{
  "results": [...],
  "summary": {
    "total": 2,
    "high_risk": 1,
    "medium_risk": 0,
    "safe": 1
  }
}
```

---

### 3. `/risk_stats` – Get Overall Risk Statistics
**GET** `/risk_stats`

### 4. `/` – Root Endpoint
**GET** `/`

---

## 🎨 Risk Levels Explained

| Risk Level | Score Range | Meaning | Action |
|-------------|-------------|----------|--------|
| 🟢 Safe | 0–29 | No privacy concerns | Approve |
| 🟡 Medium | 30–59 | Somewhat intrusive | Review carefully |
| 🔴 High | 60–100 | Very intrusive | Deny/Block |

---

## 🧪 Example Results

**Safe**
- "Verify age over 18" → Safe  
- "Confirm Nigerian citizenship" → Safe  

**Medium**
- "Provide your first name" → Medium  
- "Share your city and state" → Medium  

**High**
- "Provide full name and phone number" → High  
- "Share address, email, and NIN" → High  

---

## 🔌 Integration with Your Backend
```python
import requests

def check_privacy_risk(request_text):
    response = requests.post('http://localhost:5000/check_risk',
        json={'request_text': request_text})
    return response.json()
```

---

## 📋 Response Fields

| Field | Type | Description |
|--------|------|-------------|
| risk_level | string | "Safe", "Medium", or "High" |
| risk_score | number | 0–100 |
| color | string | "green", "orange", or "red" |
| flags | array | Privacy concerns detected |
| recommendation | string | What to do next |

---

## 🛠️ How It Works

Uses keyword-based detection to identify sensitive data requests.

**High-Risk Keywords (30 points)**  
> full name, phone number, email, address, NIN, BVN, bank account  

**Medium-Risk Keywords (15 points)**  
> first name, last name, city, state, gender, income  

**Safe Patterns (reduces score)**  
> "verify age", "confirm citizenship"

**Formula:**
```
Risk Score = (High × 30) + (Medium × 15) - (Safe × 20)
Final Score = min(100, Risk Score)
```

---

## 🚀 Features
✅ Real-time risk analysis  
✅ 40+ sensitive keywords monitored  
✅ Batch request support  
✅ Works offline  
✅ Lightweight and fast  

---

## 📁 Project Structure
```
privacy_risk_detector.py  # Main API file
README.md                 # Documentation
```

---

## 🔧 Requirements
- Python 3.7+
- Flask
- Flask-CORS

---

## 💡 Use Cases
- E-commerce checkout  
- Identity verification  
- Job applications  
- Apartment rentals  

---

## ❓ FAQ

**Q:** Does this use ML?  
**A:** No — it’s keyword-based, making it faster and more transparent.

**Q:** Can I edit keywords?  
**A:** Yes, inside the code (see `high_risk_keywords` and others).

---

## 📞 Support
For help or suggestions, contact the development team.

---

## 📝 License
**Private – Privacy Risk Detection System**
