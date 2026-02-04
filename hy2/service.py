"""
服务管理模块
"""

import time
from pathlib import Path


def create_systemd_service():
    """创建 systemd 服务"""
    from ..config import SERVICE_FILE, BINARY_PATH, CONFIG_DIR, SERVICE_NAME
    from ..utils.output import yellow, green
    from ..utils.helpers import run_cmd

    service_content = f"""[Unit]
Description=Hysteria 2 Service
After=network.target

[Service]
Type=simple
ExecStart={BINARY_PATH} server -c {CONFIG_DIR}/config.yaml
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
    SERVICE_FILE.write_text(service_content)
    yellow("  - 写入服务文件...")
    run_cmd("systemctl daemon-reload", check=False)
    yellow("  - 重载 systemd 配置...")
    green("systemd 服务已创建")


def wait_for_service():
    """
    等待服务启动

    Returns:
        服务是否成功启动
    """
    from ..utils.output import yellow
    from ..utils.helpers import run_cmd
    from ..config import SERVICE_NAME

    yellow("等待服务启动...")
    for i in range(3, 0, -1):
        import sys
        from ..utils.output import Colors
        sys.stdout.write(f"\r{Colors.YELLOW}等待服务启动... {i}秒{Colors.PLAIN}")
        sys.stdout.flush()
        time.sleep(1)
    print()

    result = run_cmd(f"systemctl is-active {SERVICE_NAME}", capture=True, check=False)
    return result == "active"


def manage_service(action):
    """
    服务控制

    Args:
        action: 操作类型 (start/stop/restart/status)
    """
    from ..config import SERVICE_NAME
    from ..utils.output import green
    from ..utils.helpers import run_cmd

    if action == "start":
        run_cmd(f"systemctl start {SERVICE_NAME}")
        run_cmd(f"systemctl enable {SERVICE_NAME}")
        green("已启动")
    elif action == "stop":
        run_cmd(f"systemctl stop {SERVICE_NAME}")
        green("已停止")
    elif action == "restart":
        run_cmd(f"systemctl restart {SERVICE_NAME}")
        green("已重启")
    elif action == "status":
        import os
        os.system(f"systemctl status {SERVICE_NAME}")


def show_logs():
    """查看服务日志"""
    from ..config import SERVICE_NAME
    import os
    os.system(f"journalctl -u {SERVICE_NAME} -f --lines 50")
