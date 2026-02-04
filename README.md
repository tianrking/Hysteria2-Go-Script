# Hysteria 2 一键安装脚本

Hysteria 2 代理服务器一键安装脚本，支持 Ubuntu VPS。

[![DigitalOcean Referral Badge](https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%203.svg)](https://www.digitalocean.com/?refcode=9b9563b5b0b2&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge)

🚀 速来拼好模，智谱 GLM Coding 超值订阅，邀你一起薅羊毛！Claude Code、Cline 等 20+ 大编程工具无缝支持，"码力"全开，越拼越爽！立即开拼，享限时惊喜价！
[链接](https://www.bigmodel.cn/glm-coding?ic=QJ82Z7R8YK)

---

## 快速开始

### 一键安装 (推荐)

```bash
curl -fsSL https://raw.githubusercontent.com/tianrking/Hysteria2-Go-Script/main/hy2.py | python3
```

或先下载再运行：

```bash
wget https://raw.githubusercontent.com/tianrking/Hysteria2-Go-Script/main/hy2.py
python3 hy2.py
```

---

## 目录结构

```
.
├── hy2.py                 # 单文件版本 - 一键安装 (curl | bash)
└── hy2/                   # 模块化版本 - 开发/定制
    ├── __init__.py
    ├── __main__.py
    ├── config.py
    ├── certificate.py
    ├── service.py
    ├── client.py
    ├── installer.py
    ├── hy2_cli.py         # CLI 包装器
    ├── setup.py           # 模块安装配置
    ├── utils/
    │   ├── output.py      # 终端输出
    │   └── helpers.py     # 辅助函数
    └── system/
        ├── check.py       # 系统检查
        ├── firewall.py    # 防火墙配置
        └── bbr.py         # BBR 加速
```

---

## 两种版本

### 1. 单文件版本 (hy2.py)

**适合用户一键安装**

- 单个文件，包含所有功能
- 支持 `curl | bash` 方式安装
- 适合快速部署

### 2. 模块化版本 (hy2/)

**适合开发者二次修改**

```bash
# 进入开发目录
cd hy2

# 方法一：直接运行模块
python3 -m __main__

# 方法二：使用 CLI 包装器
python3 hy2_cli.py

# 方法三：安装为系统命令
pip install -e .
hy2
```

---

## 功能特性

| 功能 | 说明 |
|------|------|
| 一键安装 | 自动下载、配置、启动 Hysteria 2 |
| 证书支持 | 自签证书 / 自定义证书 / Acme 自动申请 |
| 多用户 | 支持单用户或多用户配置 |
| 端口跳跃 | 支持端口跳跃增强隐蔽性 |
| 伪装站点 | 支持流量伪装 |
| BBR 加速 | 自动启用 BBR 加速 |
| 防火墙 | 自动配置 ufw/firewalld |
| 服务管理 | systemd 服务集成 |
| 状态检测 | 智能检测安装状态，支持中断后继续配置 |

---

## 模块说明

| 模块 | 功能 |
|------|------|
| `config.py` | 版本号、路径配置、常量定义 |
| `utils/output.py` | 彩色输出、加载动画、菜单显示 |
| `utils/helpers.py` | 命令执行、IP获取、端口检测、密码生成、状态检测 |
| `system/check.py` | Root检查、系统检测、依赖安装 |
| `system/firewall.py` | ufw/firewalld 防火墙配置 |
| `system/bbr.py` | BBR 加速启用 |
| `certificate.py` | 自签/自定义/Acme 证书申请 |
| `service.py` | systemd 服务创建、管理、日志查看 |
| `client.py` | YAML/JSON/URL 客户端配置生成 |
| `installer.py` | 安装流程、配置收集、配置修改 |

---

## 交互式菜单

菜单根据安装状态动态显示：

### 未安装状态
```
状态: 未安装
============================================================
1. 安装 Hysteria 2
------------------------------------------------------------
3. 启动服务
4. 停止服务
...
```

### 部分安装状态（安装中断）
```
状态: 部分安装 (需要配置)
============================================================
1. 继续配置
2. 重新安装
------------------------------------------------------------
...
```

### 已安装状态
```
状态: 已安装 - 运行中
============================================================
1. 重新配置
2. 卸载
------------------------------------------------------------
...
```

---

## 开发指南

```bash
# 克隆仓库
git clone https://github.com/tianrking/Hysteria2-Go-Script.git
cd Hysteria2-Go-Script

# 进入开发目录
cd hy2

# 开发模式安装
pip install -e .

# 运行
hy2
# 或
python3 -m __main__
```

---

## 许可协议

本项目采用 **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)** 许可协议。

- ✅ 允许：分享、修改、用于学习和个人项目
- ❌ 禁止：商业用途、商业分销

---

## 免责声明

本脚本仅供学习和研究使用。使用本脚本造成的任何后果，作者不承担任何责任。请遵守当地法律法规。
