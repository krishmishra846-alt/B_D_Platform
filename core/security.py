import hashlib
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()

# Generate or load a 256-bit key from your .env
SECRET_KEY = os.getenv("AES_SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = AESGCM.generate_key(bit_length=256).hex()
    print(f"Generated temp AES Key: {SECRET_KEY} (Save this in your .env!)")

aesgcm = AESGCM(bytes.fromhex(SECRET_KEY))

def encrypt_sensitive_data(plaintext: str) -> str:
    """Encrypts highly sensitive IDs using AES-256 GCM."""
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    return (nonce + ciphertext).hex()

def compute_photo_checksum(file_bytes: bytes) -> str:
    """Generates a SHA-256 hash of the photo."""
    return hashlib.sha256(file_bytes).hexdigest()