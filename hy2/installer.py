"""
安装和卸载模块
"""

import os
import re
import random
import shutil
import subprocess
from pathlib import Path


def download_hy2():
    """下载 Hysteria 2 二进制文件"""
    from ..config import HY2_VERSION, HY2_REPO, BINARY_PATH
    from ..utils.output import green, yellow, red
    from ..utils.helpers import get_arch

    green(f"正在下载 Hysteria 2 {HY2_VERSION}...")

    arch = get_arch()
    url = f"https://github.com/{HY2_REPO}/releases/download/{HY2_VERSION}/hysteria-linux-{arch}"

    yellow(f"  下载地址: {url}")
    yellow("  开始下载...")

    try:
        subprocess.run(
            f"wget --progress=bar:force -O {BINARY_PATH} {url}",
            shell=True, check=True, timeout=300
        )
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        red("下载失败，请检查网络或稍后重试")
        import sys
        sys.exit(1)

    BINARY_PATH.chmod(0o755)

    if BINARY_PATH.exists():
        size = BINARY_PATH.stat().st_size / 1024
        green(f"  下载完成! 文件大小: {size:.1f} KB")
        green("Hysteria 2 下载成功!")
    else:
        red("Hysteria 2 下载失败!")
        import sys
        sys.exit(1)


def collect_config():
    """
    收集配置信息

    Returns:
        tuple: (端口, 端口跳跃范围, 用户列表, 伪装站点)
    """
    from ..utils.output import yellow, green, red
    from ..utils.helpers import (
        is_port_available, generate_password, input_with_default
    )
    from ..config import DEFAULT_PROXY_SITE

    print("\n" + "="*50)
    yellow("配置向导")
    print("="*50)

    # 端口
    def validate_port(value):
        return value.isdigit() and 1 <= int(value) <= 65535

    port = input_with_default(
        "\n端口 [1-65535] (回车随机): ",
        default=str(random.randint(2000, 65535)),
        validator=validate_port,
        error_msg="端口范围: 1-65535"
    )
    port = int(port)
    yellow(f"随机端口: {port}")

    while not is_port_available(port):
        red(f"端口 {port} 已被占用")
        port = int(input_with_default(
            "\n端口 [1-65535] (回车随机): ",
            default=str(random.randint(2000, 65535)),
            validator=validate_port,
            error_msg="端口范围: 1-65535"
        ))

    # 端口跳跃
    hop_ports = None
    if input("\n启用端口跳跃? [y/N]: ").lower() == 'y':
        def validate_hop_port(value):
            return value.isdigit() and 10000 <= int(value) <= 65535

        hop_start = int(input_with_default(
            "跳跃起始端口 [10000-65535]: ",
            validator=validate_hop_port,
            error_msg="端口范围: 10000-65535"
        ))
        hop_end = int(input_with_default(
            "跳跃结束端口 [10000-65535]: ",
            validator=lambda v: validate_hop_port(v) and int(v) > hop_start,
            error_msg=f"端口范围: 10000-65535，且大于起始端口({hop_start})"
        ))
        hop_ports = f"{hop_start}:{hop_end}"
        yellow(f"端口跳跃范围: {hop_ports}")

    # 密码
    pwd = input(f"\n密码 (回车随机): ").strip()
    if not pwd:
        pwd = generate_password(8)
        yellow(f"随机密码: {pwd}")

    # 伪装站点
    proxy_site = input_with_default(
        "\n伪装站点 (回车默认): ",
        default=DEFAULT_PROXY_SITE
    )

    # 多用户
    users = [{"password": pwd}]
    if input("\n添加多用户? [y/N]: ").lower() == 'y':
        while True:
            user_pwd = input("输入用户密码 (回车跳过): ").strip()
            if not user_pwd:
                break
            users.append({"password": user_pwd})
            green(f"已添加用户，当前用户数: {len(users)}")

    return port, hop_ports, users, proxy_site


