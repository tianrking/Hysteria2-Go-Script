# Hysteria 2 一键安装脚本

Ubuntu VPS 上一键安装 Hysteria 2 的脚本。

## 功能特点

- 自动安装 Hysteria 2
- 支持自签证书、自定义证书和 Let's Encrypt (ACME) 自动申请
- 自动配置防火墙 (ufw/firewalld)
- 支持 BBR 加速优化
- 交互式菜单界面
- 多用户管理支持
- 端口跳跃功能
- 客户端配置二维码生成

## 系统要求

- 操作系统: Ubuntu 18.04+
- 权限: Root/sudo
- 架构: amd64, arm64, arm

## 快速安装

```bash
curl -fsSL https://raw.githubusercontent.com/w0x7ce/Hysteria2-Go-Script/main/hy2.py | python3 -
```

或下载脚本后运行：

```bash
wget https://raw.githubusercontent.com/w0x7ce/Hysteria2-Go-Script/main/hy2.py
python3 hy2.py
```

或作为 Python 模块运行：

```bash
python3 -m hy2
```

## 使用方法

### 运行脚本

```bash
python3 hy2.py
```

### 主菜单

```
============================================================
Hysteria 2 一键安装脚本
作者: w0x7ce
============================================================
状态: 未安装
============================================================
1. 安装 Hysteria 2
------------------------------------------------------------
3. 启动服务
4. 停止服务
5. 重启服务
6. 查看状态
7. 查看日志
------------------------------------------------------------
8. 修改配置
9. 显示配置
------------------------------------------------------------
0. 退出
```

### 菜单选项说明

| 选项 | 功能 |
|------|------|
| 1 | 安装或重新配置 Hysteria 2 |
| 2 | 卸载 Hysteria 2 |
| 3 | 启动服务 |
| 4 | 停止服务 |
| 5 | 重启服务 |
| 6 | 查看服务状态 |
| 7 | 查看实时日志 |
| 8 | 修改现有配置 |
| 9 | 显示客户端配置 |
| 0 | 退出脚本 |

## 配置向导

安装过程中，需要配置以下内容：

1. **端口** (1-65535) - 回车随机生成
2. **端口跳跃** (可选) - 提高安全性
3. **密码** - 回车随机生成
4. **伪装站点** - 默认: maimai.sega.jp
5. **多用户** (可选) - 添加更多用户
6. **证书类型**:
   - 自签证书 (默认)
   - 自定义证书
   - Let's Encrypt (ACME) - 需要域名
7. **BBR 加速** (可选) - 性能优化

## 客户端配置

安装完成后，客户端配置文件将保存在 `~/hy/` 目录：

- `hy-client.yaml` - 客户端 YAML 配置
- `hy-client.json` - 客户端 JSON 配置
- `url.txt` - 分享链接
- **二维码** - 安装结束时显示

### 分享链接格式

```
hysteria2://密码@服务器:端口/?insecure=1&sni=域名#HY2
```

## 修改配置

选择主菜单选项 8 可以修改：

1. 端口
2. 密码
3. 证书
4. 伪装站点

## 系统命令

### 查看服务状态

```bash
systemctl status hysteria-server
```

### 启动/停止/重启

```bash
systemctl start hysteria-server
systemctl stop hysteria-server
systemctl restart hysteria-server
```

### 查看日志

```bash
journalctl -u hysteria-server -f
```

### 开机自启

```bash
systemctl enable hysteria-server
systemctl disable hysteria-server
```

## 配置文件位置

| 文件 | 位置 |
|------|------|
| 服务端配置 | `/etc/hysteria/config.yaml` |
| 二进制文件 | `/usr/local/bin/hysteria` |
| systemd 服务 | `/etc/systemd/system/hysteria-server.service` |
| 客户端配置 | `~/hy/` |
| SSL 证书 | `/etc/hysteria/cert.crt` |
| SSL 私钥 | `/etc/hysteria/private.key` |

## 卸载

选择主菜单选项 2 或运行：

```bash
python3 hy2.py
# 选择选项 2
```

卸载时可以选择是否删除配置文件。

## 常见问题

### 服务无法启动

查看日志：
```bash
journalctl -u hysteria-server -n 50
```

### 端口已被占用

选择选项 8 (修改配置) > 1 (修改端口)

### 证书错误

选择选项 8 (修改配置) > 3 (修改证书)

### 防火墙问题

确保端口已开放：
```bash
# ufw
sudo ufw allow 端口/udp

# firewalld
sudo firewall-cmd --permanent --add-port=端口/udp
sudo firewall-cmd --reload
```

## 安全建议

- 使用强密码 (至少8位)
- 启用端口跳跃提高安全性
- 尽可能使用有效的 SSL 证书
- 保持系统更新

## 相关资源

- [Hysteria 2 官方文档](https://hysteria2.github.io/)
- [GitHub 仓库](https://github.com/apernet/hysteria)
- [问题反馈](https://github.com/w0x7ce/Hysteria2-Go-Script/issues)

## 许可证

MIT License

## 作者

w0x7ce

---
**注意**: 本脚本仅供学习和测试使用，请遵守当地法律法规。
