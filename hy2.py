#!/usr/bin/env python3
"""
Hysteria 2 一键安装脚本
作者: w0x7ce
支持 Ubuntu VPS
"""

import os
import sys
import subprocess
import platform
import secrets
import string
import random
import json
import re
import shutil
import time
from pathlib import Path
from urllib.parse import quote

# ============ 配置 ============
HY2_VERSION = "app/v2.7.0"
HY2_REPO = "apernet/hysteria"

# 动态路径配置
SERVICE_FILE = Path("/etc/systemd/system/hysteria-server.service")

# 配置目录 - 优先使用环境变量，否则使用 /etc/hysteria
CONFIG_DIR = Path(os.getenv("HY2_CONFIG_DIR", "/etc/hysteria"))

# 客户端配置目录 - 根据当前用户家目录动态设置
# 优先使用环境变量 HY2_CLIENT_DIR，否则使用 ~/hy
_home_dir = Path.home()
CLIENT_DIR = Path(os.getenv("HY2_CLIENT_DIR", _home_dir / "hy"))

# 二进制文件路径
BINARY_PATH = Path(os.getenv("HY2_BINARY_PATH", "/usr/local/bin/hysteria"))

# ============ 颜色输出 ============
class Colors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PLAIN = '\033[0m'

def red(msg):
    print(f"{Colors.RED}{msg}{Colors.PLAIN}")

def green(msg):
    print(f"{Colors.GREEN}{msg}{Colors.PLAIN}")

def yellow(msg):
    print(f"{Colors.YELLOW}{msg}{Colors.PLAIN}")

def blue(msg):
    print(f"{Colors.BLUE}{msg}{Colors.PLAIN}")

# ============ 工具函数 ============
def run_cmd(cmd, check=True, capture=False):
    """执行命令"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=check, timeout=300)
    except subprocess.TimeoutExpired:
        if check:
            red(f"命令执行超时: {cmd}")
            sys.exit(1)
        return None
    except subprocess.CalledProcessError as e:
        if check:
            red(f"命令执行失败: {cmd}")
            if e.stderr:
                red(f"错误: {e.stderr.strip()}")
            sys.exit(1)
        return None

def get_arch():
    """获取系统架构"""
    machine = platform.machine()
    arch_map = {
        "x86_64": "amd64",
        "aarch64": "arm64",
        "armv7l": "arm"
    }
    return arch_map.get(machine, "amd64")

def get_server_ip():
    """获取服务器IP"""
    ip = run_cmd("curl -s4m8 ip.sb -k", capture=True, check=False)
    if not ip:
        ip = run_cmd("curl -s6m8 ip.sb -k", capture=True, check=False)
    return ip or "your_server_ip"

def is_ipv6(ip):
    """判断是否为IPv6地址"""
    return ':' in str(ip)

def is_port_available(port):
    """检查端口是否可用"""
    result = run_cmd(f"ss -tunlp | grep -w udp | awk '{{print $5}}' | sed 's/.*://g' | grep -w '{port}'", capture=True, check=False)
    return not result

def generate_password(length=8):
    """生成随机密码"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def is_installed():
    """检查是否已安装"""
    return BINARY_PATH.exists()

def get_install_status():
    """
    获取安装状态

    Returns:
        0: 未安装
        1: 部分安装 (二进制存在，但配置不存在)
        2: 已安装 (二进制和配置都存在)
    """
    binary_exists = BINARY_PATH.exists()
    config_exists = (CONFIG_DIR / "config.yaml").exists()

    if not binary_exists:
        return 0
    elif not config_exists:
        return 1
    else:
        return 2

def get_status_text():
    """获取状态文本"""
    status = get_install_status()
    if status == 0:
        return "未安装"
    elif status == 1:
        return "部分安装 (需要配置)"
    else:
        # 检查服务状态
        result = run_cmd("systemctl is-active hysteria-server", capture=True, check=False)
        service_status = result if result else "unknown"
        if service_status == "active":
            return "已安装 - 运行中"
        elif service_status == "inactive":
            return "已安装 - 已停止"
        else:
            return f"已安装 - {service_status}"

