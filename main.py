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
        self.tasks = []

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
            self.logger.info(f"OKX买Aster卖价差: {spreads['okx_buy_aster_sell']:.6f}, "
                             f"Aster买OKX卖价差: {spreads['aster_buy_okx_sell']:.6f}")

    async def start(self):
        self.logger.info("启动价差监控服务...")

        # 启动Prometheus服务器
        self.metrics.start_server()

        # 连接WebSocket流
        await self.okx_stream.connect()
        await self.aster_stream.connect()

        # 启动监听任务
        self.tasks = [
            asyncio.create_task(self.okx_stream.listen()),
            asyncio.create_task(self.aster_stream.listen()),
        ]

        try:
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            self.logger.info("服务被取消，正在关闭...")
        except Exception as e:
            self.logger.error(f"服务运行错误: {e}")

    async def cleanup(self):
        self.logger.info("正在清理资源...")

        # 取消所有任务
        for task in self.tasks:
            if not task.done():
                task.cancel()

        # 等待任务完成
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        # 关闭WebSocket连接
        await self.okx_stream.close()
        await self.aster_stream.close()

        self.logger.info("资源清理完成")

    def signal_handler(self):
        self.logger.info(f"收到信号，正在停止服务...")
        self.running = False

        # 停止流
        self.okx_stream.running = False
        self.aster_stream.running = False

        # 取消所有任务
        for task in self.tasks:
            if not task.done():
                task.cancel()


async def main():
    service = SpreadMonitorService()

    # 设置信号处理
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, service.signal_handler)

    try:
        await service.start()
    except KeyboardInterrupt:
        logging.info("收到键盘中断，正在停止服务...")
    except Exception as e:
        logging.error(f"服务运行出错: {e}")
    finally:
        await service.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
