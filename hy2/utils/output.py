"""
终端输出工具 - 颜色输出和进度显示
"""


class Colors:
    """终端颜色代码"""
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PLAIN = '\033[0m'


def red(msg):
    """红色输出"""
    print(f"{Colors.RED}{msg}{Colors.PLAIN}")


def green(msg):
    """绿色输出"""
    print(f"{Colors.GREEN}{msg}{Colors.PLAIN}")


def yellow(msg):
    """黄色输出"""
    print(f"{Colors.YELLOW}{msg}{Colors.PLAIN}")


def blue(msg):
    """蓝色输出"""
    print(f"{Colors.BLUE}{msg}{Colors.PLAIN}")


def show_loading(msg, delay=0.1):
    """
    显示加载动画

    Args:
        msg: 显示的消息
        delay: 动画帧延迟（秒）

    Returns:
        stop_event: 用于停止动画的事件对象
    """
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    import sys
    import threading
    import time

    stop_event = threading.Event()

    def _animate():
        while not stop_event.is_set():
            for frame in frames:
                if stop_event.is_set():
                    break
                sys.stdout.write(f"\r{Colors.YELLOW}{frame}{Colors.PLAIN} {msg}")
                sys.stdout.flush()
                time.sleep(delay)

    thread = threading.Thread(target=_animate)
    thread.daemon = True
    thread.start()
    return stop_event


def print_header():
    """打印脚本标题"""
    print("\n" + "="*60)
    green("Hysteria 2 一键安装脚本")
    yellow("作者: w0x7ce")
    print("="*60)


def print_step(num, total, title):
    """打印安装步骤"""
    print("\n" + "-"*60)
    blue(f"步骤 {num}/{total}: {title}")
    print("-"*60)


def print_menu():
    """打印主菜单"""
    from ..utils.helpers import get_install_status, get_status_text

    os_system_clear()
    print("=" * 60)
    green("Hysteria 2 一键安装脚本")
    yellow("作者: w0x7ce")
    print("=" * 60)

    status = get_status_text()
    yellow(f"状态: {status}")
    print("=" * 60)

    install_status = get_install_status()

    if install_status == 0:
        # 未安装
        print("1. 安装 Hysteria 2")
    elif install_status == 1:
        # 部分安装
        print("1. 继续配置")
        print("2. 重新安装")
    else:
        # 已安装
        print("1. 重新配置")
        print("2. 卸载")

    print("-" * 60)
    print("3. 启动服务")
    print("4. 停止服务")
    print("5. 重启服务")
    print("6. 查看状态")
    print("7. 查看日志")
    print("-" * 60)
    print("8. 修改配置")
    print("9. 显示配置")
    print("-" * 60)
    print("0. 退出")


def os_system_clear():
    """清屏"""
    import os
    os.system("clear 2>/dev/null || cls 2>/dev/null")


def print_result(server_ip, port, password, domain, share_url):
    """
    显示安装结果

    Args:
        server_ip: 服务器IP
        port: 端口
        password: 密码
        domain: 域名
        share_url: 分享链接
    """
    from ..config import CLIENT_DIR
    from ..utils.helpers import is_ipv6, generate_qrcode

    server_addr = f"[{server_ip}]" if is_ipv6(server_ip) else server_ip

    print("\n" + "="*60)
    green("Hysteria 2 安装成功!")
    print("="*60)

    print(f"\n服务器地址: {server_addr}")
    print(f"服务器端口: {port}")
    print(f"认证密码:   {password}")
    print(f"域名SNI:    {domain}")

    print("\n" + "-"*60)
    yellow("分享链接:")
    print(share_url)

    print("\n" + "-"*60)
    yellow("二维码 (扫码导入):")
    qrcode = generate_qrcode(share_url)
    if qrcode:
        print(qrcode)
    else:
        red("二维码生成失败，请手动输入分享链接")

    print("\n" + "-"*60)
    yellow(f"配置文件目录: {CLIENT_DIR}")
    print("  - hy-client.yaml  (客户端配置)")
    print("  - hy-client.json  (JSON格式)")
    print("  - url.txt         (分享链接)")
    print("="*60)