def generate_qrcode(text):
    """生成二维码"""
    try:
        result = run_cmd(f"echo '{text}' | qrencode -t ANSIUTF8", capture=True, check=False)
        return result
    except:
        return None

def show_loading(msg, delay=0.1):
    """显示加载动画"""
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

def backup_config():
    """备份配置文件"""
    config_file = CONFIG_DIR / "config.yaml"
    if config_file.exists():
        backup_path = CONFIG_DIR / "config.yaml.backup"
        shutil.copy(config_file, backup_path)
        green(f"配置已备份到: {backup_path}")

# ============ 系统检查 ============
def check_root():
    """检查是否为root用户"""
    if os.geteuid() != 0:
        red("错误: 请使用 root 用户运行此脚本")
        sys.exit(1)

def check_system():
    """检查系统是否为Ubuntu"""
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
    green("正在更新软件源...")
    run_cmd("apt-get update -y", check=False)

    green("正在安装依赖包...")
    # 显示安装进度
    run_cmd("DEBIAN_FRONTEND=noninteractive apt-get install -y curl wget qrencode openssl socat cron", check=False)

# ============ Hysteria 2 安装 ============
def download_hy2():
    """下载 Hysteria 2 二进制文件"""
    green(f"正在下载 Hysteria 2 {HY2_VERSION}...")

    arch = get_arch()
    url = f"https://github.com/{HY2_REPO}/releases/download/{HY2_VERSION}/hysteria-linux-{arch}"

    # 使用 wget 显示进度条
    yellow(f"  下载地址: {url}")
    yellow("  开始下载...")

    # 不使用 check=False，让错误能被捕获
    try:
        result = subprocess.run(f"wget --progress=bar:force -O {BINARY_PATH} {url}",
                              shell=True, check=True, timeout=300)
    except subprocess.TimeoutExpired:
        red("下载超时，请检查网络连接")
        sys.exit(1)
    except subprocess.CalledProcessError:
        red("下载失败，请检查网络或稍后重试")
        sys.exit(1)

    BINARY_PATH.chmod(0o755)

    if BINARY_PATH.exists():
        # 获取文件大小
        size = BINARY_PATH.stat().st_size / 1024  # KB
        green(f"  下载完成! 文件大小: {size:.1f} KB")
        green("Hysteria 2 下载成功!")
    else:
        red("Hysteria 2 下载失败!")
        sys.exit(1)

# ============ 防火墙配置 ============
def setup_firewall(port, hop_ports=None):
    """配置防火墙开放端口"""
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

# ============ BBR 加速 ============
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
    with open("/etc/sysctl.d/99-hy2-bbr.conf", "w") as f:
        f.write(config_content)

    yellow("正在应用 BBR 配置...")
    run_cmd("sysctl -p /etc/sysctl.d/99-hy2-bbr.conf", check=False)
    green("BBR 已启用!")
    yellow("注意: 重启后完全生效")

# ============ 证书处理 ============
def handle_certificate():
    """处理证书配置"""
    print("\n" + "="*50)
    green("证书配置方式:")
    print("  1. 自签证书 (默认)")
    print("  2. 自定义证书")
    print("  3. Acme 自动申请 (需要域名)")
    print("="*50)

    choice = input("请选择 [1-3]: ").strip() or "1"

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if choice == "3":
        return handle_acme_certificate()

    if choice == "2":
        while True:
            cert_path = input("请输入证书路径 [.crt]: ").strip()
            key_path = input("请输入私钥路径 [.key]: ").strip()
            domain = input("请输入证书域名: ").strip()

            if not Path(cert_path).exists():
                red(f"证书文件不存在: {cert_path}")
                continue
            if not Path(key_path).exists():
                red(f"私钥文件不存在: {key_path}")
                continue
            if not domain:
                red("域名不能为空")
                continue

            return cert_path, key_path, domain

    # 默认自签证书
    yellow("正在生成自签证书...")
    cert_path = CONFIG_DIR / "cert.crt"
    key_path = CONFIG_DIR / "private.key"

    yellow("  - 生成私钥...")
    run_cmd(f"openssl ecparam -genkey -name prime256v1 -out {key_path} 2>/dev/null")
    key_path.chmod(0o600)

    yellow("  - 生成证书...")
    run_cmd(f"openssl req -new -x509 -days 36500 -key {key_path} -out {cert_path} -subj '/CN=www.bing.com' 2>/dev/null")
    cert_path.chmod(0o644)

    green("证书生成成功!")
    return str(cert_path), str(key_path), "www.bing.com"

