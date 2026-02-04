"""
系统检查模块
"""

import os
import sys


def check_root():
    """检查是否为root用户"""
    if os.geteuid() != 0:
        from ..utils.output import red
        red("错误: 请使用 root 用户运行此脚本")
        sys.exit(1)


def check_system():
    """
    检查系统是否为Ubuntu

    Returns:
        是否继续安装
    """
    from ..utils.output import red, yellow

    try:
        with open("/etc/os-release") as f:
            content = f.read().lower()
            if "ubuntu" not in content:
                red("警告: 此脚本主要针对 Ubuntu 系统")
                return input("是否继续? [y/N]: ").lower() == 'y'
    except:
        red("无法检测系统类型")
    return True


def install_dependencies():
    """安装依赖包"""
    from ..utils.output import green
    from ..utils.helpers import run_cmd

    green("正在更新软件源...")
    run_cmd("apt-get update -y", check=False)

    green("正在安装依赖包...")
    run_cmd(
        "DEBIAN_FRONTEND=noninteractive apt-get install -y "
        "curl wget qrencode openssl socat cron",
        check=False
    )
