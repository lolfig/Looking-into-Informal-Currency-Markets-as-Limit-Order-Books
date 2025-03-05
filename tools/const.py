from operator import __getitem__
import os

DIR_DATA = os.path.join(os.getcwd(), "data")

# PATH_ORDERS = "/home/figal/Projects/cuba_fx_market/data/analytics/all_orders.json"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATH_ORDERS = os.path.join(BASE_DIR, "data", "analytics", "all_orders.json")


def see_first(collection: {__getitem__}):
    return collection[0]
