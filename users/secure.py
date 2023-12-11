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
        self.p = 0
        self.q = 0
        self.private_key = 0
        self.shared_secret = 0

    def find_primitive_root(self):
        print(1)
        for g in range(2, 6):  # Check if 2 or 3 is a primitive root
            print(g)
            if pow(g, self.p - 1, self.p) == 1 and all(
                    pow(g, k, self.p) != 1 for k in range(1, self.p - 1)):
                return g
        print(0)
        return None

    def primitive_check(self, g, p):
        L = []
        # Checks If The Entered Number Is A Primitive Root Or Not
        for i in range(1, p):
            L.append(pow(g, i) % p)
        for i in range(1, p):
            if L.count(i) > 1:
                L.clear()
                return -1
            return 1

    def generate_public_key(self):
        self.p = 32416190071
        # Generate a random number for q
        self.q = 2
        self.private_key = secrets.randbelow(self.p)
        self.public_key = pow(self.q, self.private_key, self.p)
        return self.public_key, self.p, self.q

    def compute_shared_secret(self, other_public_key):
        if self.private_key > 0 and self.p > 0:
            print(other_public_key)
            # self.shared_secret = pow(other_public_key, self.private_key, self.p)
            self.shared_secret = 100
            return self.shared_secret
        else:
            self.shared_secret = 0

    def get_key(self):
        return self.shared_secret


def hash_key(secret_key):
    secret_key = str(secret_key)
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(secret_key.encode())
    return digest.finalize()


def encrypt(text, key):
    # Convert the text to bytes
    data = text.encode()

    # Generate a random initialization vector (IV)
    iv = os.urandom(12)

    # Create a new AES-GCM cipher using the key
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv),
                    backend=default_backend())
    encryptor = cipher.encryptor()

    # Encrypt the data
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
        100000  # Recommended number of iterations for security
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
    # Compare the entered hash with the stored hash
    return entered_hash == password_bytes

def create_session_id(username):
    return hashlib.sha256(os.urandom(60) + username.encode()).hexdigest()