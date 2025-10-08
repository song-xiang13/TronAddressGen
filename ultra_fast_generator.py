#!/usr/bin/env python3
"""
Ultra High Performance Tron Address Generator
Target: 500,000 addresses per second
Uses multi-threading and optimized crypto operations
"""
import sys
import secrets
import concurrent.futures
import threading
import time
from queue import Queue
from ecdsa import SigningKey, SECP256k1
from Crypto.Hash import keccak
import hashlib

# Global constants for optimization
ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
ALPHABET_BYTES = ALPHABET.encode('ascii')

class HighPerformanceGenerator:
    def __init__(self, num_threads=20):
        self.num_threads = num_threads
        self.write_queue = Queue(maxsize=10000)
        self.stats_lock = threading.Lock()
        self.total_generated = 0

    def fast_base58_encode(self, data):
        """Optimized base58 encoding"""
        # Convert bytes to integer
        num = int.from_bytes(data, 'big')

        if num == 0:
            return ALPHABET[0]

        # Convert to base58
        encoded = []
        while num > 0:
            num, remainder = divmod(num, 58)
            encoded.append(ALPHABET[remainder])

        # Handle leading zeros
        for byte in data:
            if byte == 0:
                encoded.append(ALPHABET[0])
            else:
                break

        return ''.join(reversed(encoded))

    def fast_private_key_to_address(self, private_key_bytes):
        """Optimized address generation"""
        try:
            # Generate public key using secp256k1
            sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
            vk = sk.get_verifying_key()
            public_key_bytes = vk.to_string()

            # Keccak-256 hash
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

    def generate_batch(self, batch_size):
        """Generate a batch of addresses in one thread"""
        results = []

        for _ in range(batch_size):
            # Generate random private key
            private_key_bytes = secrets.token_bytes(32)
            private_key_hex = private_key_bytes.hex()

            # Generate address
            address = self.fast_private_key_to_address(private_key_bytes)

            if address:
                results.append((private_key_hex, address))

        return results

    def worker_thread(self, total_count, batch_size, thread_id):
        """Worker thread for generating addresses"""
        generated_count = 0

        while generated_count < total_count:
            current_batch_size = min(batch_size, total_count - generated_count)
            batch_results = self.generate_batch(current_batch_size)

            # Add to write queue
            for result in batch_results:
                self.write_queue.put(result)

            generated_count += current_batch_size

            # Update stats
            with self.stats_lock:
                self.total_generated += len(batch_results)

    def writer_thread(self, output_file, total_target):
        """Writer thread for file output"""
        written_count = 0
        buffer = []
        buffer_size = 1000  # Write in batches

        with open(output_file, 'w') as f:
            while written_count < total_target:
                try:
                    # Get item from queue
                    item = self.write_queue.get(timeout=1)
                    if item is None:  # Poison pill
                        break

                    buffer.append(f"{item[0]},{item[1]}\n")
                    written_count += 1

                    # Write buffer when full
                    if len(buffer) >= buffer_size:
                        f.writelines(buffer)
                        f.flush()
                        buffer = []

                    self.write_queue.task_done()

                except:
                    continue

            # Write remaining buffer
            if buffer:
                f.writelines(buffer)
                f.flush()

    def generate_ultra_fast(self, count, output_file=None):
        """Ultra fast generation with multi-threading"""
        start_time = time.time()
        print(f"Ultra-fast generating {count} addresses with {self.num_threads} threads...")

        # Calculate work distribution
        addresses_per_thread = count // self.num_threads
        batch_size = 100  # Process in smaller batches for better responsiveness

        # Start writer thread
        writer_future = None
        if output_file:
            writer_future = threading.Thread(
                target=self.writer_thread,
                args=(output_file, count)
            )
            writer_future.start()

        # Start worker threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = []

            for thread_id in range(self.num_threads):
                # Last thread handles remainder
                thread_count = addresses_per_thread
                if thread_id == self.num_threads - 1:
                    thread_count += count % self.num_threads

                future = executor.submit(
                    self.worker_thread,
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

                if current >= last_reported + 10000:  # Report every 10k
                    elapsed = time.time() - start_time
                    rate = current / elapsed if elapsed > 0 else 0
                    print(f"  Generated {current} addresses... Rate: {rate:.0f}/sec")
                    last_reported = current

            # Wait for all threads to complete
            concurrent.futures.wait(futures)

        # Signal writer to stop
        if writer_future:
            self.write_queue.put(None)  # Poison pill
            writer_future.join()

        end_time = time.time()
        elapsed = end_time - start_time
        rate = count / elapsed

        print(f"✅ Generated {count} addresses in {elapsed:.2f} seconds")
        print(f"🚀 Rate: {rate:.0f} addresses/second")

        return rate

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ultra_fast_generator.py <count> [output_file] [threads]")
        print("Example: python3 ultra_fast_generator.py 100000 output.txt 20")
        sys.exit(1)

    try:
        count = int(sys.argv[1])
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        num_threads = int(sys.argv[3]) if len(sys.argv) > 3 else 20

        if count <= 0 or count > 10000000:
            print("Error: Count must be between 1 and 10,000,000")
            sys.exit(1)

        generator = HighPerformanceGenerator(num_threads)
        rate = generator.generate_ultra_fast(count, output_file)

        if rate >= 500000:
            print("🎉 TARGET ACHIEVED: 500k+ addresses/second!")
        else:
            print(f"📈 Current rate: {rate:.0f}/sec (Target: 500,000/sec)")

    except KeyboardInterrupt:
        print("\n❌ Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()