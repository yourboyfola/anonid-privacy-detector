# 🔐 AnonID Backend - Complete Integration Guide

## Overview

This backend integrates all components of the AnonID privacy-first identity authentication system:
- **AnonID Core**: AES-encrypted identity storage with NIN mapping
- **Privacy Risk Detector**: Real-time analysis of verification requests
- **Database**: SQLite storage for user identities and access logs
- **REST API**: Complete endpoints for authentication and data access

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Backend Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

### 3. Access the Frontend

Open your browser and go to: `http://localhost:5000/`

---

## 📁 Project Structure

```
anonid-privacy-detector/
├── app.py                          # Main Flask backend server
├── privacy_risk_detector.py       # Privacy risk analysis engine
├── requirements.txt                # Python dependencies
├── anonid_database.db              # SQLite database (auto-created)
├── frontend/                       # Frontend files
│   ├── index.html
│   ├── app.js                      # Updated to connect to backend
│   └── style.css
└── ANNON_ID E-D-V Files/          # AnonID core encryption module
    ├── anonid_core_aes.py
    ├── aes_utils.py
    ├── nimc_mock.py
    └── Demo.py
```

---

## 🔌 API Endpoints

### 1. Health Check
```http
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "AnonID Backend API",
  "version": "1.0.0",
  "database": "connected"
}
```

### 2. Register User with NIN
```http
POST /api/register
Content-Type: application/json

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

### 3. Verify Identity
```http
POST /api/verify
Content-Type: application/json

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
  "public_data": {
    "country": "Nigeria",
    "gender": "Female"
  },
  "risk_analysis": {
    "risk_level": "Safe",
    "risk_score": 0,
    "recommendation": "✅ APPROVED - This verification respects user privacy."
  }
}
```

### 4. Check Privacy Risk
```http
POST /api/check_privacy_risk
Content-Type: application/json

{
  "request_text": "Provide your full name and address"
}
```

**Response:**
```json
{
  "risk_level": "High",
  "risk_score": 60,
  "color": "red",
  "flags": [
    "🚨 Requesting: full name",
    "🚨 Requesting: home address"
  ],
  "recommendation": "⛔ DENY - This request is highly intrusive..."
}
```

### 5. Access User Data (with Privacy Check)
```http
POST /api/access_data
Content-Type: application/json

{
  "nin": "12345678901",
  "requested_fields": ["full name", "date of birth"],
  "verification_request": "Provide full name for verification"
}
```

**Response (if access granted):**
```json
{
  "access_granted": true,
  "data": {
    "full name": "Fatima Adeleke",
    "date of birth": "2000-04-12"
  },
  "risk_analysis": {
    "risk_level": "Medium",
    "risk_score": 45
  }
}
```

**Response (if access denied):**
```json
{
  "access_granted": false,
  "data": {},
  "risk_analysis": {
    "risk_level": "High",
    "risk_score": 75
  },
  "message": "Access denied - High privacy risk"
}
```

### 6. Get User by AnonID
```http
GET /api/user/<anon_id>
```

### 7. Get System Statistics
```http
GET /api/stats
```

---

## 🗄️ Database Schema

### `users` Table
Stores encrypted user identities mapped to NIN:
- `id`: Primary key
- `nin`: National Identification Number (unique)
- `anon_id`: Anonymous identifier (unique)
- `public_profile`: JSON of non-sensitive data
- `encrypted_sensitive`: JSON of encrypted sensitive data
- `salt`: Base64-encoded salt for key derivation
- `created_at`, `updated_at`: Timestamps

### `api_access_logs` Table
Tracks all API access attempts:
- `id`: Primary key
- `nin`: NIN of accessed user
- `endpoint`: API endpoint called
- `requested_fields`: JSON array of requested fields
- `access_granted`: Boolean
- `risk_level`: Risk level of request
- `risk_score`: Risk score
- `timestamp`: Access timestamp

### `organizations` Table
Tracks organizations using the API:
- `id`: Primary key
- `org_name`: Organization name
- `api_key`: API key for authentication
- `created_at`: Timestamp

---

## 🔒 Security Features

1. **AES-256-GCM Encryption**: All sensitive data is encrypted using authenticated encryption
2. **Privacy Risk Detection**: Automatic analysis of data requests
3. **Access Control**: High-risk requests are automatically denied
4. **Audit Logging**: All access attempts are logged
5. **NIN Masking**: NIN is never exposed in full (only masked format)

---

## 🔧 Configuration

### Environment Variables

- `ANONID_PASSPHRASE`: Passphrase for AES key derivation (default: "AnonID_demo_passphrase_2025")

Set in your environment:
```bash
export ANONID_PASSPHRASE="your-secure-passphrase"
```

### Database

The database is automatically created on first run at `anonid_database.db`. To reset:
```bash
rm anonid_database.db
python app.py  # Will recreate the database
```

---

## 🧪 Testing the System

### 1. Register a User
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"nin": "12345678901"}'
```

### 2. Verify Identity
```bash
curl -X POST http://localhost:5000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"nin": "12345678901", "verification_request": "Verify age over 18"}'
```

### 3. Check Privacy Risk
```bash
curl -X POST http://localhost:5000/api/check_privacy_risk \
  -H "Content-Type: application/json" \
  -d '{"request_text": "Provide your full name and phone number"}'
```

### 4. Access Data
```bash
curl -X POST http://localhost:5000/api/access_data \
  -H "Content-Type: application/json" \
  -d '{"nin": "12345678901", "requested_fields": ["full name"], "verification_request": "Provide full name"}'
```

---

## 📊 How It Works

1. **User Registration**:
   - User provides NIN
   - System fetches NIMC record (mock)
   - Data is classified into public/sensitive
   - Sensitive data is encrypted with AES-256-GCM
   - AnonID is generated
   - Everything is stored in database

2. **Identity Verification**:
   - User provides NIN and verification request
   - Privacy risk is analyzed
   - Only public data is returned
   - Access is logged

3. **Data Access**:
   - Organization requests specific fields
   - Privacy risk is analyzed
   - If risk is Safe/Medium: decrypt and return requested fields
   - If risk is High: deny access
   - All attempts are logged

---

## 🐛 Troubleshooting

### Backend won't start
- Check if port 5000 is available
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

### Module import errors
- Ensure `ANNON_ID E-D-V Files` directory is in the correct location
- Check that all files exist in that directory

### Database errors
- Delete `anonid_database.db` and restart
- Check file permissions

### Frontend can't connect
- Ensure backend is running on `http://localhost:5000`
- Check browser console for CORS errors
- Verify API endpoints are accessible

---

## 📝 Notes

- The system uses mock NIMC data (see `nimc_mock.py`)
- For production, replace with real NIMC API integration
- Database uses SQLite for simplicity; consider PostgreSQL for production
- All sensitive data is encrypted at rest
- API keys for organizations should be implemented for production use

---

## 🔮 Future Enhancements

- [ ] JWT-based authentication for API access
- [ ] Organization API key management
- [ ] Rate limiting
- [ ] Advanced analytics dashboard
- [ ] Real NIMC API integration
- [ ] Zero-knowledge proof support
- [ ] Multi-factor authentication

---

## 📞 Support

For issues or questions, check the code comments or contact the development team.

---

**License**: Private - AnonID Privacy-First Identity System

