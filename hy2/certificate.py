"""
证书处理模块
"""

import os
import shutil
from pathlib import Path


def handle_certificate():
    """
    处理证书配置

    Returns:
        tuple: (证书路径, 私钥路径, 域名)
    """
    from ..utils.output import green, yellow, red
    from ..utils.helpers import run_cmd, get_server_ip
    from ..config import CONFIG_DIR, DEFAULT_CERT_DOMAIN, ACME_EMAIL

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
        return handle_custom_certificate()

    # 默认自签证书
    return generate_self_signed_cert()


def handle_custom_certificate():
    """
    处理自定义证书

    Returns:
        tuple: (证书路径, 私钥路径, 域名)
    """
    from ..utils.output import red

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


def generate_self_signed_cert():
    """
    生成自签证书

    Returns:
        tuple: (证书路径, 私钥路径, 域名)
    """
    from ..utils.output import yellow, green
    from ..utils.helpers import run_cmd
    from ..config import CONFIG_DIR, DEFAULT_CERT_DOMAIN

    yellow("正在生成自签证书...")
    cert_path = CONFIG_DIR / "cert.crt"
    key_path = CONFIG_DIR / "private.key"

    yellow("  - 生成私钥...")
    run_cmd(f"openssl ecparam -genkey -name prime256v1 -out {key_path} 2>/dev/null")
    key_path.chmod(0o600)

    yellow("  - 生成证书...")
    run_cmd(
        f"openssl req -new -x509 -days 36500 -key {key_path} -out {cert_path} "
        f"-subj '/CN={DEFAULT_CERT_DOMAIN}' 2>/dev/null"
    )
    cert_path.chmod(0o644)

    green("证书生成成功!")
    return str(cert_path), str(key_path), DEFAULT_CERT_DOMAIN


def handle_acme_certificate():
    """
    使用 Acme 申请证书

    Returns:
        tuple: (证书路径, 私钥路径, 域名)
    """
    from ..utils.output import yellow, green, red
    from ..utils.helpers import run_cmd, get_server_ip
    from ..config import CONFIG_DIR, ACME_EMAIL

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
    run_cmd(f"curl https://get.acme.sh | sh -s email={ACME_EMAIL}", check=False)
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
    result = run_cmd(
        f"{acme_sh} --issue -d {domain} --standalone -k ec-256 --insecure",
        check=False
    )

    if result and ("Domain not" in result or "error" in result.lower()):
        red("证书申请失败，可能原因:")
        yellow("  - 域名未正确解析")
        yellow("  - 80 端口被占用")
        yellow("  - 防火墙阻止了 80 端口")
        return handle_certificate()

    run_cmd(
        f"{acme_sh} --install-cert -d {domain} --ecc "
        f"--fullchain-file {cert_path} --key-file {key_path}",
        check=False
    )

    if cert_path.exists() and key_path.exists():
        key_path.chmod(0o600)
        cert_path.chmod(0o644)
        green("证书申请成功!")

        # 设置自动续期
        cron_cmd = f"0 0 * * * {acme_sh} --cron -f >/dev/null 2>&1"
        run_cmd(
            f'(crontab -l 2>/dev/null | grep -v "acme.sh"; echo "{cron_cmd}") | crontab -',
            check=False
        )

        return str(cert_path), str(key_path), domain
    else:
        red("证书申请失败")
        return handle_certificate()
