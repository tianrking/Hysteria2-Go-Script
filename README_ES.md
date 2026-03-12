# Hysteria 2 Script de Instalación

Script de instalación en un solo clic para Hysteria 2 en servidores Ubuntu.

## Características

- Instalación automática de Hysteria 2
- Soporte para certificados SSL autofirmados, personalizados y Let's Encrypt (ACME)
- Configuración de firewall automática (ufw/firewalld)
- Soporte para BBR para optimización de rendimiento
- Interfaz de menú interactiva
- Gestión de múltiples usuarios
- Soporte para salto de puertos
- Generación de código QR para configuración del cliente

## Requisitos del Sistema

- Sistema operativo: Ubuntu 18.04+
- Permisos: Root/sudo
- Arquitectura: amd64, arm64, arm

## Instalación Rápida

```bash
curl -fsSL https://raw.githubusercontent.com/w0x7ce/Hysteria2-Go-Script/main/hy2.py | python3 -
```

O descargue el script:

```bash
wget https://raw.githubusercontent.com/w0x7ce/Hysteria2-Go-Script/main/hy2.py
python3 hy2.py
```

O como módulo Python:

```bash
python3 -m hy2
```

## Uso

### Ejecutar el Script

```bash
python3 hy2.py
```

### Menú Principal

```
============================================================
Hysteria 2 Script de Instalación
Autor: w0x7ce
============================================================
Estado: No instalado
============================================================
1. Instalar Hysteria 2
------------------------------------------------------------
3. Iniciar servicio
4. Detener servicio
5. Reiniciar servicio
6. Ver estado
7. Ver registros
------------------------------------------------------------
8. Modificar configuración
9. Mostrar configuración
------------------------------------------------------------
0. Salir
```

### Opciones del Menú

| Opción | Descripción |
|--------|-------------|
| 1 | Instalar o reconfigurar Hysteria 2 |
| 2 | Desinstalar Hysteria 2 |
| 3 | Iniciar el servicio |
| 4 | Detener el servicio |
| 5 | Reiniciar el servicio |
| 6 | Ver el estado del servicio |
| 7 | Ver registros en vivo |
| 8 | Modificar configuración existente |
| 9 | Mostrar configuración del cliente |
| 0 | Salir del script |

## Asistente de Configuración

Durante la instalación, se le pedirá que configure:

1. **Puerto** (1-65535) - Presione Enter para generar aleatoriamente
2. **Salto de puertos** (opcional) - Para mayor seguridad
3. **Contraseña** - Presione Enter para generar aleatoriamente
4. **Sitio de camouflage** - Por defecto: maimai.sega.jp
5. **Múltiples usuarios** (opcional) - Agregue más usuarios
6. **Certificado SSL**:
   - Autofirmado (por defecto)
   - Certificado personalizado
   - Let's Encrypt (ACME) - requiere dominio
7. **BBR** (opcional) - Optimización de rendimiento

## Configuración del Cliente

Después de la instalación, los archivos de configuración del cliente se guardarán en `~/hy/`:

- `hy-client.yaml` - Configuración YAML del cliente
- `hy-client.json` - Configuración JSON del cliente
- `url.txt` - Enlace de compartir (URL)
- **Código QR** - Se muestra al final de la instalación

### URL de Compartir

Formato de URL:
```
hysteria2://PASSWORD@SERVER:PORT/?insecure=1&sni=DOMAIN#HY2
```

## Modificar Configuración

Seleccione la opción 8 del menú para modificar:

1. Puerto
2. Contraseña
3. Certificado
4. Sitio de camouflage

## Comandos de Sistema

### Ver Estado del Servicio

```bash
systemctl status hysteria-server
```

### Iniciar/Detener/Reiniciar

```bash
systemctl start hysteria-server
systemctl stop hysteria-server
systemctl restart hysteria-server
```

### Ver Registros

```bash
journalctl -u hysteria-server -f
```

### Habilitar/Deshabilitar al Inicio

```bash
systemctl enable hysteria-server
systemctl disable hysteria-server
```

## Archivos de Configuración

| Archivo | Ubicación |
|---------|-----------|
| Configuración del servidor | `/etc/hysteria/config.yaml` |
| Binario | `/usr/local/bin/hysteria` |
| Servicio systemd | `/etc/systemd/system/hysteria-server.service` |
| Configuración del cliente | `~/hy/` |
| Certificado SSL | `/etc/hysteria/cert.crt` |
| Clave SSL | `/etc/hysteria/private.key` |

## Desinstalación

Seleccione la opción 2 del menú principal o ejecute:

```bash
python3 hy2.py
# Seleccione la opción 2
```

Durante la desinstalación, puede elegir si eliminar o conservar los archivos de configuración.

## Solución de Problemas

### El servicio no se inicia

Verifique los registros:
```bash
journalctl -u hysteria-server -n 50
```

### El puerto ya está en uso

Seleccione la opción 8 (Modificar configuración) > 1 (Cambiar puerto)

### Errores de certificado

Seleccione la opción 8 (Modificar configuración) > 3 (Cambiar certificado)

### Problemas de firewall

Asegúrese de que el puerto esté abierto:
```bash
# Para ufw
sudo ufw allow PUERTO/udp

# Para firewalld
sudo firewall-cmd --permanent --add-port=PUERTO/udp
sudo firewall-cmd --reload
```

## Seguridad

- Use contraseñas fuertes (mínimo 8 caracteres)
- Habilite el salto de puertos para mayor seguridad
- Use certificados SSL válidos cuando sea posible
- Mantenga el sistema actualizado

## Recursos

- [Documentación de Hysteria 2](https://hysteria2.github.io/)
- [Repositorio de GitHub](https://github.com/apernet/hysteria)
- [Issues y Soporte](https://github.com/w0x7ce/Hysteria2-Go-Script/issues)

## Licencia

MIT License

## Autor

w0x7ce

---
**Nota**: Este script es para fines educativos y de prueba. Úselo bajo su propia responsabilidad.
