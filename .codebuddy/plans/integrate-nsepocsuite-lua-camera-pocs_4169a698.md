---
name: integrate-nsepocsuite-lua-camera-pocs
overview: 将 NsePocsuite-lua 仓库中所有摄像头相关 NSE PoC 转换为 Ingram 的 Python PoC 脚本，并按现有框架加载与识别设备。
todos:
  - id: collect-nse-pocs
    content: 梳理 NsePocsuite-lua 中全部摄像头 PoC 清单与漏洞类型
    status: completed
  - id: map-products
    content: 建立品牌到 Ingram product 标识的映射表并对齐命名
    status: completed
    dependencies:
      - collect-nse-pocs
  - id: convert-pocs
    content: 为每个 NSE PoC 新建对应 Python 脚本并实现 verify/exploit
    status: completed
    dependencies:
      - map-products
  - id: update-rules
    content: 补充 rules.csv 中缺失的摄像头指纹规则
    status: completed
    dependencies:
      - map-products
  - id: validate-loading
    content: 校验新 PoC 能被动态导入并在指纹匹配后执行
    status: completed
    dependencies:
      - convert-pocs
      - update-rules
  - id: sample-results
    content: 提供典型设备的漏洞输出与截图流程示例说明
    status: completed
    dependencies:
      - validate-loading
---

## Product Overview

将 NsePocsuite-lua 仓库中全部摄像头相关 NSE PoC 转换为 Ingram 的 Python PoC 脚本，并由现有框架自动加载、识别与扫描目标设备，输出可验证的漏洞与快照结果。

## Core Features

- 将每个摄像头 NSE PoC 转译为独立 Python PoC 脚本，保持漏洞验证逻辑一致
- 新增 PoC 可被动态导入并按产品指纹匹配执行
- 扫描时产出统一的漏洞结果记录与统计报表
- 支持可选的设备快照抓取与结果文件输出

## Tech Stack

- 语言：Python
- 核心依赖：requests、loguru、gevent、lxml
- 现有 PoC 结构：Ingram/pocs/ + POCTemplate 基类

## Tech Architecture

- 复用现有 PoC 动态导入机制（Ingram/pocs/**init**.py）
- 以 POCTemplate 为统一接口，确保 verify/exploit 返回格式一致
- 指纹规则由 rules.csv 驱动，扫描入口位于 Ingram/core.py

## Implementation Details

### Core Directory Structure（仅列出新增/修改）

```
Ingram/
├── pocs/
│   ├── <新增的摄像头 PoC>.py
│   └── ...
├── rules.csv  # 可能补充新的产品指纹
```

### Key Code Structures

- **POCTemplate.verify(ip, port)**：返回 (ip, port, product, user, password, name) 或 None
- **POCTemplate.exploit(results)**：可选抓取截图并返回数量

### Technical Implementation Plan

1. **问题**：Lua NSE PoC 无法被现有 Python 框架直接加载  
**方案**：逐条转译为 Python PoC，适配 POCTemplate 接口
**步骤**：解析原 NSE 逻辑 → 实现 verify/exploit → 适配结果格式

2. **问题**：产品指纹缺失导致 PoC 无法触发  
**方案**：补齐 rules.csv 中缺失的摄像头品牌指纹
**步骤**：核对品牌列表 → 增补规则 → 对齐 product 命名

3. **问题**：扫描输出一致性  
**方案**：沿用现有结果记录与截图管线
**步骤**：确保 verify 返回标准元组 → exploit 调用 _snapshot