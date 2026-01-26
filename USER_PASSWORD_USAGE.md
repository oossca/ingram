# 用户名密码文件使用说明

## 概述

Ingram现在支持从外部文件导入用户名和密码列表，这样可以更灵活地管理弱口令字典。

## 新增命令行参数

- `-u, --users_file`: 指定用户名列表文件路径
- `-P, --passwords_file`: 指定密码列表文件路径

## 使用方法

### 1. 准备用户名密码文件

用户名文件示例 (`users.txt`):
```
# 以#开头的行为注释，会被忽略
admin
administrator
root
guest
user
operator
camera
```

密码文件示例 (`passwords.txt`):
```
# 以#开头的行为注释，会被忽略
admin
admin123
password
123456
12345
password123
```

### 2. 运行程序时指定文件

```bash
python run_ingram.py -i targets.txt -o output_dir -u users.txt -P passwords.txt
```

### 3. 仅指定其中一个文件

```bash
# 只指定用户名文件，使用默认密码列表
python run_ingram.py -i targets.txt -o output_dir -u users.txt

# 只指定密码文件，使用默认用户名列表
python run_ingram.py -i targets.txt -o output_dir -P passwords.txt
```

## 文件格式要求

1. **文件编码**: UTF-8
2. **每行一个**用户名或密码
3. **注释行**: 以`#`开头的行为注释，会被忽略
4. **空行**: 会被忽略
5. **去重**: 程序会自动处理重复项

## 默认行为

如果不指定文件，程序会使用内置的默认用户名密码列表：
- 默认用户名: `['admin']`
- 默认密码: `['admin', 'admin12345', 'asdf1234', 'abc12345', '12345admin', '12345abc']`

## 优先级

文件的优先级高于默认列表：
- 如果指定了用户名文件且文件存在，则使用文件中的用户名列表
- 如果指定了密码文件且文件存在，则使用文件中的密码列表
- 如果文件不存在或读取失败，会使用默认列表并显示警告

## 受影响的POC模块

所有使用弱口令检测的POC模块都会自动使用新的用户名密码列表，包括但不限于：
- `cam-weak-password.py`
- `axis-weak-password.py`
- `avtech-weak-password.py`
- `dahua-weak-password.py`
- `hikvision-weak-password.py`
- 以及其他所有弱口令检测模块

## 性能提示

- 建议用户名和密码列表控制在合理范围内，避免组合过多导致检测时间过长
- 可以根据目标设备类型选择针对性更强的用户名密码列表以提高效率