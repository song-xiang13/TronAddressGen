#!/bin/bash

# TronAddressGen WSL runner script
# Description: This is a Tron address generator that requires OpenCL-supported GPU environment

echo "=== Tron Address Generator (TronAddressGen) ==="
echo ""

# Check if executable exists
if [ ! -f "./TronAddressGen" ]; then
    echo "Error: TronAddressGen executable not found!"
    echo "Please run 'make' command to compile the program first."
    exit 1
fi

# Check OpenCL environment
echo "Checking OpenCL environment..."
clinfo_output=$(clinfo 2>/dev/null | grep "Number of devices" | head -1)
if echo "$clinfo_output" | grep -q "0"; then
    echo "⚠️  Warning: No available OpenCL devices (GPU) detected in current WSL environment"
    echo "   This program requires GPU support to run properly."
    echo ""
    echo "💡 Suggestions:"
    echo "   1. Run on Windows host with dedicated graphics card"
    echo "   2. Use virtual machine with GPU passthrough support"
    echo "   3. Run on Linux physical machine with NVIDIA/AMD graphics card"
    echo ""
    echo "Continuing to attempt running the program (may fail)..."
else
    echo "✅ OpenCL devices detected, can run normally"
fi

echo ""
echo "Program usage examples:"
echo "./TronAddressGen --help                                           # Show help"
echo "./TronAddressGen --matching patterns.txt                         # Use pattern file"
echo "./TronAddressGen --matching TUvvo588wF97jjiBb1Hsqao2ZfhdMrMiHa   # Match specific address"
echo ""

# If arguments provided, run directly
if [ $# -gt 0 ]; then
    echo "Executing command: ./TronAddressGen $@"
    ./TronAddressGen "$@"
else
    echo "Please provide runtime parameters, for example:"
    echo "./run.sh --matching TUvvo588wF97jjiBb1Hsqao2ZfhdMrMiHa --suffix-count 6"
fi