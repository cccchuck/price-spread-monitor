import asyncio
import logging
import signal
import sys
from src.monitor import PriceMonitor
from src.exchange.streams import OKXPriceStream, AsterPriceStream
from src.metrics.prometheus import PrometheusMetrics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class SpreadMonitorService:
    def __init__(self):
        self.monitor = PriceMonitor()
        self.metrics = PrometheusMetrics()
        self.okx_stream = OKXPriceStream(self.on_okx_price_update)
        self.aster_stream = AsterPriceStream(self.on_aster_price_update)
        self.logger = logging.getLogger(__name__)
        self.running = True
        
    def on_okx_price_update(self, bid: float, ask: float, timestamp: float):
        self.monitor.update_okx_price(bid, ask, timestamp)
        self.update_metrics()
        
    def on_aster_price_update(self, bid: float, ask: float, timestamp: float):
        self.monitor.update_aster_price(bid, ask, timestamp)
        self.update_metrics()
        
    def update_metrics(self):
        spreads = self.monitor.calculate_spreads()
        if spreads:
            self.metrics.update_metrics(spreads)
            self.logger.info(f"OKX买Aster卖价差: {spreads['okx_buy_aster_sell']:.2f}, "
                           f"Aster买OKX卖价差: {spreads['aster_buy_okx_sell']:.2f}")
            
    async def start(self):
        self.logger.info("启动价差监控服务...")
        
        # 启动Prometheus服务器
        self.metrics.start_server()
        
        # 连接WebSocket流
        await self.okx_stream.connect()
        await self.aster_stream.connect()
        
        # 启动监听任务
        tasks = [
            asyncio.create_task(self.okx_stream.listen()),
            asyncio.create_task(self.aster_stream.listen()),
        ]
        
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            self.logger.info("服务被取消，正在关闭...")
        finally:
            await self.okx_stream.close()
            await self.aster_stream.close()
            
    def signal_handler(self, signum, frame):
        self.logger.info(f"收到信号 {signum}，正在停止服务...")
        self.running = False
        
async def main():
    service = SpreadMonitorService()
    
    # 设置信号处理
    signal.signal(signal.SIGINT, service.signal_handler)
    signal.signal(signal.SIGTERM, service.signal_handler)
    
    try:
        await service.start()
    except KeyboardInterrupt:
        logging.info("收到键盘中断，正在停止服务...")

if __name__ == "__main__":
    asyncio.run(main())