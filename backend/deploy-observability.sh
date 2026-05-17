#!/bin/bash
# Loki + Grafana 部署脚本
# 用于服务器上安装和配置日志系统

set -e

LOKI_VERSION="2.9.4"
GRAFANA_VERSION="10.2.3"
INSTALL_DIR="/opt/observability"
LOKI_PORT=3100
GRAFANA_PORT=3200

echo "===== 开始部署 Loki + Grafana ====="

# 创建安装目录
echo "1. 创建安装目录..."
sudo mkdir -p $INSTALL_DIR/loki $INSTALL_DIR/grafana/data
sudo mkdir -p /opt/loki/chunks /opt/loki/index /opt/loki/rules

# 下载并安装 Loki
echo "2. 下载安装 Loki v${LOKI_VERSION}..."
cd $INSTALL_DIR/loki
if [ ! -f loki ]; then
    sudo wget -q https://github.com/grafana/loki/releases/download/v${LOKI_VERSION}/loki-linux-amd64.zip
    sudo unzip -o loki-linux-amd64.zip
    sudo mv loki-linux-amd64 loki
    sudo rm loki-linux-amd64.zip
fi
sudo chmod +x loki

# 下载并安装 Grafana
echo "3. 下载安装 Grafana v${GRAFANA_VERSION}..."
cd $INSTALL_DIR
if [ ! -d grafana-${GRAFANA_VERSION} ]; then
    sudo wget -q https://dl.grafana.com/oss/release/grafana-${GRAFANA_VERSION}.linux-amd64.tar.gz
    sudo tar -xzf grafana-${GRAFANA_VERSION}.linux-amd64.tar.gz
    sudo rm grafana-${GRAFANA_VERSION}.linux-amd64.tar.gz
fi
sudo chmod +x grafana-${GRAFANA_VERSION}/bin/grafana-server

# 配置 Loki systemd 服务
echo "4. 配置 Loki systemd 服务..."
sudo tee /etc/systemd/system/loki.service > /dev/null <<EOF
[Unit]
Description=Loki Log Aggregation System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR/loki
ExecStart=$INSTALL_DIR/loki/loki -config.file=$INSTALL_DIR/loki/loki-config.yml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 配置 Grafana systemd 服务
echo "5. 配置 Grafana systemd 服务..."
sudo mkdir -p /etc/grafana/provisioning/datasources /etc/grafana/provisioning/dashboards /var/lib/grafana/dashboards

sudo tee /etc/grafana/provisioning/datasources/datasources.yml > /dev/null <<EOF
apiVersion: 1

datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://localhost:${LOKI_PORT}
    isDefault: true
    editable: false
EOF

sudo tee /etc/grafana/provisioning/dashboards/dashboards.yml > /dev/null <<EOF
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /var/lib/grafana/dashboards
EOF

sudo tee /etc/grafana/grafana.ini > /dev/null <<EOF
[server]
http_port = ${GRAFANA_PORT}

[security]
admin_user = admin
admin_password = admin123

[users]
allow_sign_up = false

[auth]
disable_login_form = false
EOF

sudo tee /etc/systemd/system/grafana.service > /dev/null <<EOF
[Unit]
Description=Grafana Visualization Platform
After=network.target

[Service]
Type=simple
User=root
ExecStart=$INSTALL_DIR/grafana-${GRAFANA_VERSION}/bin/grafana-server \
    --config=/etc/grafana/grafana.ini \
    --homepath=$INSTALL_DIR/grafana-${GRAFANA_VERSION}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 创建 Loki 配置文件
echo "6. 创建 Loki 配置文件..."
sudo tee $INSTALL_DIR/loki/loki-config.yml > /dev/null <<EOF
# Loki Configuration for Production Server
auth_enabled: false

server:
  http_listen_port: ${LOKI_PORT}
  grpc_listen_port: 9096
  log_level: info

common:
  path_prefix: /opt/loki
  storage:
    filesystem:
      chunks_directory: /opt/loki/chunks
      rules_directory: /opt/loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

storage_config:
  boltdb:
    index:
      shared_store: filesystem
      path: /opt/loki/index
  filesystem:
    directory: /opt/loki/chunks

compactor:
  working_directory: /opt/loki/compactor
  shared_store: filesystem

limits_config:
  reject_old_samples: true
  reject_old_samples_max_age: 168h
  ingestion_rate_mb: 50
  ingestion_burst_size_mb: 100

schema_config:
  configs:
    - from: 2024-01-01
      store: boltdb
      object_store: filesystem
      schema: v12
      index:
        prefix: index_
        period: 24h
EOF

# 启动服务
echo "7. 启动服务..."
sudo systemctl daemon-reload
sudo systemctl enable loki
sudo systemctl enable grafana
sudo systemctl start loki
sudo systemctl start grafana

echo "===== 部署完成 ====="
echo ""
echo "服务状态:"
sudo systemctl status loki --no-pager
sudo systemctl status grafana --no-pager
echo ""
echo "访问地址:"
echo "  - Grafana: http://$(hostname -I | awk '{print $1}'):${GRAFANA_PORT}"
echo "  - Loki API: http://localhost:${LOKI_PORT}"
echo ""
echo "默认账号: admin / admin123"