def generate_server_config(cert_path, key_path, port, hop_ports, users, proxy_site):
    """
    生成服务端配置

    Args:
        cert_path: 证书路径
        key_path: 私钥路径
        port: 端口
        hop_ports: 端口跳跃范围
        users: 用户列表
        proxy_site: 伪装站点
    """
    from ..config import CONFIG_DIR
    from ..utils.output import yellow

    if len(users) == 1:
        # 单用户
        config = f"""listen: :{port}
tls:
  cert: {cert_path}
  key: {key_path}
auth:
  type: password
  password: {users[0]['password']}
"""
    else:
        # 多用户
        users_str = "\n".join([f"  - \"{u['password']}\"" for u in users])
        config = f"""listen: :{port}
tls:
  cert: {cert_path}
  key: {key_path}
auth:
  type: userpass
  userpass:
{users_str}
"""

    # 伪装
    config += f"""masquerade:
  type: proxy
  proxy:
    url: https://{proxy_site}
    rewriteHost: true
"""

    # 端口跳跃
    if hop_ports:
        config += f"""transport:
  udp:
    hopInterval: 30s
hopPorts:
  - {hop_ports}
"""

    (CONFIG_DIR / "config.yaml").write_text(config)
    yellow(f"服务端配置已生成: {CONFIG_DIR}/config.yaml")


def install_binary():
    """仅安装二进制文件和依赖"""
    from ..system.check import install_dependencies
    from ..utils.output import print_step, green
    from ..config import BINARY_PATH
    from . import download_hy2

    print_step(1, 2, "安装依赖和下载")
    install_dependencies()

    if not BINARY_PATH.exists():
        download_hy2()
    else:
        green("Hysteria 2 二进制文件已存在，跳过下载")


def run_config_wizard():
    """运行配置向导"""
    from ..system.bbr import enable_bbr
    from ..utils.output import print_step, green, red
    from ..utils.helpers import get_server_ip
    from ..config import SERVICE_NAME
    from .certificate import handle_certificate
    from .service import create_systemd_service, wait_for_service
    from .client import generate_client_config
    from . import collect_config, generate_server_config
    from ..system.firewall import setup_firewall
    from ..utils.output import print_result

    print_step(2, 2, "配置 Hysteria 2")

    # 证书
    cert_path, key_path, domain = handle_certificate()

    # 配置参数
    port, hop_ports, users, proxy_site = collect_config()

    # BBR 加速
    if input("\n启用 BBR 加速? [Y/n]: ").lower() != 'n':
        enable_bbr()

    # 生成配置
    generate_server_config(cert_path, key_path, port, hop_ports, users, proxy_site)
    server_ip = get_server_ip()
    share_url = generate_client_config(server_ip, port, users[0]['password'], domain, hop_ports)
    green("配置文件已生成")

    # 防火墙
    setup_firewall(port, hop_ports)

    # systemd 服务
    green("正在创建 systemd 服务...")
    create_systemd_service()

    print("\n" + "-"*60)
    from ..utils.output import blue
    blue("启动服务")
    print("-"*60)
    green("正在启用并启动服务...")
    import subprocess
    subprocess.run(f"systemctl enable {SERVICE_NAME}", shell=True)
    subprocess.run(f"systemctl restart {SERVICE_NAME}", shell=True)

    if wait_for_service():
        print_result(server_ip, port, users[0]['password'], domain, share_url)
    else:
        red("服务启动失败，请检查日志: journalctl -u hysteria-server")


def install_hy2():
    """完整安装流程"""
    from ..system.check import check_root, check_system
    from ..utils.output import print_header, yellow
    from ..utils.helpers import get_install_status

    print_header()

    check_root()
    check_system()

    status = get_install_status()

    if status == 0:
        # 未安装 - 完整安装
        install_binary()
        run_config_wizard()
    elif status == 1:
        # 部分安装 - 继续配置
        yellow("检测到 Hysteria 2 已下载，但未配置")
        yellow("现在开始配置流程...")
        run_config_wizard()
    else:
        # 已安装 - 重新配置
        yellow("检测到已安装")
        if input("是否重新配置? [y/N]: ").lower() == 'y':
            run_config_wizard()
        else:
            yellow("已取消")


