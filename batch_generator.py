#!/usr/bin/env python3
"""
Batch Tron address generator for high performance
Generates multiple addresses without subprocess overhead
"""
import sys
import secrets
from gen_tron_address_real import private_key_to_tron_address

def generate_batch_addresses(count, output_file=None):
    """Generate multiple addresses efficiently"""
    print(f"Batch generating {count} Tron addresses...")

    results = []

    # Open output file if specified
    file_handle = None
    if output_file:
        file_handle = open(output_file, 'w')
        print(f"Writing to file: {output_file}")

    try:
        for i in range(count):
            # Generate cryptographically secure random 32 bytes
            private_key_bytes = secrets.token_bytes(32)
            private_key_hex = private_key_bytes.hex()

            # Generate corresponding address
            address = private_key_to_tron_address(private_key_hex)

            # Store result
            result = (private_key_hex, address)
            results.append(result)

            # Write to file immediately (streaming)
            if file_handle:
                file_handle.write(f"{private_key_hex},{address}\n")
                file_handle.flush()  # Ensure immediate write

            # Print progress every 1000 addresses
            if (i + 1) % 1000 == 0:
                print(f"  Generated {i + 1} addresses...")

            # Show first few on console
            if i < 5:
                print(f"  Address {i+1}: Private: {private_key_hex} Address: {address}")

        print(f"Successfully generated {count} addresses!")
        return results

    finally:
        if file_handle:
            file_handle.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 batch_generator.py <count> [output_file]")
        print("Example: python3 batch_generator.py 1000 addresses.txt")
        sys.exit(1)

    try:
        count = int(sys.argv[1])
        if count <= 0 or count > 1000000:
            print("Error: Count must be between 1 and 1,000,000")
            sys.exit(1)

        output_file = sys.argv[2] if len(sys.argv) > 2 else None

        generate_batch_addresses(count, output_file)

    except ValueError:
        print("Error: Count must be a valid number")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nGeneration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)