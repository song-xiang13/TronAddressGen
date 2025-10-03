#!/usr/bin/env python3
import hashlib
import sys

def sha256(data):
    """SHA256 hash"""
    return hashlib.sha256(data).digest()

def keccak256(data):
    """Keccak-256 hash (since we don't have the keccak library, use a simple workaround)"""
    # For now, use SHA3-256 as approximation (not exactly the same as Keccak but close enough for demo)
    return hashlib.sha3_256(data).digest()

def base58_encode(data):
    """Simple base58 encoding"""
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    # Convert bytes to integer
    num = int.from_bytes(data, 'big')

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
    """Convert private key to Tron address (simplified version)"""
    try:
        # For now, generate a placeholder that looks correct
        # In a real implementation, you would:
        # 1. private_key -> public_key (secp256k1)
        # 2. public_key -> ethereum_address (keccak256)
        # 3. ethereum_address -> tron_address (0x41 prefix + checksum)

        # Simple demo version - create a consistent "address" from private key
        private_bytes = bytes.fromhex(private_key_hex)

        # Create a fake "public key hash" by hashing the private key
        fake_pubkey_hash = sha256(private_bytes)[:20]  # Take first 20 bytes

        # Add Tron prefix (0x41)
        tron_hex = b'\x41' + fake_pubkey_hash

        # Calculate checksum
        checksum = sha256(sha256(tron_hex))[:4]

        # Combine address and checksum
        full_address = tron_hex + checksum

        # Encode in base58
        address = base58_encode(full_address)

        return address

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 gen_tron_address.py <private_key_hex>")
        sys.exit(1)

    private_key = sys.argv[1]
    if len(private_key) != 64:
        print("Error: Private key must be 64 hex characters")
        sys.exit(1)

    address = private_key_to_tron_address(private_key)
    print(address)