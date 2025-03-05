import datetime
from typing import List

import pandas as pd

# const
from config.const import (
  CURRENCIES,
  DIR_DATA_MESSAGES
)
# framework
from services.scraping.tools import fetcher
from services.scraping.tools import messages
# types
from config.types import MessagesStep


class DataProcessing:
  def __init__(self, end_dates: List[str], currency: CURRENCIES):
    self.end_dates = [
      datetime.datetime.strptime(date, "%Y-%m-%d") for date in end_dates
    ]
    self.currency = currency
    self.messages = pd.DataFrame()
    self.processed_data = []
    self.orders = []
  
  def do_process_messages(self):
    """
    Processes raw messages to generate orders and save all information.

    This method iterates over the end dates and utilizes helper methods to:
    - Fetch raw messages.
    - Convert them into a DataFrame.
    - Interpret and process the messages.
    - Generate formal orders from these messages.
    - Save the collected data into a parquet file.
    """
    for end_date in self.end_dates:
      start_date = end_date - datetime.timedelta(days=1)
      raw_messages = fetcher.fetch_messages(
        currency=self.currency, start_moment=start_date, end_moment=end_date
      )
      self._to_df_raw_messages(raw_messages)
      self.processed_data = [
        messages.interpret(message_str)
        for message_str in self.messages.values[:, 0]
      ]
      self._generate_orders()
      self._save_data_info(end_date)
      yield end_date
  
  def _to_df_raw_messages(self, pure_messages: MessagesStep):
    """
    Converts raw messages into a Pandas DataFrame.

    Args:
        pure_messages (MessagesStep): The raw messages to convert.
    """
    self.messages = pd.DataFrame(
      pure_messages.messages, columns=[pure_messages.end]
    )
  
  def _generate_orders(self):
    """
    Generates formal orders from processed messages.

    This method filters the processed data to generate orders with constraints on size
    and price, ensuring only valid entries are processed into the order list.
    """
    self.orders = [
      {
        "size": int(j[1]) if j[1] != "" else 0,
        "sign": j[0],
        "price": float(j[3]) if j[3] != "" else 0.0,
      }
      for j in self.processed_data
      if isinstance(j, list)
         and len(j) > 0
         and (j[1] != "" and int(j[1]) < 10000)
         and (j[3] != "" and float(j[3]) < 500)
    ]
  
  def _save_data_info(self, date: datetime.datetime):
    """
    Saves all processed information into a Parquet file.

    Args:
        date (datetime.datetime): Day of the information, also used as the filename.

    Note:
        The parquet file is named by the date and stored in the directory fetched from
        the `get_data_messages_directory` function.
    """
    date_str = date.strftime("%Y-%m-%d")
    
    processed_data_normalized = [
      item if isinstance(item, list) else [] for item in self.processed_data
    ]
    
    combined_df = pd.DataFrame(
      [self.messages.values.tolist(), processed_data_normalized, self.orders]
    ).T
    combined_df.rename(
      columns={0: "messages", 1: "processed_messages", 2: "orders"}, inplace=True
    )
    
    combined_df.to_parquet(
      f"{DIR_DATA_MESSAGES}/{date_str}.parquet", index=False, engine="pyarrow"
    )
