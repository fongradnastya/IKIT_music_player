import ast
import binascii
import hashlib
import secrets
from base64 import b64decode, b64encode

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os


class DiffieHellman:
    def __init__(self):
        self.p = 23
        self.q = 5
        self.private_key = 0
        self.shared_secret = 0

    def generate_public_key(self):
        self.private_key = secrets.randbelow(self.p)
        self.public_key = pow(self.q, self.private_key, self.p)
        return self.public_key, self.p, self.q

    def get_public_key(self):
        return self.public_key, self.p, self.q

    def compute_shared_secret(self, other_public_key):
        if self.private_key > 0 and self.p > 0:
            self.shared_secret = pow(other_public_key, self.private_key, self.p)
            print(self.p, self.q, self.private_key, self.public_key,
                  self.shared_secret)
            return self.shared_secret
        else:
            self.shared_secret = 0

    def get_shared_secret(self):
        return self.shared_secret


def hash_key(secret_key):
    secret_key = str(secret_key)
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(secret_key.encode())
    return digest.finalize()


def encrypt(text, key, iv=None):
    # Convert the text to bytes
    data = text.encode()
    # Generate a random initialization vector (IV)
    iv = b64decode(iv) if iv else os.urandom(12)
    # Create a new AES-GCM cipher using the key
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv),
                    backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()
    # Append the tag to the encrypted data
    encrypted_data_with_tag = encrypted_data + encryptor.tag
    # Convert the encrypted data with tag and IV to Base64 strings
    encrypted_data_with_tag_str = b64encode(encrypted_data_with_tag).decode()
    iv_str = b64encode(iv).decode()
    return encrypted_data_with_tag_str, iv_str


def decrypt(encrypted_text, key, iv):
    iv = b64decode(iv)
    # Decode the Base64 string back into bytes
    encrypted_data_with_tag = b64decode(encrypted_text)
    # Separate the encrypted data and the tag
    encrypted_data = encrypted_data_with_tag[:-16]
    tag = encrypted_data_with_tag[-16:]
    decoded = ""
    # Create a new AES-GCM cipher for decryption
    try:
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag),
                        backend=default_backend())
        decryptor = cipher.decryptor()
        # Decrypt the data
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        decoded = decrypted_data.decode()
    except InvalidTag:
        print("Impossible to decrypt")
    return decoded


def hash_password(password, salt=None):
    # Create a salt
    if not salt:
        salt = os.urandom(32)
    # Use the hashlib.pbkdf2_hmac method to get a secure hash
    key = hashlib.pbkdf2_hmac(
        'sha256',  # The hash digest algorithm to use
        password.encode('utf-8'),  # Convert the password to bytes
        salt,  # Provide the salt
        100000
    )
    return salt + key

def check_password(stored_password, entered_password):
    password_bytes = ast.literal_eval(stored_password)
    print(password_bytes)
    password_hex = binascii.hexlify(password_bytes).decode()
    print(password_hex)
    # Split the stored password into the salt and the hash
    salt = bytes.fromhex(password_hex[:64])
    # Hash the entered password with the stored salt
    entered_hash = hash_password(entered_password, salt)
    print(entered_hash)
    return entered_hash == password_bytes

def create_session_id(username):
    return hashlib.sha256(os.urandom(60) + username.encode()).hexdigest()