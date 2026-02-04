"""
Hysteria 2 一键安装脚本 - 主入口
作者: w0x7ce

支持:
    python -m hy2
    python hy2/__main__.py
"""

import sys

from hy2.installer import install_hy2, uninstall_hy2, change_config, run_config_wizard
from hy2.client import show_config
from hy2.service import manage_service, show_logs
from hy2.utils.output import print_menu, red, yellow
from hy2.utils.helpers import get_install_status


def main():
    """主函数 - 交互式菜单"""
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
