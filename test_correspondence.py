#!/usr/bin/env python3
"""
Test script to verify private key and address correspondence
"""
import sys
from gen_tron_address_real import private_key_to_tron_address

def test_correspondence():
    """Test known private key/address pairs"""
    print("Testing private key to address correspondence...")
    print("=" * 60)

    # Test cases - you can use these to verify in wallet tools
    test_cases = [
        "0000000000000000000000000000000000000000000000000000000000000001",
        "0000000000000000000000000000000000000000000000000000000000000002",
        "aabbccddaabbccddaabbccddaabbccddaabbccddaabbccddaabbccddaabbccdd",
        "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    ]

    for i, private_key in enumerate(test_cases, 1):
        address = private_key_to_tron_address(private_key)
        print(f"Test {i}:")
        print(f"  Private Key: {private_key}")
        print(f"  Address:     {address}")
        print()

    print("Instructions for verification:")
    print("1. Copy any private key above")
    print("2. Import it into TronLink, TronScan, or other Tron wallet")
    print("3. Check if the generated address matches")
    print("4. If they match, the implementation is correct!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        private_key = input("Enter private key to verify: ").strip()
        if len(private_key) == 64:
            address = private_key_to_tron_address(private_key)
            print(f"Private Key: {private_key}")
            print(f"Address:     {address}")
        else:
            print("Error: Private key must be 64 hex characters")
    else:
        test_correspondence()