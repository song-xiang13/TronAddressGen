#include <iostream>
#include <vector>
#include <CL/cl.h>

int main() {
    try {
        std::cout << "Getting OpenCL platforms..." << std::endl;

        cl_uint platformCount = 0;
        clGetPlatformIDs(0, NULL, &platformCount);
        std::cout << "Found " << platformCount << " platforms" << std::endl;

        if (platformCount == 0) {
            std::cout << "No OpenCL platforms found" << std::endl;
            return 1;
        }

        std::vector<cl_platform_id> platforms(platformCount);
        clGetPlatformIDs(platformCount, platforms.data(), NULL);

        for (cl_uint i = 0; i < platformCount; i++) {
            std::cout << "Platform " << i << ":" << std::endl;

            char platformName[256];
            clGetPlatformInfo(platforms[i], CL_PLATFORM_NAME, sizeof(platformName), platformName, NULL);
            std::cout << "  Name: " << platformName << std::endl;

            cl_uint deviceCount = 0;
            clGetDeviceIDs(platforms[i], CL_DEVICE_TYPE_ALL, 0, NULL, &deviceCount);
            std::cout << "  Devices: " << deviceCount << std::endl;

            if (deviceCount > 0) {
                std::vector<cl_device_id> devices(deviceCount);
                clGetDeviceIDs(platforms[i], CL_DEVICE_TYPE_ALL, deviceCount, devices.data(), NULL);

                for (cl_uint j = 0; j < deviceCount; j++) {
                    char deviceName[256];
                    clGetDeviceInfo(devices[j], CL_DEVICE_NAME, sizeof(deviceName), deviceName, NULL);
                    std::cout << "    Device " << j << ": " << deviceName << std::endl;

                    cl_device_type deviceType;
                    clGetDeviceInfo(devices[j], CL_DEVICE_TYPE, sizeof(deviceType), &deviceType, NULL);
                    std::cout << "      Type: " << (deviceType == CL_DEVICE_TYPE_CPU ? "CPU" :
                                                   deviceType == CL_DEVICE_TYPE_GPU ? "GPU" : "OTHER") << std::endl;
                }
            }
        }

        std::cout << "OpenCL enumeration completed successfully" << std::endl;
        return 0;
    }
    catch (const std::exception& e) {
        std::cout << "Exception: " << e.what() << std::endl;
        return 1;
    }
    catch (...) {
        std::cout << "Unknown exception occurred" << std::endl;
        return 1;
    }
}