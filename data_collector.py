"""
Market data collection module with multi-exchange support and real-time streaming.
Implements robust error handling, rate limiting, and data validation.
"""
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import aiohttp

@dataclass
class MarketData:
    """Structured market data container"""
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: Optional[float] = None
    quote_volume: Optional[float] = None
    trade_count: Optional[int] = None

class DataCollector:
    """Responsible for collecting and validating market data from multiple exchanges"""
    
    def __init__(self, config):
        self.config = config
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.initialize_exchanges()
        
    def initialize_exchanges(self):
        """Initialize exchange connections with error handling"""
        for exchange_name, exchange_config in self.config.exchanges.items():
            try:
                if exchange_config.api_key and exchange_config.secret:
                    exchange_class = getattr(ccxt, exchange_name)
                    self.exchanges[exchange_name] = exchange_class({
                        'apiKey': exchange_config.api_key,
                        'secret': exchange_config.secret,
                        'enableRateLimit': exchange_config.enable_rate_limit,
                        'timeout': 30000,
                        'options': {
                            'defaultType': 'spot',
                            'adjustForTimeDifference': True
                        }
                    })
                    logging.info(f"Initialized {exchange_name} exchange")
                else:
                    logging.warning(f"No API credentials for