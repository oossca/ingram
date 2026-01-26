# FOFA集成使用说明

## 概述

Ingram现在支持从FOFA（网络空间搜索引擎）获取目标地址，无需手动准备targets.txt文件，可以直接从互联网上搜索摄像头等设备作为扫描目标。

## 获取FOFA API密钥

1. 访问 [FOFA官网](https://fofa.info/)
2. 注册账号并登录
3. 在用户中心获取API信息：
   - Email: 注册邮箱
   - Key: API密钥

## 基本使用方法

### 1. 命令行参数

```bash
# 使用FOFA获取摄像头目标
python run_ingram.py --use_fofa --fofa_email your_email@example.com --fofa_key your_fofa_key -o output_dir

# 自定义搜索查询
python run_ingram.py --use_fofa --fofa_email your_email@example.com --fofa_key your_fofa_key --fofa_query "Hikvision" -o output_dir

# 限制结果数量
python run_ingram.py --use_fofa --fofa_email your_email@example.com --fofa_key your_fofa_key --fofa_max 500 -o output_dir

# 结合用户名密码文件
python run_ingram.py --use_fofa --fofa_email your_email@example.com --fofa_key your_fofa_key -u users.txt -P passwords.txt -o output_dir
```

### 2. 新增参数说明

- `--use_fofa`: 启用FOFA模式，不从文件读取目标
- `--fofa_email`: FOFA账号邮箱
- `--fofa_key`: FOFA API密钥
- `--fofa_query`: FOFA搜索查询语法（默认：camera）
- `--fofa_max`: 最大获取结果数（默认：1000）

## FOFA搜索语法

### 基础查询

```bash
# 搜索所有摄像头
--fofa_query "camera"

# 搜索特定厂商设备
--fofa_query "app=\"Hikvision-Web\""
--fofa_query "app=\"Dahua-Web\""
--fofa_query "app=\"AXIS-Web\""

# 搜索特定端口
--fofa_query "port=8080"
--fofa_query "port=554"

# 搜索特定地区
--fofa_query "country=\"CN\""
--fofa_query "country=\"US\""
```

### 高级查询

```bash
# 组合查询
--fofa_query "app=\"Hikvision-Web\" && country=\"CN\""

# 搜索特定标题
--fofa_query "title=\"摄像头\""

# 搜索特定响应头
--fofa_query "header=\"Dahua\""

# 搜索特定协议
--fofa_query "protocol=\"rtsp\""
--fofa_query "protocol=\"http\""
```

## 摄像头专用搜索

当`--fofa_query`设置为"camera"或包含"摄像头"时，程序会自动使用优化的摄像头搜索策略：

```bash
# 默认摄像头搜索（推荐）
python run_ingram.py --use_fofa --fofa_email your_email@example.com --fofa_key your_fofa_key -o output

# 自动搜索多种摄像头相关目标：
# - camera
# - title="摄像头"
# - body="摄像头"
# - app="Hikvision-Web"
# - app="Dahua-Web"
# - app="AXIS-Web"
# - banner="Camera"
# - banner="DVR"
```

## 输出文件

FOFA模式会自动生成目标文件：

```
output_dir/
├── fofa_targets.txt  # FOFA获取的目标列表
├── results.csv
├── not_vulnerable.csv
├── snapshots
└── log.txt
```

`fofa_targets.txt`文件格式：
```
# FOFA搜索结果
# 生成时间: 2024-01-25 15:30:00
# 格式: ip:port 或 host

192.168.1.100:80
camera.example.com:8080
10.0.0.50:80
```

## 注意事项

### API限制

1. **请求频率**: 程序会自动控制请求间隔（1秒），避免触发限制
2. **结果数量**: 每次搜索最多1000个结果，可根据需要调整
3. **查询数量**: 摄像头模式会限制查询数量，避免过多请求

### 最佳实践

1. **精确查询**: 使用具体的搜索语法提高目标质量
2. **地区限制**: 结合country参数缩小搜索范围
3. **厂商特定**: 针对特定厂商设备使用对应的app查询
4. **结果筛选**: 获取大量结果时考虑进一步筛选

### 安全建议

1. **授权扫描**: 仅扫描有授权的目标
2. **速率控制**: 不要过于频繁地调用FOFA API
3. **合规使用**: 遵守FOFA使用条款和当地法律法规

## 错误处理

常见错误及解决方法：

```bash
# 1. API密钥错误
ERROR: FOFA API错误: Invalid email or key
解决: 检查邮箱和API密钥是否正确

# 2. 请求过于频繁
ERROR: FOFA请求失败: 429 Too Many Requests
解决: 程序会自动控制频率，如仍出现请减少查询数量

# 3. 查询语法错误
ERROR: FOFA API错误: Invalid query syntax
解决: 检查FOFA查询语法是否正确

# 4. 网络问题
ERROR: FOFA请求失败: Connection timeout
解决: 检查网络连接，稍后重试
```

## 使用示例

### 扫描海康威视摄像头
```bash
python run_ingram.py --use_fofa \
  --fofa_email your_email@example.com \
  --fofa_key your_fofa_key \
  --fofa_query "app=\"Hikvision-Web\" && country=\"CN\"" \
  --fofa_max 500 \
  -u users.txt -P passwords.txt \
  -o hikvision_scan
```

### 扫描特定端口设备
```bash
python run_ingram.py --use_fofa \
  --fofa_email your_email@example.com \
  --fofa_key your_fofa_key \
  --fofa_query "port=554" \
  -o rtsp_scan
```

通过FOFA集成，Ingram可以更方便地获取真实的互联网目标，提高漏洞发现效率。