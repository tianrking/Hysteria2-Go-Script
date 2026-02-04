#!/usr/bin/env python3
"""
Hysteria 2 一键安装脚本 - CLI 包装器
直接运行此文件即可，无需安装

使用方法:
    python3 hy2_cli.py
    或
    chmod +x hy2_cli.py && ./hy2_cli.py
"""

import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from __main__ import main

if __name__ == "__main__":
    main()
