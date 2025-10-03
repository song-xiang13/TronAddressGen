# WSL环境运行说明

## 项目概述
这是一个波场(Tron)地址生成器，移植自profanity项目。程序使用OpenCL技术通过GPU并行计算来快速生成符合指定模式的波场地址。

## 编译状态 ✅
程序已在WSL环境中成功编译：
- 安装了必要的依赖：`build-essential`, `opencl-headers`, `ocl-icd-opencl-dev`
- 创建了Makefile构建配置
- 编译生成了`TronAddressGen`可执行文件

## 运行环境要求 ⚠️
**重要**: 此程序需要支持OpenCL的GPU环境才能正常运行。

当前WSL环境状态：
- OpenCL开发环境：✅ 已安装
- 可用GPU设备：❌ 未检测到

## 运行方法

### 1. 基本命令
```bash
# 查看帮助信息
./TronAddressGen --help

# 使用运行脚本（推荐）
./run.sh --help
```

### 2. 地址生成示例
```bash
# 生成匹配特定后缀的地址
./TronAddressGen --matching TUvvo588wF97jjiBb1Hsqao2ZfhdMrMiHa --suffix-count 6 --quit-count 10

# 使用模式文件
./TronAddressGen --matching patterns.txt --prefix-count 2 --suffix-count 4
```

### 3. 编译命令
```bash
# 编译程序
make

# 清理并重新编译
make clean && make

# 检查OpenCL环境
make check-opencl
```

## 文件说明
- `TronAddressGen` - 主程序可执行文件
- `run.sh` - 运行脚本，包含环境检查
- `Makefile` - 编译配置文件
- `test_patterns.txt` - 测试用地址模式文件

## GPU环境配置建议

### 在Windows上运行
1. 安装Visual Studio 2022
2. 安装NVIDIA/AMD显卡驱动
3. 使用原始的Visual Studio项目文件编译

### 在Linux物理机上运行
1. 安装显卡驱动（NVIDIA CUDA或AMD ROCm）
2. 安装OpenCL运行时
3. 使用此Makefile编译

### WSL GPU支持
WSL2理论上支持GPU，但需要：
1. Windows 11或Windows 10版本2004+
2. 安装WSL2 GPU驱动
3. 启用WSL2 GPU功能

## 安全提示 🔒
- 生成的私钥请妥善保管
- 建议对重要地址使用多重签名
- 验证生成的地址与私钥是否匹配
- 不要在网络环境不安全的地方运行此程序

## 故障排除
1. 如果遇到"unknown exception"错误，通常是GPU环境问题
2. 检查`clinfo`命令输出，确认有可用的OpenCL设备
3. 在GPU环境正常的机器上重新运行程序