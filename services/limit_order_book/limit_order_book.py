import datetime
from sortedcontainers import SortedKeyList
from collections import defaultdict
from services.limit_order_book.tools.types import DailyInfo
from tools.const import see_first


class LimitOrderBook:
    def __init__(self) -> None:
        self.buy_orders = SortedKeyList(key=lambda x: (-x.price, x.time_stamp))
        self.sell_orders = SortedKeyList(key=lambda x: (x.price, x.time_stamp))
        self.current_date = None
        self.daily_info = defaultdict(lambda: DailyInfo())

    def add_orders_daily(self, orders):
        """Add daily orders to the limit order book."""
        for order in orders:

            if not self.current_date or order.date > self.current_date:
                self.advance_time(order.date)

            if order.sign == 1:
                self.execute_bid_order(order)
            else:
                self.execute_ask_order(order)

            while self.can_execute():
                self.execute_orders(order)

            self.get_prices()

    def execute_bid_order(self, order):
        if self.sell_orders and order.price >= self.sell_orders[0].price:
            quantity_to_execute = min(order.volume, self.sell_orders[0].volume)
            price_to_execute = self.sell_orders[0].price

            # Calculate mid-price
            if self.buy_orders and self.sell_orders:
                mid_price = (self.buy_orders[0].price + self.sell_orders[0].price) / 2
            else:
                mid_price = (
                    price_to_execute  # Fallback if no mid-price can be calculated
                )

            # Calculate Δp
            delta_p = price_to_execute - mid_price
            self.daily_info[self.current_date].delta_p.append(delta_p)

            # Save the market order volume Q
            self.daily_info[self.current_date].market_order_volumes.append(order.volume)

            self.daily_info[self.current_date].executed_orders.append(
                (quantity_to_execute, price_to_execute, order, self.sell_orders[0])
            )
            balance = order.volume - self.sell_orders[0].volume
            match balance:
                case _ if balance > 0:
                    self.sell_orders.pop(0)
                    order.volume -= quantity_to_execute
                    self.buy_orders.add(order)
                case _ if balance < 0:
                    self.daily_info[self.current_date].market_orders_buy.append(order)
                    self.sell_orders[0].volume -= quantity_to_execute
                case 0:
                    self.sell_orders.pop(0)
                    self.daily_info[self.current_date].market_orders_buy.append(order)
        else:
            if self.buy_orders:
                rate_distance = (
                    self.buy_orders[0].price - order.price
                ) / self.buy_orders[0].price
                self.daily_info[self.current_date].rate_distance.append(rate_distance)
                self.daily_info[self.current_date].bid_rate_distance.append(
                    rate_distance
                )
            self.buy_orders.add(order)

    def execute_ask_order(self, order):
        if self.buy_orders and order.price <= self.buy_orders[0].price:
            quantity_to_execute = min(order.volume, self.buy_orders[0].volume)
            price_to_execute = self.buy_orders[0].price

            # Calculate mid-price
            if self.buy_orders and self.sell_orders:
                mid_price = (self.buy_orders[0].price + self.sell_orders[0].price) / 2
            else:
                mid_price = (
                    price_to_execute  # Fallback if no mid-price can be calculated
                )

            # Calculate Δp
            delta_p = price_to_execute - mid_price
            self.daily_info[self.current_date].delta_p.append(delta_p)

            # Save the market order volume Q
            self.daily_info[self.current_date].market_order_volumes.append(order.volume)

            self.daily_info[self.current_date].executed_orders.append(
                (quantity_to_execute, price_to_execute, order, self.buy_orders[0])
            )
            balance = order.volume - self.buy_orders[0].volume
            match balance:
                case _ if balance > 0:
                    self.buy_orders.pop(0)
                    order.volume -= quantity_to_execute
                    self.sell_orders.add(order)
                case _ if balance < 0:
                    self.daily_info[self.current_date].market_orders_sell.append(order)
                    self.buy_orders[0].volume -= quantity_to_execute
                case 0:
                    self.buy_orders.pop(0)
                    self.daily_info[self.current_date].market_orders_sell.append(order)
        else:
            if self.sell_orders:
                rate_distance = (
                    order.price - self.sell_orders[0].price
                ) / self.sell_orders[0].price
                self.daily_info[self.current_date].rate_distance.append(rate_distance)
                self.daily_info[self.current_date].ask_rate_distance.append(
                    rate_distance
                )
            self.sell_orders.add(order)

    def can_execute(self) -> bool:
        """Check if an execution can occur based on the best buy and sell prices."""
        if self.buy_orders and self.sell_orders:
            return self.buy_orders[0].price >= self.sell_orders[0].price
        return False

    def execute_orders(self, order):
        """Execute orders based on available buy and sell orders."""
        quantity_to_execute = min(self.buy_orders[0].volume, self.sell_orders[0].volume)
        price_to_execute = (
            self.buy_orders[0].price if order.sign == -1 else self.sell_orders[0].price
        )

        self.daily_info[self.current_date].executed_orders.append(
            (
                quantity_to_execute,
                price_to_execute,
                self.buy_orders[0],
                self.sell_orders[0],
            )
        )

        balance = see_first(self.buy_orders).volume - see_first(self.sell_orders).volume

        match balance:
            case _ if balance > 0:
                self.sell_orders.pop(0)
                self.buy_orders[0].volume -= quantity_to_execute
            case _ if balance < 0:
                self.buy_orders.pop(0)
                self.sell_orders[0].volume -= quantity_to_execute
            case 0:
                self.buy_orders.pop(0)
                self.sell_orders.pop(0)

    def advance_time(self, date):
        """Advance the current date and remove old orders."""
        new_date = date
        if self.current_date:
            self.remove_old_orders()

            # Store current day's buy/sell orders
            self.daily_info[self.current_date].limit_orders_buy.extend(
                [order for order in self.buy_orders]
            )
            self.daily_info[self.current_date].limit_orders_sell.extend(
                [order for order in self.sell_orders]
            )
        self.current_date = new_date

    def get_prices(self):
        if self.buy_orders and self.sell_orders:
            self.daily_info[self.current_date].ask_price.append(
                self.sell_orders[0].price
            )
            self.daily_info[self.current_date].bid_price.append(
                self.buy_orders[0].price
            )
            self.daily_info[self.current_date].bid_ask_spread.append(
                self.sell_orders[0].price - self.buy_orders[0].price
            )
            self.daily_info[self.current_date].mid_price.append(
                (self.sell_orders[0].price + self.buy_orders[0].price) / 2
            )

    def remove_old_orders(self):
        cutoff_date = (
            datetime.datetime.strptime(self.current_date, "%Y-%m-%d")
            - datetime.timedelta(days=7)
            if self.current_date
            else None
        )
        cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")

        self.daily_info[self.current_date].old_buy_orders.extend(
            (order for order in self.buy_orders if order.date < cutoff_date_str)
        )
        self.daily_info[self.current_date].old_sell_orders.extend(
            (order for order in self.sell_orders if order.date < cutoff_date_str)
        )

        self.buy_orders = SortedKeyList(
            (order for order in self.buy_orders if order.date >= cutoff_date_str),
            key=lambda x: (-x.price, x.time_stamp),
        )
        self.sell_orders = SortedKeyList(
            (order for order in self.sell_orders if order.date >= cutoff_date_str),
            key=lambda x: (x.price, x.time_stamp),
        )