def handle_acme_certificate():
    """使用 Acme 申请证书"""
    yellow("\nAcme 证书申请需要:")
    print("  - 域名已解析到当前服务器IP")
    print("  - 80 端口未被占用")

    domain = input("\n请输入域名: ").strip()
    if not domain:
        red("域名不能为空")
        return handle_certificate()

    # 检查域名解析
    green("正在验证域名解析...")
    server_ip = get_server_ip()
    domain_ip = run_cmd(f"curl -sm8 ipget.net/?ip={domain}", capture=True, check=False)

    if domain_ip != server_ip:
        red(f"域名 {domain} 解析IP ({domain_ip}) 与服务器IP ({server_ip}) 不匹配")
        return handle_certificate()
    green("域名解析验证通过!")

    # 安装 acme.sh
    green("\n正在安装 acme.sh...")
    run_cmd("curl https://get.acme.sh | sh -s email=acme@hy2.local", check=False)
    acme_sh = Path.home() / ".acme.sh" / "acme.sh"

    if not acme_sh.exists():
        red("acme.sh 安装失败")
        return handle_certificate()

    # 申请证书
    cert_path = CONFIG_DIR / "cert.crt"
    key_path = CONFIG_DIR / "private.key"

    green(f"正在申请证书: {domain}")
    yellow("(这可能需要 30-60 秒，请耐心等待...)")

    run_cmd(f"{acme_sh} --set-default-ca --server letsencrypt", check=False)
    result = run_cmd(f"{acme_sh} --issue -d {domain} --standalone -k ec-256 --insecure", check=False)

    if "Domain not" in result or "error" in result.lower():
        red("证书申请失败，可能原因:")
        yellow("  - 域名未正确解析")
        yellow("  - 80 端口被占用")
        yellow("  - 防火墙阻止了 80 端口")
        return handle_certificate()

    run_cmd(f"{acme_sh} --install-cert -d {domain} --ecc --fullchain-file {cert_path} --key-file {key_path}", check=False)

    if cert_path.exists() and key_path.exists():
        key_path.chmod(0o600)
        cert_path.chmod(0o644)
        green("证书申请成功!")

        # 设置自动续期
        cron_cmd = f"0 0 * * * {acme_sh} --cron -f >/dev/null 2>&1"
        run_cmd(f'(crontab -l 2>/dev/null | grep -v "acme.sh"; echo "{cron_cmd}") | crontab -', check=False)

        return str(cert_path), str(key_path), domain
    else:
        red("证书申请失败")
        return handle_certificate()

# ============ 配置收集 ==========
def collect_config():
    """收集配置信息"""
    print("\n" + "="*50)
    yellow("配置向导")
    print("="*50)

    # 端口
    while True:
        port = input("\n端口 [1-65535] (回车随机): ").strip()
        if not port:
            port = random.randint(2000, 65535)
            yellow(f"随机端口: {port}")
        if port.isdigit() and 1 <= int(port) <= 65535:
            port = int(port)
            if is_port_available(port):
                break
            red(f"端口 {port} 已被占用")
        else:
            red("端口范围: 1-65535")

    # 端口跳跃
    hop_ports = None
    if input("\n启用端口跳跃? [y/N]: ").lower() == 'y':
        while True:
            hop_start = input("跳跃起始端口 [10000-65535]: ").strip()
            hop_end = input("跳跃结束端口 [10000-65535]: ").strip()
            if hop_start.isdigit() and hop_end.isdigit():
                hop_start = int(hop_start)
                hop_end = int(hop_end)
                if hop_start < hop_end:
                    hop_ports = f"{hop_start}:{hop_end}"
                    yellow(f"端口跳跃范围: {hop_ports}")
                    break
            red("端口范围无效")

    # 密码
    pwd = input(f"\n密码 (回车随机): ").strip()
    if not pwd:
        pwd = generate_password(8)
        yellow(f"随机密码: {pwd}")

    # 伪装站点
    proxy_site = input("\n伪装站点 (回车默认: maimai.sega.jp): ").strip()
    if not proxy_site:
        proxy_site = "maimai.sega.jp"

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

