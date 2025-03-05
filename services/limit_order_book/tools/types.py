from dataclasses import dataclass


@dataclass
class Order:
    sign: int
    price: float
    volume: float
    time_stamp: int
    date: str


@dataclass
class DailyInfo:
    limit_orders_buy: list = None
    limit_orders_sell: list = None
    market_orders_buy: list = None
    market_orders_sell: list = None
    executed_orders: list = None
    bid_price: list = None
    ask_price: list = None
    bid_ask_spread: list = None
    rate_distance: list = None
    bid_rate_distance: list = None
    ask_rate_distance: list = None
    mid_price: list = None
    old_buy_orders: list = None
    old_sell_orders: list = None
    delta_p: list = None
    market_order_volumes: list = None

    def __post_init__(self):
        self.limit_orders_buy = []
        self.limit_orders_sell = []
        self.market_orders_buy = []
        self.market_orders_sell = []
        self.executed_orders = []
        self.bid_price = []
        self.ask_price = []
        self.bid_ask_spread = []
        self.rate_distance = []
        self.bid_rate_distance = []
        self.ask_rate_distance = []
        self.mid_price = []
        self.old_buy_orders = []
        self.old_sell_orders = []
        self.delta_p = []
        self.market_order_volumes = []
