CXX = g++
CXXFLAGS = -std=c++11 -O0 -g -Wall -Wextra -DCL_TARGET_OPENCL_VERSION=120 -faligned-new
LDFLAGS = -lOpenCL -lpthread

# Source files
SOURCES = profanity.cpp \
          Dispatcher.cpp \
          Mode.cpp \
          SpeedSample.cpp \
          precomp.cpp

# Object files
OBJECTS = $(SOURCES:.cpp=.o)

# Executable name
TARGET = TronAddressGen

# Default target
all: $(TARGET)

# Link object files to generate executable
$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

# Compile source files to object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean object files and executable
clean:
	rm -f $(OBJECTS) $(TARGET)

# Rebuild
rebuild: clean all

# Check OpenCL environment
check-opencl:
	@echo "Checking OpenCL environment..."
	@pkg-config --exists OpenCL && echo "OpenCL development environment installed" || echo "OpenCL development environment not found"
	@ls /usr/include/CL/cl.h > /dev/null 2>&1 && echo "OpenCL headers exist" || echo "OpenCL headers not found"

.PHONY: all clean rebuild check-opencl