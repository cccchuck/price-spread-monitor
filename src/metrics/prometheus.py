from prometheus_client import Gauge, start_http_server, REGISTRY
import logging
from typing import Dict, Any

class PrometheusMetrics:
    def __init__(self, port: int = 8000):
        self.port = port
        self.logger = logging.getLogger(__name__)
        
        # 定义指标
        self.okx_buy_aster_sell_spread = Gauge(
            'okx_buy_aster_sell_spread',
            'Price spread for buying on OKX and selling on Aster'
        )
        
        self.aster_buy_okx_sell_spread = Gauge(
            'aster_buy_okx_sell_spread', 
            'Price spread for buying on Aster and selling on OKX'
        )
        
        self.okx_bid_price = Gauge('okx_bid_price', 'OKX BTC bid price')
        self.okx_ask_price = Gauge('okx_ask_price', 'OKX BTC ask price')
        self.aster_bid_price = Gauge('aster_bid_price', 'Aster BTC bid price')
        self.aster_ask_price = Gauge('aster_ask_price', 'Aster BTC ask price')
        
    def start_server(self):
        start_http_server(self.port)
        self.logger.info(f"Prometheus metrics server started on port {self.port}")
        
    def update_metrics(self, spreads: Dict[str, float]):
        self.okx_buy_aster_sell_spread.set(spreads['okx_buy_aster_sell'])
        self.aster_buy_okx_sell_spread.set(spreads['aster_buy_okx_sell'])
        self.okx_bid_price.set(spreads['okx_bid'])
        self.okx_ask_price.set(spreads['okx_ask'])
        self.aster_bid_price.set(spreads['aster_bid'])
        self.aster_ask_price.set(spreads['aster_ask'])
        
        self.logger.debug(f"Updated metrics: {spreads}")