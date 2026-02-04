"""
通用工具函数
"""

import os
import sys
import subprocess
import platform
import secrets
import string
import random
from pathlib import Path


def run_cmd(cmd, check=True, capture=False, timeout=300):
    """
    执行命令

    Args:
        cmd: 要执行的命令
        check: 是否检查返回值
        capture: 是否捕获输出
        timeout: 超时时间（秒）

    Returns:
        捕获的输出或None
    """
    try:
        if capture:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=check, timeout=timeout)
    except subprocess.TimeoutExpired:
        if check:
            from .output import red
            red(f"命令执行超时: {cmd}")
            sys.exit(1)
        return None
    except subprocess.CalledProcessError as e:
        if check:
            from .output import red
            red(f"命令执行失败: {cmd}")
            if e.stderr:
                red(f"错误: {e.stderr.strip()}")
            sys.exit(1)
        return None
    return None


def get_arch():
    """
    获取系统架构

    Returns:
        架构字符串 (amd64/arm64/arm)
    """
    machine = platform.machine()
    arch_map = {
        "x86_64": "amd64",
        "aarch64": "arm64",
        "armv7l": "arm"
    }
    return arch_map.get(machine, "amd64")


def get_server_ip():
    """
    获取服务器IP

    Returns:
        服务器IP地址字符串
    """
    ip = run_cmd("curl -s4m8 ip.sb -k", capture=True, check=False)
    if not ip:
        ip = run_cmd("curl -s6m8 ip.sb -k", capture=True, check=False)
    return ip or "your_server_ip"


def is_ipv6(ip):
    """
    判断是否为IPv6地址

    Args:
        ip: IP地址字符串

    Returns:
        是否为IPv6
    """
    return ':' in str(ip)


def is_port_available(port):
    """
    检查端口是否可用

    Args:
        port: 端口号

    Returns:
        端口是否可用
    """
    result = run_cmd(
        f"ss -tunlp | grep -w udp | awk '{{print $5}}' | sed 's/.*://g' | grep -w '{port}'",
        capture=True, check=False
    )
    return not result


def generate_password(length=8):
    """
    生成随机密码

    Args:
        length: 密码长度

    Returns:
        随机密码字符串
    """
    return ''.join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def generate_qrcode(text):
    """
    生成二维码

    Args:
        text: 要编码的文本

    Returns:
        二维码ANSI字符串或None
    """
    try:
        result = run_cmd(
            f"echo '{text}' | qrencode -t ANSIUTF8",
            capture=True, check=False
        )
        return result
    except Exception:
        return None


def is_installed():
    """
    检查Hysteria 2是否已安装

    Returns:
        是否已安装
    """
    from ..config import BINARY_PATH
    return BINARY_PATH.exists()


def get_install_status():
    """
    获取安装状态

    Returns:
        0: 未安装
        1: 部分安装 (二进制存在，但配置不存在)
        2: 已安装 (二进制和配置都存在)
    """
    from ..config import BINARY_PATH, CONFIG_DIR

    binary_exists = BINARY_PATH.exists()
    config_exists = (CONFIG_DIR / "config.yaml").exists()

    if not binary_exists:
        return 0
    elif not config_exists:
        return 1
    else:
        return 2


def get_status_text():
    """
    获取状态文本

    Returns:
        状态描述字符串
    """
    status = get_install_status()
    if status == 0:
        return "未安装"
    elif status == 1:
        return "部分安装 (需要配置)"
    else:
        # 检查服务状态
        from ..config import SERVICE_NAME
        from .output import Colors
        result = run_cmd(f"systemctl is-active {SERVICE_NAME}", capture=True, check=False)
        service_status = result if result else "unknown"
        if service_status == "active":
            return "已安装 - 运行中"
        elif service_status == "inactive":
            return "已安装 - 已停止"
        else:
            return f"已安装 - {service_status}"


def backup_config():
    """备份配置文件"""
    from ..config import CONFIG_DIR
    from .output import green
    import shutil

    config_file = CONFIG_DIR / "config.yaml"
    if config_file.exists():
        backup_path = CONFIG_DIR / "config.yaml.backup"
        shutil.copy(config_file, backup_path)
        green(f"配置已备份到: {backup_path}")


def input_with_default(prompt, default=None, validator=None, error_msg=None):
    """
    带默认值和验证的输入函数

    Args:
        prompt: 提示信息
        default: 默认值
        validator: 验证函数
        error_msg: 验证失败时的错误信息

    Returns:
        用户输入的值
    """
    while True:
        value = input(prompt).strip()
        if not value and default is not None:
            return default
        if validator is None or validator(value):
            return value
        from .output import red
        red(error_msg or "输入无效，请重试")
