# BTC 价差监控系统

这是一个监控 OKX 和 Aster BTC 价差的系统，能够实时追踪两个交易所的价格差异，并通过 Prometheus 和 Grafana 提供可视化监控。

## 功能特性

- 实时监控 OKX 和 Aster 的 BTC/USDT 价格
- 计算 "OKX买入 Aster卖出" 和 "Aster买入 OKX卖出" 的价差
- 将指标数据推送到 Prometheus
- 通过 Grafana 看板直观显示价差变化

## 快速开始

### 使用 Docker Compose 启动

```bash
cd price-spread-monitor
docker-compose up -d
```

这将启动以下服务：
- `spread-monitor`: 价差监控服务 (端口 8000)
- `prometheus`: Prometheus 服务器 (端口 9090)
- `grafana`: Grafana 看板 (端口 3000)

### 访问服务

- Grafana 看板: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- 指标端点: http://localhost:8000/metrics

## 指标说明

- `okx_buy_aster_sell_spread`: OKX买入 Aster卖出的价差 (Aster ask - OKX bid)
- `aster_buy_okx_sell_spread`: Aster买入 OKX卖出的价差 (OKX ask - Aster bid)
- `okx_bid_price`/`okx_ask_price`: OKX 的买入/卖出价格
- `aster_bid_price`/`aster_ask_price`: Aster 的买入/卖出价格

## 项目结构

```
price-spread-monitor/
├── src/
│   ├── monitor.py          # 价差计算逻辑
│   ├── exchange/
│   │   └── streams.py      # OKX 和 Aster WebSocket 连接
│   └── metrics/
│       └── prometheus.py   # Prometheus 指标导出
├── grafana/
│   ├── dashboards/         # Grafana 看板配置
│   └── datasources/        # 数据源配置
├── docker/
│   └── prometheus.yml      # Prometheus 配置
├── main.py                 # 主程序入口
├── docker-compose.yml      # Docker 编排文件
└── Dockerfile             # 容器构建文件
```