# ============ 配置文件生成 ==========
def generate_server_config(cert_path, key_path, port, hop_ports, users, proxy_site):
    """生成服务端配置"""
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

def generate_client_config(server_ip, port, password, domain, hop_ports=None):
    """生成客户端配置"""
    CLIENT_DIR.mkdir(parents=True, exist_ok=True)

    server_addr = f"[{server_ip}]" if is_ipv6(server_ip) else server_ip

    # 端口跳跃
    port_str = f"{port},{hop_ports}" if hop_ports else str(port)

    yellow("  - 生成客户端配置...")
    # YAML 配置
    yaml_config = f"""server: {server_addr}:{port_str}
auth: {password}
tls:
  sni: {domain}
  insecure: true
fastOpen: true
socks5:
  listen: 127.0.0.1:5080
"""
    (CLIENT_DIR / "hy-client.yaml").write_text(yaml_config)

    # JSON 配置
    json_config = {
        "server": f"{server_addr}:{port_str}",
        "auth": password,
        "tls": {"sni": domain, "insecure": True},
        "fastOpen": True,
        "socks5": {"listen": "127.0.0.1:5080"}
    }
    (CLIENT_DIR / "hy-client.json").write_text(json.dumps(json_config, indent=2))

    # 分享链接
    encoded_password = quote(password, safe='')
    share_url = f"hysteria2://{encoded_password}@{server_addr}:{port}/?insecure=1&sni={domain}#HY2"
    (CLIENT_DIR / "url.txt").write_text(share_url)

    yellow(f"  - 生成二维码...")
    return share_url

# ============ 服务管理 ============
def create_systemd_service():
    """创建 systemd 服务"""
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
    """等待服务启动"""
    yellow("等待服务启动...")
    for i in range(3, 0, -1):
        sys.stdout.write(f"\r{Colors.YELLOW}等待服务启动... {i}秒{Colors.PLAIN}")
        sys.stdout.flush()
        time.sleep(1)
    print()  # 换行

    result = run_cmd("systemctl is-active hysteria-server", capture=True, check=False)
    return result == "active"

def show_result(server_ip, port, password, domain, share_url):
    """显示安装结果"""
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

# ============ 安装 ==========
def install_binary():
    """仅安装二进制文件和依赖"""
    print("\n" + "-"*60)
    blue("步骤 1/2: 安装依赖和下载")
    print("-"*60)

    install_dependencies()

    if not BINARY_PATH.exists():
        download_hy2()
    else:
        green("Hysteria 2 二进制文件已存在，跳过下载")

def run_config_wizard():
    """运行配置向导"""
    print("\n" + "-"*60)
    blue("步骤 2/2: 配置 Hysteria 2")
    print("-"*60)

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
    blue("启动服务")
    print("-"*60)
    green("正在启用并启动服务...")
    run_cmd("systemctl enable hysteria-server")
    run_cmd("systemctl restart hysteria-server")

    if wait_for_service():
        show_result(server_ip, port, users[0]['password'], domain, share_url)
    else:
        red("服务启动失败，请检查日志: journalctl -u hysteria-server")

def install_hy2():
    """完整安装流程"""
    print("\n" + "="*60)
    green("Hysteria 2 安装脚本")
    yellow("作者: w0x7ce")
    print("="*60)

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

