"""
客户端配置生成模块
"""

import json
from pathlib import Path
from urllib.parse import quote


def generate_client_config(server_ip, port, password, domain, hop_ports=None):
    """
    生成客户端配置

    Args:
        server_ip: 服务器IP
        port: 端口
        password: 密码
        domain: 域名/SNI
        hop_ports: 端口跳跃范围

    Returns:
        分享链接字符串
    """
    from ..config import CLIENT_DIR
    from ..utils.helpers import is_ipv6
    from ..utils.output import yellow

    CLIENT_DIR.mkdir(parents=True, exist_ok=True)

    server_addr = f"[{server_ip}]" if is_ipv6(server_ip) else server_ip

    # 端口跳跃
    port_str = f"{port},{hop_ports}" if hop_ports else str(port)

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

    return share_url


def show_config():
    """显示客户端配置"""
    from ..config import CLIENT_DIR
    from ..utils.output import red, yellow
    from ..utils.helpers import generate_qrcode

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
