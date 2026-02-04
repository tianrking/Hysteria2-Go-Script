"""
Hysteria 2 一键安装脚本 - 模块化版本
作者: w0x7ce
支持 Ubuntu VPS
"""

__version__ = "2.0.0"
__author__ = "w0x7ce"

# 导出主要功能
from .config import *
from .utils.output import *
from .utils.helpers import *
from .system.check import *
from .system.firewall import *
from .system.bbr import *
from .certificate import *
from .service import *
from .client import *
from .installer import *

__all__ = [
    "install_hy2",
    "install_binary",
    "run_config_wizard",
    "uninstall_hy2",
    "change_config",
    "show_config",
    "show_logs",
    "manage_service",
    "main",
]
