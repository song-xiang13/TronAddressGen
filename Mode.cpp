#include "Mode.hpp"
#include <stdexcept>

#include <iostream>
#include <sstream>
#include <vector>
#include <fstream>
#include <string>

Mode::Mode() : score(0), prefixCount(0), suffixCount(0), matchingCount(0), isGenerateMode(false), generateCount(0) {

}

static std::string::size_type hexValueNoException(char c) {
	const std::string hex = "0123456789abcdef";
	const std::string::size_type ret = hex.find(tolower(c));
	return ret;
}

Mode Mode::matching(std::string matchingInput) {
	Mode r;
	std::vector<std::string> matchingList;

	if(matchingInput.size() == 34 && matchingInput[0] == 'T') {
		std::stringstream ss;
		matchingInput.erase(10, 14);
		for (const char &item: matchingInput) {
			ss << std::hex << int(item);
		}
		matchingList.push_back(ss.str());
	} else {
		std::ifstream file(matchingInput);
		if (file.is_open()) {
			std::string line;
			while (std::getline(file, line)) {
				std::stringstream ss;
				if(line.size() == 20 || line.size() == 34) {
					if(line.size() == 34) {
						line.erase(10, 14);
					}
					for (const char &item: line) {
						ss << std::hex << int(item);
					}
					matchingList.push_back(ss.str());
				}
			}
		} else {
			std::cout << "error: Failed to open matching file. :<" << std::endl;
		}
	}
	
	if(matchingList.size() > 0) {
		r.matchingCount = matchingList.size();
		for( size_t j = 0; j < matchingList.size(); j += 1) {
			const std::string matchingItem = matchingList[j];
			for( size_t i = 0; i < matchingItem.size(); i += 2 ) {
				const size_t indexHi = hexValueNoException(matchingItem[i]);
				const size_t indexLo = (i + 1) < matchingItem.size() ? hexValueNoException(matchingItem[i+1]) : std::string::npos;
				const unsigned long valHi = (indexHi == std::string::npos) ? 0 : indexHi << 4;
				const unsigned long valLo = (indexLo == std::string::npos) ? 0 : indexLo;
				const int maskHi = (indexHi == std::string::npos) ? 0 : 0xF << 4;
				const int maskLo = (indexLo == std::string::npos) ? 0 : 0xF;
				r.data1.push_back(maskHi | maskLo);
				r.data2.push_back(valHi | valLo);
			}
		}
	}

	return r;
}

Mode Mode::generate(const size_t count) {
	Mode r;
	r.isGenerateMode = true;
	r.generateCount = count;
	r.matchingCount = 1;

	// For generate mode, create a very easy match pattern
	// We'll match the Tron address prefix "41" in hex (which becomes "T" in base58)
	// This means any valid Tron address will match, allowing fast generation
	r.data1.push_back(0xFF); // Match exactly on first byte
	r.data2.push_back(0x41); // Tron address prefix is 0x41

	// Add more bytes to have enough data for the kernel
	for(int i = 1; i < 20; i++) {
		r.data1.push_back(0x00); // Don't care about other bytes
		r.data2.push_back(0x00); // Don't care about the value
	}

	return r;
}
