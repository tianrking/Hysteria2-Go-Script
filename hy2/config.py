"""
配置常量
"""

from pathlib import Path
import os

# Hysteria 2 版本配置
HY2_VERSION = "app/v2.7.0"
HY2_REPO = "apernet/hysteria"

# 路径配置
SERVICE_FILE = Path("/etc/systemd/system/hysteria-server.service")

# 配置目录 - 优先使用环境变量，否则使用 /etc/hysteria
CONFIG_DIR = Path(os.getenv("HY2_CONFIG_DIR", "/etc/hysteria"))

# 客户端配置目录
_home_dir = Path.home()
CLIENT_DIR = Path(os.getenv("HY2_CLIENT_DIR", _home_dir / "hy"))

# 二进制文件路径
BINARY_PATH = Path(os.getenv("HY2_BINARY_PATH", "/usr/local/bin/hysteria"))

# 伪装站点默认值
DEFAULT_PROXY_SITE = "maimai.sega.jp"

# 默认证书域名
DEFAULT_CERT_DOMAIN = "www.bing.com"

# Acme 邮箱
ACME_EMAIL = "acme@hy2.local"

# 服务名称
SERVICE_NAME = "hysteria-server"

# BBR 配置文件
BBR_CONFIG_FILE = "/etc/sysctl.d/99-hy2-bbr.conf"
