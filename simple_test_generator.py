#!/usr/bin/env python3
"""
Simple Coincurve Test Generator
Test coincurve performance vs ecdsa in single threaded mode
"""
import sys
import secrets
import time
import hashlib

# Test both libraries for comparison
try:
    import coincurve
    HAS_COINCURVE = True
    print("✅ Coincurve available")
except ImportError:
    HAS_COINCURVE = False
    print("❌ Coincurve not available")

try:
    from ecdsa import SigningKey, SECP256k1
    HAS_ECDSA = True
    print("✅ ECDSA available")
except ImportError:
    HAS_ECDSA = False
    print("❌ ECDSA not available")

try:
    from Crypto.Hash import keccak
    HAS_KECCAK = True
    print("✅ Keccak available")
except ImportError:
    HAS_KECCAK = False
    print("❌ Keccak not available")

ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def fast_base58_encode(data):
    """Optimized base58 encoding"""
    num = int.from_bytes(data, 'big')
    if num == 0:
        return ALPHABET[0]

    encoded = []
    while num > 0:
        num, remainder = divmod(num, 58)
        encoded.append(ALPHABET[remainder])

    leading_zeros = 0
    for byte in data:
        if byte == 0:
            leading_zeros += 1
        else:
            break

    return ALPHABET[0] * leading_zeros + ''.join(reversed(encoded))

def generate_with_coincurve(private_key_bytes):
    """Generate address using coincurve"""
    if not HAS_COINCURVE or not HAS_KECCAK:
        return None

    try:
        # Use coincurve
        private_key = coincurve.PrivateKey(private_key_bytes)
        public_key_bytes = private_key.public_key.format(compressed=False)[1:]  # Remove 0x04 prefix

        # Keccak-256
        k = keccak.new(digest_bits=256)
        k.update(public_key_bytes)
        keccak_hash = k.digest()
        ethereum_address = keccak_hash[-20:]

        # Tron address
        tron_address_hex = b'\x41' + ethereum_address
        checksum = hashlib.sha256(hashlib.sha256(tron_address_hex).digest()).digest()[:4]
        full_address = tron_address_hex + checksum

        return fast_base58_encode(full_address)
    except Exception as e:
        print(f"Coincurve error: {e}")
        return None

def generate_with_ecdsa(private_key_bytes):
    """Generate address using ecdsa"""
    if not HAS_ECDSA or not HAS_KECCAK:
        return None

    try:
        # Use ecdsa
        sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        public_key_bytes = vk.to_string()

        # Keccak-256
        k = keccak.new(digest_bits=256)
        k.update(public_key_bytes)
        keccak_hash = k.digest()
        ethereum_address = keccak_hash[-20:]

        # Tron address
        tron_address_hex = b'\x41' + ethereum_address
        checksum = hashlib.sha256(hashlib.sha256(tron_address_hex).digest()).digest()[:4]
        full_address = tron_address_hex + checksum

        return fast_base58_encode(full_address)
    except Exception as e:
        print(f"ECDSA error: {e}")
        return None

def test_speed(count, use_coincurve=True):
    """Test generation speed"""
    print(f"\n🧪 Testing {count} addresses with {'coincurve' if use_coincurve else 'ecdsa'}...")

    start_time = time.time()
    successful = 0

    for i in range(count):
        private_key_bytes = secrets.token_bytes(32)

        if use_coincurve:
            address = generate_with_coincurve(private_key_bytes)
        else:
            address = generate_with_ecdsa(private_key_bytes)

        if address:
            successful += 1

        # Show progress
        if (i + 1) % 100 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed
            print(f"  Generated {i + 1} | Rate: {rate:.0f}/sec")

    end_time = time.time()
    elapsed = end_time - start_time
    rate = successful / elapsed

    print(f"✅ Completed {successful} addresses in {elapsed:.2f} seconds")
    print(f"🎯 Rate: {rate:.0f} addresses/second")

    return rate

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 simple_test_generator.py <count>")
        print("Example: python3 simple_test_generator.py 1000")
        sys.exit(1)

    try:
        count = int(sys.argv[1])
        if count <= 0 or count > 100000:
            print("Error: Count must be between 1 and 100,000")
            sys.exit(1)

        # Test both if available
        if HAS_COINCURVE and HAS_KECCAK:
            coincurve_rate = test_speed(count, use_coincurve=True)
        else:
            print("❌ Cannot test coincurve")
            coincurve_rate = 0

        if HAS_ECDSA and HAS_KECCAK:
            ecdsa_rate = test_speed(count, use_coincurve=False)
        else:
            print("❌ Cannot test ecdsa")
            ecdsa_rate = 0

        # Compare results
        print(f"\n📊 COMPARISON:")
        if coincurve_rate > 0:
            print(f"  Coincurve: {coincurve_rate:.0f} addresses/sec")
        if ecdsa_rate > 0:
            print(f"  ECDSA:     {ecdsa_rate:.0f} addresses/sec")

        if coincurve_rate > 0 and ecdsa_rate > 0:
            improvement = coincurve_rate / ecdsa_rate
            print(f"  🚀 Coincurve is {improvement:.1f}x faster!")

    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()