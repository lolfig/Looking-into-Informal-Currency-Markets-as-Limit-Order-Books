import datetime
import os
from typing import Literal

today = datetime.datetime.now().date()
yesterday = today - datetime.timedelta(days=1)

CURRENCIES = Literal['USD', 'EUR']

DIR_DATA_ANALYTICS = os.path.join(os.getcwd(), "data", "analytics")
DIR_DATA_MESSAGES = os.path.join(os.getcwd(), "data", "messages")


ACCESS_TOKEN = "aCY78gC3kWRv1pR7VfgSlg"
SOURCE_URL = "https://api.cambiocuba.money/api/v1/x-rates"
EL_TOQUE_FIRST_DAY = "2021-07-23"
