import time
from functools import wraps
import matplotlib.dates as mpl_dates
import pandas as pd


def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Executions time: {func.__name__}: {end_time - start_time:.4f} seconds")
        return result

    return wrapper


def create_ohlc_dataframe(lob_data):

    dates = []
    prices = []

    for date, info in lob_data.items():
        dates.extend([date] * len(info.executed_orders))
        prices.extend([q[1] for q in info.executed_orders])

    df = pd.DataFrame({"date": dates, "prices": prices})
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)

    open_price = df.groupby(df.index.date).first()
    high_price = df.groupby(df.index.date).max()
    low_price = df.groupby(df.index.date).min()
    close_price = df.groupby(df.index.date).last()

    df = pd.DataFrame(
        {
            "Open": open_price["prices"].values,
            "High": high_price["prices"].values,
            "Low": low_price["prices"].values,
            "Close": close_price["prices"].values,
        },
        index=pd.to_datetime(open_price.index),
    )

    ohlc = df.loc[:, ["Open", "High", "Low", "Close"]]
    ohlc.reset_index(
        inplace=True,
    )
    ohlc.rename(columns={"index": "Date"}, inplace=True)
    ohlc["Date"] = ohlc["Date"].apply(mpl_dates.date2num)
    ohlc = ohlc.astype(float)

    return ohlc


def get_close_price(data_dict, start_date, end_date):
    dates = []
    prices = []
    for date, info in data_dict.items():
        if start_date <= date <= end_date:
            dates.extend([date] * len(info.executed_orders))
            prices.extend([q[1] for q in info.executed_orders])
    df = pd.DataFrame({"date": dates, "prices": prices})
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    df = df.groupby(df.index.date).last()
    return df


def extract_bid_ask_spread(data_dict, start_date, end_date, flag):
    dates = []
    spreads = []
    for date, info in data_dict.items():
        if start_date <= date <= end_date:
            dates.extend([date] * len(info.bid_ask_spread))
            spreads.extend(info.bid_ask_spread)
    df = pd.DataFrame({"date": dates, "bid_ask_spread": spreads})
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    if flag:
        df = df["bid_ask_spread"].groupby(df.index).mean()
        return df
    else:
        return df


def get_executed_volume(data_dict, start_date, end_date, flag):
    dates = []
    executed_vol = []
    for date, info in data_dict.items():
        if start_date <= date <= end_date:
            dates.extend([date] * len(info.executed_orders))
            executed_vol.extend([q[0] for q in info.executed_orders])
    df = pd.DataFrame({"date": dates, "executed_vol": executed_vol})
    df.set_index("date", inplace=True)
    df.index = pd.to_datetime(df.index)
    if flag:
        df = df["executed_vol"].groupby(df.index).mean()
        return df
    else:
        return df
