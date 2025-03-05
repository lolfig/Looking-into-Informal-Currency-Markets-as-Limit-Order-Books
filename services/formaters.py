from datetime import datetime



def from_string(selected_date: str):
  return datetime.strptime(selected_date, "%Y-%m-%d")


def datetime_to_str(date: datetime) -> str:
  return date.strftime("%Y-%m-%d")
