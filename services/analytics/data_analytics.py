import glob
import numpy as np
import pandas as pd

from services.analytics.tools.analytics_utils import find_marginal_price


class DataAnalytics:
    def __init__(self, path):
        self.path = path
        self.dataframe = pd.DataFrame()
        self.orders = {}

    def do_analytics(self):
        """
        Performs framework_analytics on processed messages and formal orders.

        This method reads all parquet files from the specified path,
        processes each file to extract relevant framework_analytics, and
        compiles the results into a single DataFrame.
        """
        all_files = glob.glob(self.path + "/*.parquet")

        for file in all_files:
            date = file[-18:-8]
            df = pd.read_parquet(file)
            intraday_data = self._do_intra_day_analytics(df, date)
            self.dataframe = pd.concat([self.dataframe, intraday_data])

        self.dataframe.sort_index(inplace=True)
        self.dataframe.index = pd.to_datetime(self.dataframe.index)

    def _do_intra_day_analytics(self, df, date):
        """
        Analyzes intraday data to calculate stylized facts.

        Args:
            df (pd.DataFrame): DataFrame containing processed messages and orders.
            date (str): The date corresponding to the data being analyzed.

        Returns:
            pd.DataFrame: A DataFrame containing calculated stylized facts for the day.
        """
        compra_df, venta_df, all_orders = self._extract_orders(df)
        self.orders[date] = all_orders

        # Calculate volume and price levels
        nivel_volumen_compra, nivel_precio_compra = self._calculate_levels(compra_df)
        nivel_volumen_venta, nivel_precio_venta = self._calculate_levels(
            venta_df, is_sell=True
        )

        price, vol = find_marginal_price(
            nivel_precio_compra,
            nivel_volumen_compra,
            nivel_precio_venta,
            nivel_volumen_venta,
        )
        marginal_data = [{"price_mar": price, "vol_mar": vol}]

        # Group orders for histogram plot
        grouped_buy = self._group_orders(compra_df)
        grouped_sell = self._group_orders(venta_df)

        analytics = {
            "Compras_ordenadas": grouped_buy[grouped_buy >= 500],
            "Ventas_ordenadas": grouped_sell[grouped_sell >= 500],
            "Nivel_volumen_compra": nivel_volumen_compra,
            "Nivel_precio_compra": nivel_precio_compra,
            "Nivel_volumen_venta": nivel_volumen_venta,
            "Nivel_precio_venta": nivel_precio_venta,
            "Marginal_Data": marginal_data,
            "Volumen_Compra": sum(compra_df["vol_compra"]),
            "Volumen_Venta": sum(venta_df["vol_venta"]),
            "Volumen_Total": sum(compra_df["vol_compra"]) + sum(venta_df["vol_venta"]),
            "Cantidad_Compra": compra_df["vol_compra"].tolist(),
            "Cantidad_Venta": venta_df["vol_venta"].tolist(),
            "Precio_Compra": compra_df["precio_compra"].tolist(),
            "Precio_Venta": venta_df["precio_venta"].tolist(),
        }

        return pd.DataFrame([analytics], index=[date])

    def _extract_orders(self, df):
        """
        Extracts buy and sell orders from the DataFrame.

        Args:
            df (pd.DataFrame): DataFrame containing formal orders.

        Returns:
            tuple: Two DataFrames containing buy and sell orders respectively.
        """

        buy_orders = [
            {"vol_compra": order["size"], "precio_compra": order["price"]}
            for order in df["orders"]
            if order and order["sign"] == "compro"
        ]
        sell_orders = [
            {"vol_venta": order["size"], "precio_venta": order["price"]}
            for order in df["orders"]
            if order and order["sign"] == "vendo"
        ]
        all_orders = [
            {"sign": order["sign"], "price": order["price"], "volume": order["size"]}
            for order in df["orders"]
            if order and 45 < order["price"] < 500 and 0 <= order["size"] < 50000
        ]

        return pd.DataFrame(buy_orders), pd.DataFrame(sell_orders), all_orders

    def _calculate_levels(self, orders_df, is_sell=False):
        """
        Calculates cumulative volume and price levels from orders.

        Args:
            orders_df (pd.DataFrame): DataFrame containing formal orders.
            is_sell (bool): Indicates whether to process sell orders. Defaults to False.

        Returns:
            tuple: Two numpy arrays representing cumulative volume and price levels.
        """
        if is_sell:
            orders_df.sort_values(by="precio_venta", inplace=True)
        else:
            orders_df.sort_values(by="precio_compra", ascending=False, inplace=True)

        volumen_nivel = np.array(
            orders_df["vol_compra" if not is_sell else "vol_venta"].cumsum()
        )
        precio_nivel = np.array(orders_df[orders_df.columns[1]].tolist())

        return volumen_nivel, precio_nivel

    def _group_orders(self, orders_df):
        """
        Groups orders by price levels.

        Args:
            orders_df (pd.DataFrame): DataFrame containing formal orders.

        Returns:
            pd.Series: Series with grouped order volumes by price.
        """
        return (
            orders_df.apply(lambda x: 5 * round(x / 5.0))
            .groupby(orders_df.columns[1])[  # Agrupar por precio
                "vol_compra" if "compra" in orders_df.columns[1] else "vol_venta"
            ]
            .sum()
            .replace(0, np.nan)
            .dropna()
        )
