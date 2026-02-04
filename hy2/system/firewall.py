"""
防火墙配置模块
"""

from ..utils.output import yellow, green, red
from ..utils.helpers import run_cmd


def setup_firewall(port, hop_ports=None):
    """
    配置防火墙开放端口

    Args:
        port: 主端口
        hop_ports: 端口跳跃范围 (格式: "start:end")
    """
    yellow("正在配置防火墙...")

    # ufw
    if run_cmd("which ufw", capture=True, check=False):
        yellow("检测到 ufw，正在添加规则...")
        run_cmd(f"ufw allow {port}/udp", check=False)
        green(f"已开放端口: {port}/udp")
        if hop_ports:
            run_cmd(f"ufw allow {hop_ports}/udp", check=False)
            green(f"已开放端口范围: {hop_ports}/udp")
        green("ufw 防火墙规则已添加!")
        return

    # firewalld
    if run_cmd("which firewall-cmd", capture=True, check=False):
        yellow("检测到 firewalld，正在添加规则...")
        run_cmd(f"firewall-cmd --permanent --add-port={port}/udp", check=False)
        green(f"已开放端口: {port}/udp")
        if hop_ports:
            run_cmd(f"firewall-cmd --permanent --add-port={hop_ports}/udp", check=False)
            green(f"已开放端口范围: {hop_ports}/udp")
        run_cmd("firewall-cmd --reload", check=False)
        green("firewalld 防火墙规则已添加!")
        return

    yellow("未检测到 ufw 或 firewalld")
    red(f"请手动开放端口: {port}/udp")
    if hop_ports:
        red(f"请手动开放端口范围: {hop_ports}/udp")
