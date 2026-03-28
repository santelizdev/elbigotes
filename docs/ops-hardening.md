# Ops Hardening Runbook

Este documento deja el mínimo de endurecimiento para que:

- el stack Docker se recupere solo después de reinicios del host o del daemon
- se reduzca el riesgo de apagarlo por error
- SSH deje de depender de password
- exista trazabilidad de comandos y sesiones

## 1. Docker: recuperación automática

El `docker-compose.yml` del proyecto ya usa:

```yaml
restart: unless-stopped
```

en todos los servicios principales.

Eso ayuda si:

- reinicia el VPS
- reinicia Docker
- el daemon levanta nuevamente

No evita una caída intencional por `docker compose down`.

## 2. Operativa segura

Evita esta secuencia salvo mantención:

```bash
docker compose down
```

Usa en cambio:

```bash
docker compose up -d
docker compose up -d --build web
docker compose up -d --build frontend
docker compose ps
docker compose logs -f web frontend
```

Atajos del repo:

```bash
make up-detached
make restart-web
make restart-frontend
make status
make logs-app
```

Alias recomendados para `deploy`:

```bash
echo 'alias dcup="docker compose up -d"' >> ~/.bashrc
echo 'alias dcweb="docker compose up -d --build web"' >> ~/.bashrc
echo 'alias dcfront="docker compose up -d --build frontend"' >> ~/.bashrc
echo 'alias dcps="docker compose ps"' >> ~/.bashrc
echo 'alias dclogs="docker compose logs -f web frontend"' >> ~/.bashrc
source ~/.bashrc
```

## 3. SSH: cambiar password por llaves

### 3.1 Generar llave en tu máquina local

Si no tienes una:

```bash
ssh-keygen -t ed25519 -C "deploy@elbigotes"
```

### 3.2 Copiar la llave al servidor

```bash
ssh-copy-id deploy@TU_IP_O_HOST
```

Prueba acceso:

```bash
ssh deploy@TU_IP_O_HOST
```

### 3.3 Endurecer SSH en el VPS

Edita:

```bash
sudo nano /etc/ssh/sshd_config
```

Deja al menos:

```text
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
ChallengeResponseAuthentication no
UsePAM yes
```

Valida:

```bash
sudo sshd -t
```

Reinicia:

```bash
sudo systemctl restart ssh
```

Importante:

- no cierres tu sesión actual hasta probar una nueva sesión SSH con llave

## 4. Bloqueo básico de fuerza bruta

Instala `fail2ban`:

```bash
sudo apt-get update
sudo apt-get install -y fail2ban
```

Crea configuración local:

```bash
sudo tee /etc/fail2ban/jail.local >/dev/null <<'EOF'
[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 5
findtime = 10m
bantime = 1h
EOF
```

Activa:

```bash
sudo systemctl enable --now fail2ban
sudo fail2ban-client status sshd
```

## 5. Trazabilidad real de comandos

### Opción A: `auditd` para comandos sensibles

Instalación:

```bash
sudo apt-get install -y auditd audispd-plugins
sudo systemctl enable --now auditd
```

Reglas sugeridas para Docker y SSH:

```bash
sudo tee /etc/audit/rules.d/docker-ops.rules >/dev/null <<'EOF'
-w /usr/bin/docker -p x -k docker_ops
-w /usr/bin/dockerd -p x -k docker_daemon
-w /usr/bin/docker-compose -p x -k docker_ops
-w /usr/bin/ssh -p x -k ssh_exec
-w /usr/bin/sudo -p x -k sudo_exec
EOF
```

Recarga:

```bash
sudo augenrules --load
sudo systemctl restart auditd
```

Consultas útiles:

```bash
sudo ausearch -k docker_ops --start today
sudo ausearch -k sudo_exec --start today
```

### Opción B: `psacct` para historial de procesos

Instalación:

```bash
sudo apt-get install -y acct
sudo systemctl enable --now acct
```

Consultas:

```bash
lastcomm | head -n 50
lastcomm docker | head -n 50
lastcomm docker-compose | head -n 50
```

Recomendación:

- usa `auditd` si quieres trazabilidad más fuerte
- usa `psacct` como complemento liviano

## 6. Verificación posterior

Después del hardening:

```bash
docker compose ps
sudo systemctl status ssh --no-pager
sudo fail2ban-client status sshd
sudo ausearch -k docker_ops --start today | tail -n 20
lastcomm docker | head -n 20
```

## 7. Resumen operativo

1. llaves SSH funcionando
2. password login desactivado
3. fail2ban activo
4. auditd o psacct activo
5. `restart: unless-stopped` desplegado
6. operativa diaria sin `docker compose down`