# ============ 卸载 ==========
def uninstall_hy2(skip_confirm=False):
    """卸载"""
    if not skip_confirm:
        if input("确认卸载? [y/N]: ").lower() != 'y':
            return

    run_cmd("systemctl stop hysteria-server", check=False)
    run_cmd("systemctl disable hysteria-server", check=False)
    SERVICE_FILE.unlink(missing_ok=True)
    BINARY_PATH.unlink(missing_ok=True)

    if not skip_confirm and input("删除配置文件? [y/N]: ").lower() == 'y':
        shutil.rmtree(CONFIG_DIR, ignore_errors=True)
        shutil.rmtree(CLIENT_DIR, ignore_errors=True)

    run_cmd("systemctl daemon-reload", check=False)
    green("已卸载")

# ============ 修改配置 ==========
def change_config():
    """修改配置"""
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
        new_pwd = input(f"\n新密码 (回车随机): ").strip() or generate_password(8)
        content = config_file.read_text()
        # 单用户模式
        content = re.sub(r'password: \S+', f'password: {new_pwd}', content)
        config_file.write_text(content)
        green(f"密码已修改为: {new_pwd}")

        # 更新客户端配置
        old_url = (CLIENT_DIR / "url.txt").read_text().strip()
        domain = re.search(r'sni=([^#&]+)', old_url)
        if domain:
            domain = domain.group(1)
            server_ip = get_server_ip()
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

# ============ 日志查看 ==========
def show_logs():
    """查看日志"""
    if not SERVICE_FILE.exists():
        red("服务文件不存在，请先安装 Hysteria 2")
        return
    os.system("journalctl -u hysteria-server -f --lines 50")

# ============ 主菜单 ==========
def print_menu():
    """打印菜单"""
    os.system("clear 2>/dev/null || cls 2>/dev/null")
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

def manage_service(action):
    """服务控制"""
    if not SERVICE_FILE.exists():
        red("服务文件不存在，请先安装 Hysteria 2")
        return

    if not BINARY_PATH.exists():
        red("Hysteria 2 未安装")
        return

    if action == "start":
        run_cmd("systemctl start hysteria-server", check=False)
        run_cmd("systemctl enable hysteria-server", check=False)
        green("已启动")
    elif action == "stop":
        run_cmd("systemctl stop hysteria-server", check=False)
        green("已停止")
    elif action == "restart":
        run_cmd("systemctl restart hysteria-server", check=False)
        green("已重启")
    elif action == "status":
        os.system("systemctl status hysteria-server")

def show_config():
    """显示配置"""
    url_file = CLIENT_DIR / "url.txt"
    if url_file.exists():
        print("\n" + "="*60)
        yellow("分享链接:")
        print(url_file.read_text())
        print("\n二维码:")
        qrcode = generate_qrcode(url_file.read_text().strip())
        if qrcode:
            print(qrcode)
        print("="*60)
    else:
        red("配置文件不存在")

def main():
    """主函数"""
    while True:
        print_menu()
        choice = input("\n请选择 [0-9]: ").strip()

        install_status = get_install_status()

        if choice == "1":
            if install_status == 0:
                # 未安装 - 执行安装
                install_hy2()
            elif install_status == 1:
                # 部分安装 - 继续配置
                run_config_wizard()
            else:
                # 已安装 - 重新配置
                if input("是否重新配置? [y/N]: ").lower() == 'y':
                    run_config_wizard()

        elif choice == "2":
            if install_status >= 1:
                uninstall_hy2()
            else:
                red("未安装，无需卸载")

        elif choice == "3":
            manage_service("start")
        elif choice == "4":
            manage_service("stop")
        elif choice == "5":
            manage_service("restart")
        elif choice == "6":
            manage_service("status")
        elif choice == "7":
            show_logs()

        elif choice == "8":
            if install_status >= 2:
                change_config()
            else:
                red("请先完成安装和配置")

        elif choice == "9":
            if install_status >= 2:
                show_config()
            else:
                red("请先完成安装和配置")

        elif choice in ["0", "q", "Q"]:
            print("\n再见!")
            break
        else:
            red("无效选择")

        input("\n回车返回...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消")
        sys.exit(0)
