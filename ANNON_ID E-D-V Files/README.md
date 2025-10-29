# 🧩 AnonID – Privacy-First Digital Identity Encryption System

## 🔍 Overview
This project implements the **encryption and anonymization engine** for the **AnonID** prototype — a privacy-preserving digital identity system designed to protect personal data (such as NIN, BVN, and contact information) using AES encryption and selective data handling principles.

The system simulates integration with **NIMC records** (National Identity Management Commission) and allows secure creation of anonymized user identities without exposing sensitive details.

---

## 📁 Folder Contents

### 1. `aes_utils.py`
**Purpose:**  
Provides low-level AES-GCM encryption and decryption utilities using the `cryptography` library.

**Key Features:**
- 🔑 **Key Derivation (PBKDF2-HMAC-SHA256):**
  - Generates AES-256 keys from a passphrase with random salt.
- 🧱 **AES-GCM Encryption:**
  - Authenticated encryption ensuring both confidentiality and integrity.
- 🔓 **AES-GCM Decryption:**
  - Safely restores original data from the encrypted payload.
- 📦 **Outputs/Inputs:**
  - Encrypted blobs are stored as Base64-encoded JSON structures:
    ```json
    { "iv": "...", "ciphertext": "...", "tag": "..." }
    ```
- ⚙️ **Functions Provided:**
  - `generate_aes_key(passphrase, salt=None)`
  - `aes_encrypt(data_dict, key)`
  - `aes_decrypt(enc_blob, key)`

---

### 2. `anonid_core_aes.py`
**Purpose:**  
Core logic of the **AnonID engine** — connects to `nimc_mock.py`, classifies data by sensitivity, encrypts high-risk fields, and produces anonymized identity records.

**Key Features:**
- 🧩 **Integration with NIMC Mock Data:**
  - Retrieves structured personal data via `get_nimc_record(nin)`.
- 🔍 **Risk-Based Data Classification:**
  - Splits each record into:
    - `public_profile` → safe / medium-risk fields (stored in plain text)
    - `encrypted_sensitive` → high-risk fields (AES-encrypted)
- 🔐 **AES-GCM Encryption via `aes_utils`:**
  - Encrypts only the fields tagged as high-risk (e.g. name, address, date of birth).
- 🆔 **Anonymous ID Generation:**
  - Produces a 12-character `anon_id` derived from the NIN and random nonce.
- 🧠 **Decryption Utility:**
  - `decrypt_sensitive()` decrypts the encrypted blob internally for audits.
- 🧮 **Demo Mode:**
  - Accepts a user-entered NIN, returns minimal public data:
    ```python
    { "anon_id": "<hash>", "masked_nin": "12*******01" }
    ```

**Core Functions:**
- `register_user_from_nin(nin)` → returns anonymized + encrypted record  
- `decrypt_sensitive(record)` → internal decryption (requires salt + key)

---

### 3. `nimc_mock.py`
**Purpose:**  
Simulated **NIMC identity dataset** using realistic fields and privacy-risk keyword naming conventions.

**Key Features:**
- 🧾 **Keyword-Based Field Names:**
  - Uses privacy-related keys like `"full name"`, `"date of birth"`, `"home address"`, `"phone number"`, etc.
- 🧍‍♂️ **Mock Records:**
  - Contains verified profiles for demonstration (3 entries by default).
- 🔎 **Data Retrieval Function:**
  - `get_nimc_record(nin)` → returns a subset of verified fields for encryption.

**Example Record:**
```json
{
  "nin": "12345678901",
  "full name": "Fatima Adeleke",
  "date of birth": "2000-04-12",
  "home address": "12 Adeola Street, Surulere, Lagos",
  "phone number": "+2348012345678",
  "country": "Nigeria"
}
```

---

## 🔧 How It Works (Process Flow)

1. **User provides NIN**
   ↓  
2. `get_nimc_record()` fetches verified identity from mock dataset  
   ↓  
3. `register_user_from_nin()` classifies data by sensitivity  
   ↓  
4. Sensitive fields → encrypted via AES-GCM  
   ↓  
5. AnonID generated (non-traceable)  
   ↓  
6. Output: `{ anon_id, public_profile, encrypted_sensitive, salt }`

---

## 🧠 Example Demo Output
```
Enter NIN to register: 12345678901

✅ Registration successful. Minimal public output:
{'anon_id': 'af92b45f2d9e', 'masked_nin': '12*******01'}
```

---

## 🧰 Requirements
- Python 3.8+
- `cryptography` library
  ```bash
  pip install cryptography
  ```

---

## 🚀 Future Extensions
- 🔗 Connect to live NIMC or NDPR-compliant APIs.
- 🪶 Implement real Zero-Knowledge Proof (ZKP) verification for selective disclosures.
- 🧩 Integrate with Flask backend and PowerBI analytics for end-to-end demo.

---

## 📜 License
Private- Anon ID E-D-V System. 
