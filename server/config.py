import threading
from typing import Optional


class Config:
    _instance = None
    _lock = threading.Lock()
    _price_per_unit: Optional[float] = None
    _standing_charge: Optional[float] = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Config, cls).__new__(cls)
            return cls._instance

    @classmethod
    def initialize(cls, price_per_unit: float, standing_charge: float) -> None:
        with cls._lock:
            if cls._price_per_unit is not None:
                raise RuntimeError("Config already initialized")
            if price_per_unit <= 0:
                raise ValueError("Price per unit must be positive")
            if standing_charge < 0:
                raise ValueError("Standing charge cannot be negative")
            cls._price_per_unit = price_per_unit
            cls._standing_charge = standing_charge

    @classmethod
    def get_price_per_unit(cls) -> float:
        if cls._price_per_unit is None:
            raise RuntimeError("Config not initialized")
        return cls._price_per_unit

    @classmethod
    def get_standing_charge(cls) -> float:
        if cls._standing_charge is None:
            raise RuntimeError("Config not initialized")
        return cls._standing_charge
