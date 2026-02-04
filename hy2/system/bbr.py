"""
BBR 加速模块
"""

from ..utils.output import yellow, green
from ..utils.helpers import run_cmd
from ..config import BBR_CONFIG_FILE


def enable_bbr():
    """启用 BBR 加速"""
    yellow("正在配置 BBR 加速...")

    # 检查是否已启用
    result = run_cmd("sysctl net.ipv4.tcp_congestion_control", capture=True, check=False)
    if result and "bbr" in result:
        green("BBR 已启用")
        return

    # 设置 BBR
    config_content = """net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
"""

    yellow("正在写入 BBR 配置...")
    with open(BBR_CONFIG_FILE, "w") as f:
        f.write(config_content)

    yellow("正在应用 BBR 配置...")
    run_cmd("sysctl -p " + BBR_CONFIG_FILE, check=False)
    green("BBR 已启用!")
    yellow("注意: 重启后完全生效")


def is_bbr_enabled():
    """
    检查 BBR 是否已启用

    Returns:
        BBR 是否已启用
    """
    result = run_cmd("sysctl net.ipv4.tcp_congestion_control", capture=True, check=False)
    return result and "bbr" in result
