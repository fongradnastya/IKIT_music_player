import secrets
import sys
from sympy import randprime


def generate_dh_parameters():
    # Generate a 1024-bit prime number for p
    p = randprime(pow(10, 15), pow(10, 16))

    # Generate a random number for g
    g = secrets.randbelow(sys.maxsize)

    # Generate a private key
    private_key = secrets.randbelow(p)

    # Calculate the public key
    public_key = pow(g, private_key, p)

    return p, g, public_key
