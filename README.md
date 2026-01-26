<div align=center>
    <img alt="Ingram" src="https://github.com/jorhelp/imgs/blob/master/Ingram/logo.png">
</div>


<!-- icons -->
<div align=center>
    <img alt="Platform" src="https://img.shields.io/badge/platform-Linux%20|%20Mac-blue.svg">
    <img alt="Python Version" src="https://img.shields.io/badge/python-3.8-yellow.svg">
    <img alt="GitHub" src="https://img.shields.io/github/license/jorhelp/Ingram">
    <img alt="Github Checks" src="https://img.shields.io/github/checks-status/jorhelp/Ingram/master">
    <img alt="GitHub Last Commit (master)" src="https://img.shields.io/github/last-commit/jorhelp/Ingram/master">
    <img alt="Languages Count" src="https://img.shields.io/github/languages/count/jorhelp/Ingram?style=social">
</div>

简体中文 | [English](https://github.com/jorhelp/Ingram/blob/master/README.en.md)

## 简介

主要针对网络摄像头的漏洞扫描框架，目前已集成海康、大华、宇视、dlink等常见设备

<div align=center>
    <img alt="run" src="https://github.com/jorhelp/imgs/blob/master/Ingram/run_time.gif">
</div>


## 安装

**请在 Linux 或 Mac 系统使用，确保安装了3.8及以上版本的Python，推荐使用3.8-3.10版本**

+ 克隆该仓库:
```bash
git clone https://github.com/jorhelp/Ingram.git
cd Ingram
```

+ 进入项目目录，创建一个虚拟环境，并激活该环境：
```bash
# Windows系统
python -m venv venv
venv\Scripts\activate

# Linux/Mac系统
python3 -m venv venv
source venv/bin/activate
```

+ 安装依赖:
```bash
pip install -r requirements.txt
```

如果遇到依赖安装问题，可以尝试：
```bash
pip install -r requirements.txt --upgrade
# 或者
pip install -r requirements.txt --force-reinstall
```

至此安装完毕！

### 新增功能

本次更新包含以下新功能：
1. **自定义用户名密码文件**：支持从外部文件导入字典
2. **改进的中断恢复**：更精确的状态保存和恢复
3. **性能优化**：修复了gevent兼容性问题，提高稳定性
4. **更好的错误处理**：增强异常处理和资源管理
5. **FOFA集成**：支持从FOFA网络空间搜索引擎获取目标地址


## 运行

+ 由于是在虚拟环境中配置，所以，每次运行之前，请先激活虚拟环境：`source venv/bin/activate`

+ 你需要准备一个目标文件，比如 targets.txt，里面保存着你要扫描的 IP 地址，每行一个目标，具体格式如下：
```
# 你可以使用井号(#)来进行注释

# 单个的 IP 地址
192.168.0.1

# IP 地址以及要扫描的端口
192.168.0.2:80

# 带 '/' 的IP段
192.168.0.0/16

# 带 '-' 的IP段
192.168.0.0-192.168.255.255
```

+ 有了目标文件之后就可直接运行:
```bash
python3 run_ingram.py -i 你要扫描的文件 -o 输出文件夹
```

+ 端口：
如果target.txt文件中指定了目标的端口，比如: 192.168.6.6:8000，那么会扫描该目标的8000端口 

否则的话，默认只扫描常见端口(定义在 `Ingram/config.py` 中)，若要批量扫描其他端口，需自行指定，例如：
```bash
python3 run_ingram.py -i 你要扫描的文件 -o 输出文件夹 -p 80 81 8000
```

+ 默认并发数目为 300，可以根据机器配置及网速通过 `-t` 参数来自行调控：
```bash
python3 run_ingram.py -i 你要扫描的文件 -o 输出文件夹 -t 500
```

+ 支持中断恢复，程序会定期保存运行状态（每10个任务保存一次），如果扫描因为网络或异常而中断，可以通过重复执行上次的扫描命令来恢复进度

+ 支持自定义用户名密码字典：
```bash
# 使用自定义用户名密码文件
python3 run_ingram.py -i 你要扫描的文件 -o 输出文件夹 -u users.txt -P passwords.txt

# 只指定用户名文件，使用默认密码列表
python3 run_ingram.py -i 你要扫描的文件 -o 输出文件夹 -u users.txt

# 只指定密码文件，使用默认用户名列表
python3 run_ingram.py -i 你要扫描的文件 -o 输出文件夹 -P passwords.txt
```

用户名和密码文件格式要求：
- 文件编码：UTF-8
- 每行一个用户名或密码
- 以#开头的行为注释，会被忽略
- 空行会被忽略

+ 所有参数：
```
optional arguments:
  -h, --help            show this help message and exit
  -i IN_FILE, --in_file IN_FILE
                        the targets will be scan
  -o OUT_DIR, --out_dir OUT_DIR
                        the dir where results will be saved
  -p PORTS [PORTS ...], --ports PORTS [PORTS ...]
                        the port(s) to detect
  -t TH_NUM, --th_num TH_NUM
                        the processes num
  -T TIMEOUT, --timeout TIMEOUT
                        requests timeout
  -u USERS_FILE, --users_file USERS_FILE
                        file containing usernames list
  -P PASSWORDS_FILE, --passwords_file PASSWORDS_FILE
                        file containing passwords list
  --use_fofa            use FOFA to get targets instead of input file
  --fofa_email FOFA_EMAIL
                        FOFA account email
  --fofa_key FOFA_KEY    FOFA API key
  --fofa_query FOFA_QUERY
                        FOFA search query (default: camera)
  --fofa_max FOFA_MAX    Maximum FOFA results (default: 1000)
  -D, --disable_snapshot
                        disable snapshot
  --debug
```


## 用户名密码文件功能

Ingram支持从外部文件导入用户名和密码列表，提高弱口令检测的灵活性。

### 基本用法

```bash
# 同时指定用户名和密码文件
python3 run_ingram.py -i targets.txt -o output -u users.txt -P passwords.txt
```

### 文件格式

**用户名文件示例 (users.txt)**:
```
# 注释行以#开头
admin
administrator
root
guest
user
operator
```

**密码文件示例 (passwords.txt)**:
```
# 注释行以#开头
admin
admin123
password
123456
```

### 注意事项

- 文件必须使用UTF-8编码
- 每行一个用户名或密码
- 以#开头的行为注释，会被忽略
- 空行会被忽略
- 文件优先级高于默认列表
- 如果文件读取失败，会回退到默认列表并显示警告

### 默认字典

如果不指定文件，程序使用内置的默认字典：
- 默认用户名: `['admin']`
- 默认密码: `['admin', 'admin12345', 'asdf1234', 'abc12345', '12345admin', '12345abc']`

## 中断恢复功能

Ingram具有智能的中断恢复能力，可以安全地处理各种异常情况：

### 恢复机制

- **自动保存**: 每完成10个任务自动保存进度
- **状态记录**: 保存已完成任务数、发现漏洞数和运行时间
- **精确恢复**: 从上次中断位置继续，避免重复扫描
- **异常安全**: 即使状态文件损坏也能安全重启

### 使用方法

当程序因网络问题、用户中断或其他异常停止时，只需重新运行相同的命令即可：

```bash
# 第一次运行
python3 run_ingram.py -i targets.txt -o output

# 如果中断，再次运行相同命令即可恢复
python3 run_ingram.py -i targets.txt -o output
```

### 状态文件

- 状态文件保存在输出目录中，文件名为`.taskid`
- 程序会自动管理状态文件的创建和更新
- 正常退出时也会保存最终状态

## FOFA网络空间搜索引擎集成

Ingram现已集成FOFA网络空间搜索引擎，可以直接从互联网获取摄像头等设备作为扫描目标。

### 获取FOFA API密钥

1. 访问 [FOFA官网](https://fofa.info/) 注册账号
2. 在用户中心获取API邮箱和密钥

### FOFA模式使用

```bash
# 基础FOFA搜索
python3 run_ingram.py --use_fofa --fofa_email your_email@example.com --fofa_key your_fofa_key -o output

# 自定义搜索查询
python3 run_ingram.py --use_fofa --fofa_email your_email@example.com --fofa_key your_fofa_key --fofa_query "Hikvision" -o output

# 限制结果数量
python3 run_ingram.py --use_fofa --fofa_email your_email@example.com --fofa_key your_fofa_key --fofa_max 500 -o output

# 结合用户名密码文件
python3 run_ingram.py --use_fofa --fofa_email your_email@example.com --fofa_key your_fofa_key -u users.txt -P passwords.txt -o output
```

### 常用FOFA查询语法

```bash
# 搜索摄像头设备
--fofa_query "camera"

# 搜索特定厂商
--fofa_query "app=\"Hikvision-Web\""
--fofa_query "app=\"Dahua-Web\""
--fofa_query "app=\"AXIS-Web\""

# 搜索特定端口
--fofa_query "port=8080"
--fofa_query "port=554"

# 组合查询
--fofa_query "app=\"Hikvision-Web\" && country=\"CN\""
```

### FOFA模式特点

- **自动去重**：基于host去除重复目标
- **智能分页**：自动处理API分页，获取最大数量结果
- **速率控制**：内置请求间隔，避免触发API限制
- **格式兼容**：自动生成与Ingram兼容的目标文件格式

详细使用说明请参考：[FOFA_USAGE.md](FOFA_USAGE.md)

## 端口扫描器

+ 我们可以利用强大的端口扫描器来获取活动主机，进而缩小 Ingram 的扫描范围，提高运行速度，具体做法是将端口扫描器的结果文件整理成 `ip:port` 的格式，并作为 Ingram 的输入

+ 这里以 masscan 为例简单演示一下（masscan 的详细用法这里不再赘述），首先用 masscan 扫描 80 或 8000-8008 端口存活的主机：`masscan -p80,8000-8008 -iL 目标文件 -oL 结果文件 --rate 8000`

+ masscan 运行完之后，将结果文件整理一下：`grep 'open' 结果文件 | awk '{printf"%s:%s\n", $4, $3}' > targets.txt`

+ 之后对这些主机进行扫描：`python run_ingram.py -i targets.txt -o out`


## ~~微信提醒~~(已移除)

+ (**可选**) 扫描时间可能会很长，如果你想让程序扫描结束的时候通过微信发送一条提醒的话，你需要按照 [wxpusher](https://wxpusher.zjiecode.com/docs/) 的指示来获取你的专属 *UID* 和 *APP_TOKEN*，并将其写入 `run_ingram.py`:
```python
# wechat
config.set_val('WXUID', '这里写uid')
config.set_val('WXTOKEN', '这里写token')
```


## 结果

```bash
.
├── not_vulnerable.csv
├── results.csv
├── snapshots
└── log.txt
```

+ `results.csv` 里保存了完整的结果, 格式为: `ip,端口,设备类型,用户名,密码,漏洞条目`:  

<div align=center>
    <img alt="Ingram" src="https://github.com/jorhelp/imgs/blob/master/Ingram/results.png">
</div>

+ `not_vulnerable.csv` 中保存的是没有暴露的设备

+ `snapshots` 中保存了部分设备的快照:  

<div align=center>
    <img alt="Ingram" src="https://github.com/jorhelp/imgs/blob/master/Ingram/snapshots.png">
</div>


## ~~实时预览~~ (由于部分原因已移除)

+ ~~可以直接通过浏览器登录来预览~~
  
+ ~~如果想批量查看，我们提供了一个脚本 `show/show_rtsp/show_all.py`，不过它还有一些问题:~~

<div align=center>
    <img alt="Ingram" src="https://github.com/jorhelp/imgs/blob/master/Ingram/show_rtsp.png">
</div>


## 使用技巧和性能优化

### 扫描效率优化

1. **目标范围控制**：
   ```bash
   # 使用端口扫描器预先筛选存活主机
   masscan -p80,8000-8008 -iL targets.txt -oL masscan_results.txt --rate 8000
   grep 'open' masscan_results.txt | awk '{printf"%s:%s\n", $4, $3}' > filtered_targets.txt
   python3 run_ingram.py -i filtered_targets.txt -o output
   ```

2. **并发数调整**：
   ```bash
   # 根据网络和机器配置调整并发数
   python3 run_ingram.py -i targets.txt -o output -t 300  # 默认值
   python3 run_ingram.py -i targets.txt -o output -t 500  # 高性能
   python3 run_ingram.py -i targets.txt -o output -t 100  # 稳定优先
   ```

3. **超时设置**：
   ```bash
   # 根据网络环境调整超时时间
   python3 run_ingram.py -i targets.txt -o output -T 3   # 默认3秒
   python3 run_ingram.py -i targets.txt -o output -T 1   # 快速网络
   python3 run_ingram.py -i targets.txt -o output -T 10  # 慢速网络
   ```

### 字典优化

1. **针对性字典**：
   - 根据目标设备类型选择合适的用户名密码
   - 海康威视设备常用: admin/12345, admin/888888
   - 大华设备常用: admin/admin, admin/888888
   - 字典越大，扫描时间越长，建议控制在合理范围内

2. **优先级设置**：
   ```bash
   # 将最可能的用户名密码放在文件前面
   users.txt:
   admin
   administrator
   root
   
   passwords.txt:
   admin
   123456
   888888
   ```

### 批量处理建议

1. **分批扫描**：大量目标建议分批次处理，避免内存占用过高
2. **磁盘空间**：确保输出目录有足够空间存储快照和日志
3. **监控资源**：使用`--debug`参数查看详细日志，监控程序状态

### 故障排除

1. **常见错误**：
   - `LoopExit`: 已修复，如果仍有问题请更新到最新版本
   - `ValueError: only one '/' allowed in IP Address`: 检查targets.txt中的URL格式
   - 内存不足：降低并发数或分批处理

2. **恢复方法**：
   - 程序中断后重新运行相同命令即可恢复
   - 如果状态损坏，删除输出目录中的`.`开头的隐藏文件重新开始

## 免责声明

本工具仅供安全测试，严禁用于非法用途，后果与本团队无关


## 鸣谢 & 引用

Thanks to [Aiminsun](https://github.com/Aiminsun/CVE-2021-36260) for CVE-2021-36260  
Thanks to [chrisjd20](https://github.com/chrisjd20/hikvision_CVE-2017-7921_auth_bypass_config_decryptor) for hidvision config file decryptor  
Thanks to [mcw0](https://github.com/mcw0/DahuaConsole) for DahuaConsole
