"""
Hysteria 2 安装脚本 - 模块化版本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 在 hy2/ 目录内运行，需要指定包位置
setup(
    name="hy2-installer",
    version="2.0.0",
    author="w0x7ce",
    author_email="tian.r.king@gmail.com",
    description="Hysteria 2 一键安装脚本 - 模块化版本",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tianrking/Hysteria2-Go-Script",
    packages=find_packages("."),
    package_dir={"": "."},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "hy2=__main__:main",
        ],
    },
)
