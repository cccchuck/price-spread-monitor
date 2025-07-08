import asyncio
import aiohttp
import websockets
import json
import logging
from typing import Optional, Callable

class OKXPriceStream:
    def __init__(self, callback: Callable[[float, float, float], None]):
        self.callback = callback
        self.logger = logging.getLogger(__name__)
        self.ws_url = "wss://ws.okx.com:8443/ws/v5/public"
        self.ws = None
        
    async def connect(self):
        try:
            self.ws = await websockets.connect(self.ws_url)
            # 订阅BTC-USDT永续合约盘口数据
            subscribe_msg = {
                "op": "subscribe",
                "args": [{"channel": "books", "instId": "BTC-USDT-SWAP"}]
            }
            await self.ws.send(json.dumps(subscribe_msg))
            self.logger.info("OKX WebSocket connected and subscribed")
        except Exception as e:
            self.logger.error(f"Failed to connect to OKX: {e}")
            raise
            
    async def listen(self):
        try:
            async for message in self.ws:
                data = json.loads(message)
                if "data" in data and data["data"]:
                    book_data = data["data"][0]
                    if "bids" in book_data and "asks" in book_data:
                        bid = float(book_data["bids"][0][0])
                        ask = float(book_data["asks"][0][0])
                        timestamp = float(book_data["ts"]) / 1000
                        self.callback(bid, ask, timestamp)
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("OKX WebSocket connection closed")
        except Exception as e:
            self.logger.error(f"Error in OKX listener: {e}")
            
    async def close(self):
        if self.ws:
            await self.ws.close()

class AsterPriceStream:
    def __init__(self, callback: Callable[[float, float, float], None]):
        self.callback = callback
        self.logger = logging.getLogger(__name__)
        self.ws_url = "wss://fstream.asterdex.com/ws/BTCUSDT@bookTicker"
        self.ws = None
        
    async def connect(self):
        try:
            self.ws = await websockets.connect(self.ws_url)
            self.logger.info("Aster WebSocket connected")
        except Exception as e:
            self.logger.error(f"Failed to connect to Aster: {e}")
            raise
            
    async def listen(self):
        try:
            async for message in self.ws:
                data = json.loads(message)
                bid = float(data["b"])
                ask = float(data["a"])
                timestamp = float(data["E"]) / 1000
                self.callback(bid, ask, timestamp)
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("Aster WebSocket connection closed")
        except Exception as e:
            self.logger.error(f"Error in Aster listener: {e}")
            
    async def close(self):
        if self.ws:
            await self.ws.close()