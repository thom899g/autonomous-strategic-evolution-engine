"""
Configuration management for the Autonomous Strategic Evolution Engine.
Centralizes all environment variables, Firebase credentials, and system parameters.
"""
import os
from dataclasses import dataclass
from typing import Dict, Any
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

@dataclass
class ExchangeConfig:
    """Exchange API configuration"""
    name: str
    api_key: str
    secret: str
    enable_rate_limit: bool = True

@dataclass
class EvolutionConfig:
    """Evolution algorithm parameters"""
    population_size: int = 100
    generations: int = 50
    mutation_rate: float = 0.15
    crossover_rate: float = 0.85
    elitism_count: int = 5
    strategy_complexity: int = 10  # Max indicators per strategy

@dataclass
class RiskConfig:
    """Risk management parameters"""
    max_position_size: float = 0.1  # 10% of portfolio per trade
    max_drawdown: float = 0.2  # 20% max drawdown
    stop_loss_pct: float = 0.02  # 2% stop loss
    take_profit_pct: float = 0.04  # 4% take profit

class TradingConfig:
    """Main configuration manager"""
    
    def __init__(self):
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.firebase_project_id = os.getenv('FIREBASE_PROJECT_ID')
        self.firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase_credentials.json')
        
        # Initialize Firebase
        self.firebase_app = self._init_firebase()
        self.firestore_client = firestore.client(self.firebase_app)
        
        # Exchange configurations
        self.exchanges = {
            'binance': ExchangeConfig(
                name='binance',
                api_key=os.getenv('BINANCE_API_KEY', ''),
                secret=os.getenv('BINANCE_API_SECRET', '')
            ),
            'coinbase': ExchangeConfig(
                name='coinbase',
                api_key=os.getenv('COINBASE_API_KEY', ''),
                secret=os.getenv('COINBASE_API_SECRET', '')
            )
        }
        
        self.evolution_config = EvolutionConfig()
        self.risk_config = RiskConfig()
        
        # Trading pairs and timeframes
        self.trading_pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT']
        self.timeframes = ['5m', '15m', '1h', '4h', '1d']
        
        # Performance tracking
        self.performance_update_interval = 300  # 5 minutes
        
    def _init_firebase(self):
        """Initialize Firebase Admin SDK with error handling"""
        try:
            # Check if Firebase app already exists
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.firebase_credentials_path)
                app = firebase_admin.initialize_app(cred)
                logging.info("Firebase initialized successfully")
                return app
            else:
                return firebase_admin.get_app()
        except Exception as e:
            logging.error(f"Failed to initialize Firebase: {e}")
            # Fallback to memory storage if Firebase fails
            logging.warning("Using memory storage as fallback")
            return None
    
    def validate(self) -> bool:
        """Validate all required configurations"""
        required_vars = ['FIREBASE_PROJECT_ID', 'FIREBASE_CREDENTIALS_PATH']
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            logging.error(f"Missing required environment variables: {missing}")
            return False
        
        if not os.path.exists(self.firebase_credentials_path):
            logging.error(f"Firebase credentials file not found: {self.firebase_credentials_path}")
            return False
            
        return True

# Global configuration instance
config = TradingConfig()