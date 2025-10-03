#ifndef HPP_HELP
#define HPP_HELP

#include <string>

const std::string g_strHelp = R"(
Usage: ./TronAddressGen [options]

  Basic:
    --help              Show help information

  Mode:
    --matching          Match input, file or single address string
    --generate          Generate specified number of random addresses (1-10000)

  Matching Parameters:
    --prefix-count      Minimum prefix match count, default 0
    --suffix-count      Minimum suffix match count, default 6
    --quit-count        Exit program when generated addresses exceed this value, default 0

  Device Management:
    --skip              Skip device by index number

  Output Management:
    --output            Output to file
    --post              Send to URL if needed

Examples:

  # Matching mode (original functionality)
  ./TronAddressGen --matching profanity.txt
  ./TronAddressGen --matching profanity.txt --skip 1
  ./TronAddressGen --matching profanity.txt --prefix-count 1 --suffix-count 8
  ./TronAddressGen --matching TUqEg3dzVEJNQSVW2HY98z5X8SBdhmao8D --prefix-count 2 --suffix-count 4 --quit-count 1

  # Generate mode (new functionality)
  ./TronAddressGen --generate 10                    # Generate 10 random addresses with correct private key mapping
  ./TronAddressGen --generate 100 --output result.txt   # Generate 100 addresses to file
  ./TronAddressGen --generate 50 --post http://127.0.0.1:7002/api   # Generate 50 addresses and send to URL

About:

  TronAddressGen is a Tron blockchain address generator: https://tron.network/
  Based on Ethereum profanity tool: https://github.com/johguse/profanity
  Ensure you get the program from the latest address: https://github.com/GG4mida/profanity-tron
  Author: telegram -> @jackslowfak
  Port modifier: telegram -> @MrMiHa

Security Warning:

  Always verify that generated addresses print correctly and match their private keys.
  The generate mode creates cryptographically valid private key/address pairs.
  Always use multi-signature for addresses to ensure account security.
  Test any generated address with small amounts before using for large transactions.
)";

#endif /* HPP_HELP */