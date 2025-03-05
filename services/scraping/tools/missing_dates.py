import os
from datetime import datetime, timedelta
from typing import List

from services.formaters import datetime_to_str
# frameworks
from config.const import EL_TOQUE_FIRST_DAY
from config.types import ReporterDates


def get_missing_dates(data_dir: str) -> ReporterDates:
  start_datetime = datetime.strptime(EL_TOQUE_FIRST_DAY, "%Y-%m-%d")
  end_datetime = datetime.now() - timedelta(days=1)
  assert start_datetime < end_datetime, "Start date must be less than end date"
  
  all_dates: List[str] = [
    datetime_to_str(
      start_datetime + timedelta(days=i)
    )
    for i in range(
      0,  # include first day
      (end_datetime - start_datetime).days + 1  # include last day
    )
  ]
  
  existing_dates = load_day_files(data_dir)
  
  return ReporterDates(
    dates=[(date, date in existing_dates) for date in all_dates],
    start_date=datetime_to_str(start_datetime),
    end_date=datetime_to_str(end_datetime)
  )


def load_day_files(data_dir):
  existing_dates = {
    file[:-len(parquet_postfix)]  # sub_string without ".parquet" postfix
    for file
    in os.listdir(data_dir)
    if file.endswith(parquet_postfix := ".parquet")
  }
  return existing_dates
