import secrets
from sympy import randprime
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization, hashes, asymmetric
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend
import os


class DiffieHellman:
    def __init__(self):
        self.p = 0
        self.q = 0
        self.private_key = 0

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
            self.shared_secret = pow(other_public_key, self.private_key, self.p)
            encrypt_decrypt_example(self.shared_secret)
            return self.shared_secret
        else:
            self.shared_secret = 0



def encrypt_decrypt_example(secret_key):
    # Hash the secret key
    secret_key = str(secret_key)
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(secret_key.encode())
    hashed_key = digest.finalize()

    # The data to encrypt
    data = b'Hello, World!'

    # Generate a random initialization vector (IV)
    iv = os.urandom(12)

    # Create a new AES-GCM cipher using the hashed key
    cipher = Cipher(algorithms.AES(hashed_key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Encrypt the data
    encrypted_data = encryptor.update(data) + encryptor.finalize()

    print(encrypted_data)

    # Create a new AES-GCM cipher for decryption
    cipher = Cipher(algorithms.AES(hashed_key), modes.GCM(iv, encryptor.tag), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the data
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    print(decrypted_data.decode())