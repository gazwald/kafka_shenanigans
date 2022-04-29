from enum import Enum


class MessageType(str, Enum):
    heartbeat: str = "pricing.PricingHeartbeat"
    price: str = "pricing.ClientPrice"


class HostType(str, Enum):
    stream: str = "stream-fxtrade.oanda.com"
    api: str = "api-fxtrade.oanda.com"
