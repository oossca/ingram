# Ingram

Ingram 是一个针对摄像头的漏洞扫描工具，旨在帮助安全研究人员发现和修复摄像头设备中的安全漏洞。

## 功能特点

- 支持多种摄像头品牌和漏洞类型的检测（Hikvision, Dahua, Xiongmai, Uniview 等）
- 支持弱口令爆破
- 支持自动截图
- 多线程扫描，速度快
- 集成 FOFA API，支持自动获取目标
- 详细的扫描报告

## 安装依赖

在使用本工具前，请确保已安装 Python 3，并安装所需的依赖库：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python run_ingram.py -i targets.txt -o out
```

### 参数说明

| 参数 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `-i`, `--in_file` | 目标列表文件 (IP 或 IP:Port) | 必填 (除非使用 FOFA) |
| `-o`, `--out_dir` | 结果输出目录 | 必填 |
| `-p`, `--ports` | 指定扫描端口 | None (默认扫描常用端口) |
| `-t`, `--th_num` | 扫描线程数 | 150 |
| `-T`, `--timeout` | 请求超时时间(秒) | 3 |
| `-D`, `--disable_snapshot` | 禁用截图功能 | False |
| `--debug` | 开启调试模式，输出更多日志 | False |
| `-u`, `--users_file` | 自定义用户名字典文件 | None (使用内置字典) |
| `-P`, `--passwords_file` | 自定义密码字典文件 | None (使用内置字典) |
| `--use_fofa` | 使用 FOFA 获取目标 | False |
| `--fofa_email` | FOFA 账号邮箱 | None |
| `--fofa_key` | FOFA API Key | None |
| `--fofa_query` | FOFA 查询语句 | camera |
| `--fofa_max` | FOFA 最大获取数量 | 1000 |

### 示例

**1. 扫描指定文件中的目标：**

```bash
python run_ingram.py -i targets.txt -o results
```

**2. 指定端口和线程数：**

```bash
python run_ingram.py -i targets.txt -o results -p 80 8000 8080 -t 200
```

**3. 使用 FOFA 获取目标并扫描：**

```bash
python run_ingram.py -o results --use_fofa --fofa_email your_email@example.com --fofa_key your_api_key --fofa_query "app=\"Hikvision-Video-Surveillance\""
```

## 目录结构

- `Ingram/`: 核心代码库
  - `pocs/`: 漏洞验证脚本 (POCs)
  - `lib/`: 库文件
  - `utils/`: 工具函数
- `out/`: 默认输出目录
- `targets.txt`: 示例目标文件
- `passwords.txt`: 弱口令字典
- `users.txt`: 用户名字典
- `run_ingram.py`: 启动脚本

## 免责声明

本工具仅供网络安全研究和授权测试使用。严禁用于非法用途。使用本工具产生的任何后果由使用者自行承担，开发者不承担任何责任。
