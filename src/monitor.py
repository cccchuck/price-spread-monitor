import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class PriceData:
    exchange: str
    symbol: str
    bid: float
    ask: float
    timestamp: float


class PriceMonitor:
    def __init__(self):
        self.okx_price: Optional[PriceData] = None
        self.aster_price: Optional[PriceData] = None
        self.logger = logging.getLogger(__name__)

    def update_okx_price(self, bid: float, ask: float, timestamp: float):
        self.okx_price = PriceData("OKX", "BTC/USDT", bid, ask, timestamp)

    def update_aster_price(self, bid: float, ask: float, timestamp: float):
        self.aster_price = PriceData("Aster", "BTC/USDT", bid, ask, timestamp)

    def calculate_spreads(self) -> Optional[Dict[str, float]]:
        if not self.okx_price or not self.aster_price:
            return None

        # OKX买入 Aster卖出的价差 (Aster ask - OKX bid)
        # OKX限价 Aster市价
        okx_buy_aster_sell = self.aster_price.bid / self.okx_price.bid - 1

        # Aster买入 OKX卖出的价差 (OKX ask - Aster bid)
        # OKX限价 Aster市价
        aster_buy_okx_sell = self.okx_price.ask / self.aster_price.ask - 1

        return {
            "okx_buy_aster_sell": okx_buy_aster_sell,
            "aster_buy_okx_sell": aster_buy_okx_sell,
            "okx_bid": self.okx_price.bid,
            "okx_ask": self.okx_price.ask,
            "aster_bid": self.aster_price.bid,
            "aster_ask": self.aster_price.ask
        }
