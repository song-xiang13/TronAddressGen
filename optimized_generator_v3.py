#!/usr/bin/env python3
"""
Optimized Tron Address Generator v3
Focus on threading + coincurve optimization
Target: 500,000+ addresses per second
"""
import sys
import secrets
import concurrent.futures
import threading
import time
from queue import Queue
import hashlib

# Import the fastest crypto library available
try:
    import coincurve
    CRYPTO_LIB = "coincurve"
    print("✅ Using coincurve (fastest secp256k1)")
except ImportError:
    try:
        from ecdsa import SigningKey, SECP256k1
        CRYPTO_LIB = "ecdsa"
        print("⚠️  Using ecdsa (slower fallback)")
    except ImportError:
        print("❌ No crypto library available")
        sys.exit(1)

try:
    from Crypto.Hash import keccak
    KECCAK_LIB = "pycryptodome"
    print("✅ Using pycryptodome keccak")
except ImportError:
    import hashlib
    KECCAK_LIB = "hashlib"
    print("⚠️  Using hashlib sha3 (fallback)")

# Optimized constants
ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

class OptimizedGeneratorV3:
    def __init__(self, num_threads=32):
        self.num_threads = num_threads
        self.write_queue = Queue(maxsize=20000)
        self.stats_lock = threading.Lock()
        self.total_generated = 0

    def fast_keccak256(self, data):
        """Fastest keccak implementation"""
        if KECCAK_LIB == "pycryptodome":
            k = keccak.new(digest_bits=256)
            k.update(data)
            return k.digest()
        else:
            return hashlib.sha3_256(data).digest()

    def optimized_base58_encode(self, data):
        """Optimized base58 encoding with less overhead"""
        num = int.from_bytes(data, 'big')

        if num == 0:
            return ALPHABET[0]

        encoded = []
        while num > 0:
            num, remainder = divmod(num, 58)
            encoded.append(ALPHABET[remainder])

        # Count leading zeros
        leading_zeros = 0
        for byte in data:
            if byte == 0:
                leading_zeros += 1
            else:
                break

        return ALPHABET[0] * leading_zeros + ''.join(reversed(encoded))

    def ultra_fast_generation(self, private_key_bytes):
        """Ultra-optimized address generation"""
        try:
            if CRYPTO_LIB == "coincurve":
                # Use coincurve - much faster than ecdsa
                private_key = coincurve.PrivateKey(private_key_bytes)
                public_key_bytes = private_key.public_key.format(compressed=False)[1:]  # Remove 0x04 prefix
            else:
                # Fallback to ecdsa
                sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
                vk = sk.get_verifying_key()
                public_key_bytes = vk.to_string()

            # Keccak-256 hash
            keccak_hash = self.fast_keccak256(public_key_bytes)
            ethereum_address = keccak_hash[-20:]

            # Tron address
            tron_address_hex = b'\x41' + ethereum_address
            checksum = hashlib.sha256(hashlib.sha256(tron_address_hex).digest()).digest()[:4]
            full_address = tron_address_hex + checksum

            return self.optimized_base58_encode(full_address)
        except:
            return None

    def generate_batch_optimized(self, batch_size):
        """Generate batch with minimal overhead"""
        results = []
        for _ in range(batch_size):
            private_key_bytes = secrets.token_bytes(32)
            private_key_hex = private_key_bytes.hex()
            address = self.ultra_fast_generation(private_key_bytes)
            if address:
                results.append((private_key_hex, address))
        return results

    def worker_thread_optimized(self, total_count, batch_size, thread_id):
        """Optimized worker thread"""
        generated_count = 0

        while generated_count < total_count:
            current_batch_size = min(batch_size, total_count - generated_count)
            batch_results = self.generate_batch_optimized(current_batch_size)

            # Queue results
            for result in batch_results:
                self.write_queue.put(result)

            generated_count += current_batch_size

            # Update stats less frequently for performance
            if generated_count % 500 == 0:
                with self.stats_lock:
                    self.total_generated += len(batch_results)

    def writer_thread_optimized(self, output_file, total_target):
        """Optimized writer thread"""
        if not output_file:
            return

        written_count = 0
        buffer = []
        buffer_size = 2000

        with open(output_file, 'w') as f:
            while written_count < total_target:
                try:
                    item = self.write_queue.get(timeout=1)
                    if item is None:
                        break

                    buffer.append(f"{item[0]},{item[1]}\n")
                    written_count += 1

                    if len(buffer) >= buffer_size:
                        f.writelines(buffer)
                        f.flush()
                        buffer = []

                    self.write_queue.task_done()
                except:
                    continue

            if buffer:
                f.writelines(buffer)
                f.flush()

    def generate_optimized_v3(self, count, output_file=None):
        """Generate with optimized threading"""
        start_time = time.time()
        print(f"🚀 V3 OPTIMIZED: Generating {count} addresses with {self.num_threads} threads...")

        addresses_per_thread = count // self.num_threads
        batch_size = 200  # Smaller batches for better responsiveness

        # Start writer thread
        writer_future = None
        if output_file:
            writer_future = threading.Thread(
                target=self.writer_thread_optimized,
                args=(output_file, count)
            )
            writer_future.start()

        # Start worker threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = []

            for thread_id in range(self.num_threads):
                thread_count = addresses_per_thread
                if thread_id == self.num_threads - 1:
                    thread_count += count % self.num_threads

                future = executor.submit(
                    self.worker_thread_optimized,
                    thread_count,
                    batch_size,
                    thread_id
                )
                futures.append(future)

            # Monitor progress
            last_reported = 0
            while self.total_generated < count:
                time.sleep(0.1)
                current = self.total_generated

                if current >= last_reported + 5000:
                    elapsed = time.time() - start_time
                    rate = current / elapsed if elapsed > 0 else 0
                    progress = (current / count) * 100
                    print(f"  ⚡ {progress:.1f}% | {current} addresses | {rate:.0f}/sec")
                    last_reported = current

            concurrent.futures.wait(futures)

        # Signal writer to stop
        if writer_future:
            self.write_queue.put(None)
            writer_future.join()

        end_time = time.time()
        elapsed = end_time - start_time
        rate = count / elapsed

        print(f"✅ COMPLETED: {count} addresses in {elapsed:.2f} seconds")
        print(f"🎯 RATE: {rate:.0f} addresses/second")

        if rate >= 500000:
            print("🏆 TARGET ACHIEVED: 500k+ addresses/second!")
        elif rate >= 100000:
            print(f"🔥 Great progress! {rate:.0f}/sec (need {500000/rate:.1f}x more)")
        else:
            print(f"📈 Current: {rate:.0f}/sec (target: 500,000/sec)")

        return rate

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 optimized_generator_v3.py <count> [output_file] [threads]")
        print("Example: python3 optimized_generator_v3.py 50000 output.txt 32")
        sys.exit(1)

    try:
        count = int(sys.argv[1])
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        num_threads = int(sys.argv[3]) if len(sys.argv) > 3 else 32

        if count <= 0 or count > 10000000:
            print("Error: Count must be between 1 and 10,000,000")
            sys.exit(1)

        generator = OptimizedGeneratorV3(num_threads)
        rate = generator.generate_optimized_v3(count, output_file)

    except KeyboardInterrupt:
        print("\n❌ Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()