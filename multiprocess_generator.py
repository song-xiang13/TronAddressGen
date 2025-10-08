#!/usr/bin/env python3
"""
Multiprocessing Coincurve Generator
Use multiprocessing to bypass Python GIL for true parallelism
"""
import sys
import secrets
import multiprocessing
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

def worker_process(count_per_process):
    """Worker process function"""
    results = []

    for i in range(count_per_process):
        private_key_bytes = secrets.token_bytes(32)
        private_key_hex = private_key_bytes.hex()
        address = generate_address(private_key_bytes)

        if address:
            results.append((private_key_hex, address))

    return results

def test_multiprocessing(total_count, num_processes=None):
    """Test with multiprocessing"""
    if num_processes is None:
        num_processes = multiprocessing.cpu_count()

    print(f"🚀 Testing {total_count} addresses with {num_processes} processes...")
    print(f"📊 Expected rate: ~{27000 * num_processes:,} addresses/sec")

    count_per_process = total_count // num_processes

    start_time = time.time()

    # Create process pool and execute
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Submit tasks
        tasks = [count_per_process] * num_processes

        # Handle remainder
        remainder = total_count % num_processes
        if remainder > 0:
            tasks[0] += remainder

        print(f"📝 Task distribution: {tasks}")

        # Execute in parallel
        results = pool.map(worker_process, tasks)

    end_time = time.time()

    # Combine results
    all_results = []
    for result_list in results:
        all_results.extend(result_list)

    elapsed = end_time - start_time
    rate = len(all_results) / elapsed

    print(f"✅ Generated {len(all_results)} addresses in {elapsed:.2f} seconds")
    print(f"🎯 RATE: {rate:.0f} addresses/second")

    efficiency = (rate / (27000 * num_processes)) * 100
    print(f"📊 Efficiency: {efficiency:.1f}% of theoretical maximum")

    if rate >= 500000:
        print("🏆 TARGET ACHIEVED: 500k+ addresses/second!")
    elif rate >= 100000:
        multiplier = 500000 / rate
        print(f"🔥 Excellent progress! Need {multiplier:.1f}x more for 500k target")
    else:
        multiplier = 500000 / rate
        print(f"📈 Current: {rate:.0f}/sec (need {multiplier:.1f}x for 500k target)")

    return rate, all_results

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 multiprocess_generator.py <count> [processes] [output_file]")
        print("Example: python3 multiprocess_generator.py 50000 8 output.txt")
        sys.exit(1)

    try:
        count = int(sys.argv[1])
        num_processes = int(sys.argv[2]) if len(sys.argv) > 2 else None
        output_file = sys.argv[3] if len(sys.argv) > 3 else None

        if count <= 0 or count > 1000000:
            print("Error: Count must be between 1 and 1,000,000")
            sys.exit(1)

        rate, results = test_multiprocessing(count, num_processes)

        # Write to file if specified
        if output_file and results:
            print(f"💾 Writing to {output_file}...")
            with open(output_file, 'w') as f:
                for private_key, address in results:
                    f.write(f"{private_key},{address}\n")
            print(f"✅ Saved {len(results)} addresses to {output_file}")

    except KeyboardInterrupt:
        print("\n❌ Generation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()