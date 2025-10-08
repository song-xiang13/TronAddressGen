#!/usr/bin/env python3
"""
Simple 4-Thread Coincurve Test
Test if threading works with coincurve at all
"""
import sys
import secrets
import threading
import time
import hashlib

try:
    import coincurve
    print("✅ Using coincurve")
except ImportError:
    print("❌ Coincurve required")
    sys.exit(1)

try:
    from Crypto.Hash import keccak
    print("✅ Using keccak")
except ImportError:
    print("❌ Keccak required")
    sys.exit(1)

ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# Global results storage
results = []
results_lock = threading.Lock()

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

def generate_address(private_key_bytes):
    """Generate address using coincurve"""
    try:
        private_key = coincurve.PrivateKey(private_key_bytes)
        public_key_bytes = private_key.public_key.format(compressed=False)[1:]

        k = keccak.new(digest_bits=256)
        k.update(public_key_bytes)
        keccak_hash = k.digest()
        ethereum_address = keccak_hash[-20:]

        tron_address_hex = b'\x41' + ethereum_address
        checksum = hashlib.sha256(hashlib.sha256(tron_address_hex).digest()).digest()[:4]
        full_address = tron_address_hex + checksum

        return fast_base58_encode(full_address)
    except:
        return None

def worker_simple(count_per_thread, thread_id):
    """Simple worker function"""
    local_results = []

    for i in range(count_per_thread):
        private_key_bytes = secrets.token_bytes(32)
        private_key_hex = private_key_bytes.hex()
        address = generate_address(private_key_bytes)

        if address:
            local_results.append((private_key_hex, address))

    # Add to global results
    with results_lock:
        results.extend(local_results)
        print(f"Thread {thread_id} completed: {len(local_results)} addresses")

def test_simple_threading(total_count):
    """Test with 4 simple threads"""
    print(f"🧪 Testing {total_count} addresses with 4 threads...")

    global results
    results = []

    threads = []
    count_per_thread = total_count // 4

    start_time = time.time()

    # Start 4 threads
    for i in range(4):
        thread = threading.Thread(target=worker_simple, args=(count_per_thread, i))
        threads.append(thread)
        thread.start()
        print(f"Started thread {i}")

    # Wait for all threads
    for i, thread in enumerate(threads):
        thread.join()
        print(f"Thread {i} finished")

    end_time = time.time()
    elapsed = end_time - start_time
    rate = len(results) / elapsed

    print(f"✅ Generated {len(results)} addresses in {elapsed:.2f} seconds")
    print(f"🎯 Rate: {rate:.0f} addresses/second")
    print(f"📊 Expected vs Actual: {27000 * 4} vs {rate:.0f}")

    return rate

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 simple_thread_test.py <count>")
        print("Example: python3 simple_thread_test.py 4000")
        sys.exit(1)

    try:
        count = int(sys.argv[1])
        if count <= 0 or count > 50000:
            print("Error: Count must be between 1 and 50,000")
            sys.exit(1)

        rate = test_simple_threading(count)

        if rate >= 100000:
            print("🔥 Great! Threading is working well")
        else:
            print("⚠️ Threading efficiency needs improvement")

    except KeyboardInterrupt:
        print("\n❌ Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()