"""
AnonID core logic:
- Fetch NIMC mock record by NIN (nimc_mock.get_nimc_record)
- Categorize fields using keyword-risk lists
- Encrypt only high-risk fields using AES-GCM (aes_utils)
- Produce anonymized record with:
    { anon_id, public_profile, encrypted_sensitive_blob, salt (b64) }
"""

import os
import base64
import hashlib
import json
import secrets
from typing import Dict, Any, Tuple

from aes_utils import generate_aes_key, aes_encrypt, aes_decrypt
from nimc_mock import get_nimc_record  # uses keyword-based fields

# ------------------------
# Risk keyword groups (from your keyword list)
# ------------------------
HIGH_RISK_KEYWORDS = [
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

MEDIUM_RISK_KEYWORDS = [
    'first name', 'last name', 'surname',
    'city', 'state', 'country',
    'workplace', 'employer', 'company name',
    'education', 'school attended',
    'marital status', 'gender',
    'income level', 'salary',
    'religion', 'tribe', 'ethnicity'
]

SAFE_KEYWORDS = [
    'age verification', 'over 18', 'over 21', 'adult verification',
    'nigerian citizen', 'citizenship status',
    'bvn verified', 'nin verified', 'identity verified',
    'is registered', 'account exists',
    'eligible', 'qualified'
]

# ------------------------
# Key management for demo
# ------------------------

_DEMO_PASSPHRASE = os.environ.get("ANONID_PASSPHRASE", "AnonID_demo_passphrase_2025")


def _classify_fields(record: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Split record into public_profile (non-sensitive/medium) and sensitive_fields (high-risk).
    - Fields with keys matching HIGH_RISK_KEYWORDS are considered sensitive and will be encrypted.
    - The rest are put into public_profile (which can be used for lightweight display).
    """
    sensitive = {}
    public = {}
    for k, v in record.items():
        key_lower = k.lower()
        if any(hr == key_lower or hr in key_lower for hr in HIGH_RISK_KEYWORDS):
            sensitive[k] = v
        else:
            # keep medium or safe into public profile
            public[k] = v
    return public, sensitive


def _generate_anon_id(nin: str) -> str:
    """
    Generate an anonymized short id (non-guessable). We avoid storing raw NIN in outputs.
    Use a random nonce to ensure same NIN doesn't produce a stable public id for privacy.
    """
    nonce = secrets.token_hex(8)
    digest = hashlib.sha256(f"{nin}:{nonce}".encode("utf-8")).hexdigest()
    return digest[:12]  # 12 hex chars (48 bits) - short but unique for demo


def register_user_from_nin(nin: str) -> Dict[str, Any]:
    """
    Primary function Member 1 should expose.
    - Fetches NIMC record (dictionary using your keyword field names).
    - Splits into public_profile and sensitive_fields.
    - Derives AES key (returns salt to allow re-derive) and encrypts sensitive fields.
    - Returns anonymized record containing:
        {
            "anon_id": str,
            "public_profile": { ... },           # non-sensitive fields (not encrypted)
            "encrypted_sensitive": {iv,ciphertext,tag},   # base64 strings
            "salt": base64(salt)                 # required to re-derive key for decrypt
        }
    """
    nimc = get_nimc_record(nin)
    if not nimc:
        raise ValueError("NIN not found in NIMC records (mock).")

    # classify fields
    public_profile, sensitive_fields = _classify_fields(nimc)

    # If no sensitive fields (unlikely), still keep a minimal encrypted blob
    if not sensitive_fields:
        sensitive_fields = {"note": "no high-risk fields present"}

    # derive AES key and get salt
    key, salt = generate_aes_key(_DEMO_PASSPHRASE, salt=None)

    # encrypt sensitive fields
    enc_blob = aes_encrypt(sensitive_fields, key)

    anon_id = _generate_anon_id(nin)

    # Return a record that backend stores instead of raw identity details
    return {
        "anon_id": anon_id,
        "public_profile": public_profile,
        "encrypted_sensitive": enc_blob,
        "salt": base64.b64encode(salt).decode("utf-8")
    }


def decrypt_sensitive(encrypted_record: Dict[str, Any], passphrase: str = None) -> Dict[str, Any]:
    """
    For internal/audit use: decrypt the encrypted_sensitive blob.
    Requires the salt contained in the record and the passphrase (or use demo passphrase).
    Returns the sensitive fields dictionary.
    """
    if passphrase is None:
        passphrase = _DEMO_PASSPHRASE

    salt_b64 = encrypted_record.get("salt")
    if not salt_b64:
        raise ValueError("Missing salt in record; cannot derive key.")
    salt = base64.b64decode(salt_b64)

    key, _ = generate_aes_key(passphrase, salt=salt)
    enc_blob = encrypted_record.get("encrypted_sensitive")
    if not enc_blob:
        raise ValueError("No encrypted_sensitive blob found.")

    return aes_decrypt(enc_blob, key)