def uninstall_hy2(skip_confirm=False):
    """
    卸载 Hysteria 2

    Args:
        skip_confirm: 是否跳过确认
    """
    from ..config import SERVICE_FILE, BINARY_PATH, CONFIG_DIR, CLIENT_DIR, SERVICE_NAME
    from ..utils.output import green
    from ..utils.helpers import run_cmd

    if not skip_confirm:
        if input("确认卸载? [y/N]: ").lower() != 'y':
            return

    run_cmd(f"systemctl stop {SERVICE_NAME}", check=False)
    run_cmd(f"systemctl disable {SERVICE_NAME}", check=False)
    SERVICE_FILE.unlink(missing_ok=True)
    BINARY_PATH.unlink(missing_ok=True)

    if not skip_confirm and input("删除配置文件? [y/N]: ").lower() == 'y':
        shutil.rmtree(CONFIG_DIR, ignore_errors=True)
        shutil.rmtree(CLIENT_DIR, ignore_errors=True)

    run_cmd("systemctl daemon-reload", check=False)
    green("已卸载")


def change_config():
    """修改配置"""
    from ..config import CONFIG_DIR, CLIENT_DIR
    from ..utils.output import green, yellow, red
    from ..utils.helpers import backup_config, run_cmd, get_server_ip, is_port_available
    from ..certificate import handle_certificate
    from ..client import generate_client_config
    from ..system.firewall import setup_firewall

    print("\n" + "="*50)
    green("修改配置")
    print("="*50)
    print("1. 修改端口")
    print("2. 修改密码")
    print("3. 修改证书")
    print("4. 修改伪装站点")

    choice = input("\n请选择 [1-4]: ").strip()

    config_file = CONFIG_DIR / "config.yaml"
    if not config_file.exists():
        red("配置文件不存在，请先安装 Hysteria 2")
        return

    backup_config()

    if choice == "1":
        while True:
            port = input(f"\n新端口 [1-65535]: ").strip()
            if port.isdigit() and 1 <= int(port) <= 65535:
                port = int(port)
                if is_port_available(port):
                    break
                red(f"端口 {port} 已被占用")
        content = config_file.read_text()
        content = re.sub(r'listen: :\d+', f'listen: :{port}', content)
        config_file.write_text(content)
        green(f"端口已修改为: {port}")
        setup_firewall(port)
        run_cmd("systemctl restart hysteria-server")

    elif choice == "2":
        from ..utils.helpers import generate_password
        new_pwd = input(f"\n新密码 (回车随机): ").strip() or generate_password(8)
        content = config_file.read_text()
        content = re.sub(r'password: \S+', f'password: {new_pwd}', content)
        config_file.write_text(content)
        green(f"密码已修改为: {new_pwd}")

        # 更新客户端配置
        old_url = (CLIENT_DIR / "url.txt").read_text().strip()
        domain = re.search(r'sni=([^#&]+)', old_url)
        if domain:
            domain = domain.group(1)
            server_ip = get_server_ip()
            port = re.search(r'listen: :(\d+)', content)
            port = int(port.group(1)) if port else 443
            share_url = generate_client_config(server_ip, port, new_pwd, domain)
            yellow("\n新的分享链接:")
            print(share_url)

        run_cmd("systemctl restart hysteria-server")

    elif choice == "3":
        cert_path, key_path, domain = handle_certificate()
        content = config_file.read_text()
        content = re.sub(r'cert: .*', f'cert: {cert_path}', content)
        content = re.sub(r'key: .*', f'key: {key_path}', content)
        config_file.write_text(content)
        green("证书已更新")
        run_cmd("systemctl restart hysteria-server")

    elif choice == "4":
        proxy_site = input("\n新伪装站点: ").strip()
        if proxy_site:
            content = config_file.read_text()
            content = re.sub(r'url: https://\S+', f'url: https://{proxy_site}', content)
            config_file.write_text(content)
            green(f"伪装站点已更新为: {proxy_site}")
            run_cmd("systemctl restart hysteria-server")
