# 🔐 Privacy Risk Detection System

Real-time API that analyzes verification requests and detects privacy-invasive data collection.

---

## 🎯 What It Does

Checks if a verification request is asking for too much personal information.

**Examples:**
- ✅ "Verify age over 18" → **Safe** (not intrusive)
- ⚠️ "Provide your first name and city" → **Medium Risk** (somewhat sensitive)
- 🚨 "Share full name, address, and phone number" → **High Risk** (very intrusive)

---

## ⚡ Quick Start

### Install Dependencies
```bash
pip install flask flask-cors
```

### Run the API
```bash
python privacy_risk_detector.py
```

API will start at: `http://localhost:5000`

---

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

### 1. `/check_risk` – Analyze Single Request
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

### 2. `/batch_check` – Analyze Multiple Requests
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
