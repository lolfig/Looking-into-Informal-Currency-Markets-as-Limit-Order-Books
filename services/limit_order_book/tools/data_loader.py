import json
from typing import List
from .types import Order


def load_orders(file_path: str) -> List[Order]:
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading file {file_path}: {e}")
        return []

    sorted_data = {key: data[key] for key in sorted(data.keys())}

    all_orders = []

    counter = 1

    for date_str, orders in sorted_data.items():
        for order in orders:
            if order["volume"] > 0:
                all_orders.append(
                    Order(
                        sign=1 if order["sign"] == "compro" else -1,
                        price=order["price"],
                        volume=order["volume"],
                        time_stamp=counter,
                        date=date_str,
                    )
                )
                counter += 1

    return all_orders
