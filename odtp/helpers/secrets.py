import secrets
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# Constants
SALT_SIZE = 16  # Salt size in bytes
IV_SIZE = 16    # Initialization vector size in bytes

def encrypt_text(text, password):
    """Encrypt a string and return the encrypted data along with salt and IV."""
    # Generate a salt and derive a key
    salt = secrets.token_bytes(SALT_SIZE)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = kdf.derive(password.encode())

    # Generate an IV and create a cipher
    iv = secrets.token_bytes(IV_SIZE)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Pad the text to match the block size
    data = text.encode('utf-8')
    pad_length = algorithms.AES.block_size // 8 - (len(data) % (algorithms.AES.block_size // 8))
    padded_data = data + bytes([pad_length]) * pad_length

    # Encrypt the data
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return salt, iv, encrypted_data

def decrypt_file(encrypted_file_path, password):
    """Decrypt an encrypted file and return the decrypted content."""
    with open(encrypted_file_path, "rb") as f:
        file_data = f.read()

    # Extract the salt, IV, and encrypted data
    salt = file_data[:16]  # First 16 bytes are the salt
    iv = file_data[16:32]  # Next 16 bytes are the IV
    encrypted_data = file_data[32:]  # The rest is the encrypted data

    # Derive the key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = kdf.derive(password.encode())

    # Create the cipher and decryptor
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt and remove padding
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    pad_length = decrypted_padded_data[-1]  # Last byte indicates padding length
    decrypted_data = decrypted_padded_data[:-pad_length]

    # Return the decrypted content as a string
    return decrypted_data.decode('utf-8')
