#!/usr/bin/env python3
import hashlib
import sys
from ecdsa import SigningKey, SECP256k1
from Crypto.Hash import keccak

def sha256(data):
    """SHA256 hash"""
    return hashlib.sha256(data).digest()

def keccak256(data):
    """Keccak-256 hash"""
    k = keccak.new(digest_bits=256)
    k.update(data)
    return k.digest()

def base58_encode(data):
    """Base58 encoding for Bitcoin/Tron addresses"""
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    # Convert bytes to integer
    num = int.from_bytes(data, 'big')

    # Handle zero case
    if num == 0:
        return alphabet[0]

    # Convert to base58
    encoded = ""
    while num > 0:
        num, remainder = divmod(num, 58)
        encoded = alphabet[remainder] + encoded

    # Handle leading zeros
    for byte in data:
        if byte == 0:
            encoded = alphabet[0] + encoded
        else:
            break

    return encoded

def private_key_to_tron_address(private_key_hex):
    """Convert private key to Tron address using correct cryptographic methods"""
    try:
        # Step 1: Convert hex private key to bytes
        private_key_bytes = bytes.fromhex(private_key_hex)

        # Step 2: Generate public key using secp256k1 elliptic curve
        sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()

        # Get uncompressed public key (64 bytes: 32 bytes x + 32 bytes y)
        public_key_bytes = vk.to_string()

        # Step 3: Calculate Ethereum address using Keccak-256
        # Take Keccak-256 hash of public key and take last 20 bytes
        keccak_hash = keccak256(public_key_bytes)
        ethereum_address = keccak_hash[-20:]  # Last 20 bytes

        # Step 4: Convert to Tron address
        # Add Tron prefix (0x41) to Ethereum address
        tron_address_hex = b'\x41' + ethereum_address

        # Step 5: Calculate checksum using double SHA-256
        checksum = sha256(sha256(tron_address_hex))[:4]  # First 4 bytes

        # Step 6: Combine address and checksum
        full_address = tron_address_hex + checksum

        # Step 7: Encode in Base58
        address = base58_encode(full_address)

        return address

    except Exception as e:
        return f"Error: {str(e)}"

def test_known_example():
    """Test with a known example"""
    # Known test case (you can verify this online)
    test_private_key = "aabbccddaabbccddaabbccddaabbccddaabbccddaabbccddaabbccddaabbccdd"
    test_address = private_key_to_tron_address(test_private_key)
    print(f"Test - Private: {test_private_key}")
    print(f"Test - Address: {test_address}")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--test":
        test_known_example()
        sys.exit(0)

    if len(sys.argv) != 2:
        print("Usage: python3 gen_tron_address_real.py <private_key_hex>")
        print("       python3 gen_tron_address_real.py --test")
        sys.exit(1)

    private_key = sys.argv[1]
    if len(private_key) != 64:
        print("Error: Private key must be 64 hex characters")
        sys.exit(1)

    try:
        # Validate hex
        int(private_key, 16)
    except ValueError:
        print("Error: Private key must be valid hexadecimal")
        sys.exit(1)

    address = private_key_to_tron_address(private_key)
    print(address)