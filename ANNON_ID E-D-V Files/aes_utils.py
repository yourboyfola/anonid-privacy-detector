# aes_utils.py
"""
AES-GCM utilities using cryptography.hazmat.
Provides:
- generate_aes_key(passphrase, salt=None) -> (key, salt)
- aes_encrypt(data_dict, key) -> dict with base64 iv/ciphertext/tag
- aes_decrypt(enc_blob, key) -> original dict
"""

import os
import json
import base64
from typing import Tuple, Dict, Any
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Recommended parameters
_KDF_ITERATIONS = 390000
_KEY_LENGTH = 32  # AES-256
_IV_LENGTH = 12   # 96-bit nonce for GCM


def generate_aes_key(passphrase: str, salt: bytes = None) -> Tuple[bytes, bytes]:
    """
    Derive an AES-256 key from a passphrase using PBKDF2 (SHA-256).
    Returns (key, salt). If salt=None, a random salt is generated.
    Store salt safely if you want to reuse the same key.
    """
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=_KEY_LENGTH,
        salt=salt,
        iterations=_KDF_ITERATIONS,
        backend=default_backend()
    )
    key = kdf.derive(passphrase.encode("utf-8"))
    return key, salt


def aes_encrypt(data: Dict[str, Any], key: bytes) -> Dict[str, str]:
    """
    Encrypt a dictionary with AES-GCM.
    Returns a dict: { "iv": base64, "ciphertext": base64, "tag": base64 }
    """
    iv = os.urandom(_IV_LENGTH)
    # Serialize plaintext
    plaintext = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    tag = encryptor.tag

    return {
        "iv": base64.b64encode(iv).decode("utf-8"),
        "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
        "tag": base64.b64encode(tag).decode("utf-8")
    }


def aes_decrypt(enc_blob: Dict[str, str], key: bytes) -> Dict[str, Any]:
    """
    Decrypt AES-GCM blob produced by aes_encrypt and return original dict.
    Expects keys: "iv", "ciphertext", "tag" (all base64 strings).
    """
    iv = base64.b64decode(enc_blob["iv"])
    ciphertext = base64.b64decode(enc_blob["ciphertext"])
    tag = base64.b64decode(enc_blob["tag"])

    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()

    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return json.loads(plaintext.decode("utf-8"))
