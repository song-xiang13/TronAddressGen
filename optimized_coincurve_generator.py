#!/usr/bin/env python3
"""
Optimized Coincurve Multi-threaded Generator
Based on successful simple test, now add threading for 500k/sec target
"""
import sys
import secrets
import threading
import time
import queue
import hashlib

try:
    import coincurve
    print("✅ Using coincurve (27k+ addresses/sec per thread)")
except ImportError:
    print("❌ Coincurve required for optimal performance")
    sys.exit(1)

try:
    from Crypto.Hash import keccak
    print("✅ Using keccak")
except ImportError:
    print("❌ Keccak required")
    sys.exit(1)

ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

class OptimizedCoinCurveGenerator:
    def __init__(self, num_threads=20):
        self.num_threads = num_threads
        self.results_queue = queue.Queue(maxsize=10000)
        self.stats_lock = threading.Lock()
        self.total_generated = 0
        self.running = True

    def fast_base58_encode(self, data):
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

    def generate_address_optimized(self, private_key_bytes):
        """Generate address using optimized coincurve"""
        try:
            # Use coincurve - fastest secp256k1 implementation
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

            return self.fast_base58_encode(full_address)
        except:
            return None

    def worker_thread(self, addresses_to_generate, thread_id):
        """Worker thread - generate addresses continuously"""
        local_count = 0

        while local_count < addresses_to_generate and self.running:
            private_key_bytes = secrets.token_bytes(32)
            private_key_hex = private_key_bytes.hex()
            address = self.generate_address_optimized(private_key_bytes)

            if address:
                self.results_queue.put((private_key_hex, address))
                local_count += 1

                # Update global stats periodically
                if local_count % 100 == 0:
                    with self.stats_lock:
                        self.total_generated += 100

        # Add remaining count
        if local_count % 100 != 0:
            with self.stats_lock:
                self.total_generated += local_count % 100

    def writer_thread(self, output_file, total_target):
        """Writer thread for file output"""
        if not output_file:
            return

        written = 0
        buffer = []
        buffer_size = 1000

        with open(output_file, 'w') as f:
            while written < total_target and self.running:
                try:
                    item = self.results_queue.get(timeout=0.5)
                    if item is None:  # Poison pill
                        break

                    buffer.append(f"{item[0]},{item[1]}\n")
                    written += 1

                    if len(buffer) >= buffer_size:
                        f.writelines(buffer)
                        f.flush()
                        buffer = []

                except queue.Empty:
                    continue

            # Write remaining buffer
            if buffer:
                f.writelines(buffer)
                f.flush()

    def generate_multi_threaded(self, count, output_file=None):
        """Generate addresses with multiple threads"""
        start_time = time.time()
        print(f"🚀 Generating {count} addresses with {self.num_threads} threads...")
        print(f"📊 Expected rate: ~{27000 * self.num_threads:,} addresses/sec")

        # Calculate work distribution
        addresses_per_thread = count // self.num_threads
        remainder = count % self.num_threads

        # Start writer thread
        writer = None
        if output_file:
            writer = threading.Thread(target=self.writer_thread, args=(output_file, count))
            writer.start()

        # Start worker threads
        threads = []
        for thread_id in range(self.num_threads):
            # Distribute remainder among first few threads
            thread_count = addresses_per_thread + (1 if thread_id < remainder else 0)

            thread = threading.Thread(
                target=self.worker_thread,
                args=(thread_count, thread_id)
            )
            threads.append(thread)
            thread.start()

        # Monitor progress
        last_reported = 0
        while self.total_generated < count and self.running:
            time.sleep(0.1)
            current = self.total_generated

            if current >= last_reported + 10000:  # Report every 10k
                elapsed = time.time() - start_time
                rate = current / elapsed if elapsed > 0 else 0
                progress = (current / count) * 100
                print(f"  ⚡ {progress:.1f}% | {current:,} addresses | {rate:.0f}/sec")
                last_reported = current

        # Wait for all worker threads to complete
        for thread in threads:
            thread.join()

        # Signal writer to stop
        if writer:
            self.results_queue.put(None)  # Poison pill
            writer.join()

        end_time = time.time()
        elapsed = end_time - start_time
        rate = count / elapsed

        print(f"✅ COMPLETED: {count:,} addresses in {elapsed:.2f} seconds")
        print(f"🎯 FINAL RATE: {rate:.0f} addresses/second")

        if rate >= 500000:
            print("🏆 TARGET ACHIEVED: 500k+ addresses/second!")
        elif rate >= 100000:
            multiplier = 500000 / rate
            print(f"🔥 Excellent! Need {multiplier:.1f}x more for 500k target")
        else:
            multiplier = 500000 / rate
            print(f"📈 Progress: {rate:.0f}/sec (need {multiplier:.1f}x for 500k target)")

        return rate

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 optimized_coincurve_generator.py <count> [output_file] [threads]")
        print("Example: python3 optimized_coincurve_generator.py 50000 output.txt 20")
        sys.exit(1)

    try:
        count = int(sys.argv[1])
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        num_threads = int(sys.argv[3]) if len(sys.argv) > 3 else 20

        if count <= 0 or count > 5000000:
            print("Error: Count must be between 1 and 5,000,000")
            sys.exit(1)

        generator = OptimizedCoinCurveGenerator(num_threads)
        rate = generator.generate_multi_threaded(count, output_file)

        print(f"\n🎯 SUMMARY:")
        print(f"  Single thread performance: ~27,000/sec")
        print(f"  {num_threads} threads achieved: {rate:.0f}/sec")
        print(f"  Efficiency: {(rate / (27000 * num_threads)) * 100:.1f}%")

    except KeyboardInterrupt:
        print("\n❌ Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()