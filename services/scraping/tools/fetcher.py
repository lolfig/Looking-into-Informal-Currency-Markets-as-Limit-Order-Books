# build-in
import datetime

# packages
import requests

# framework
from config import const, types
from services import formaters


def fetch_messages(currency: str, start_moment: datetime.datetime, end_moment: datetime.datetime) -> types.MessagesStep:
    """
    Downloads raw offer messages from the TOQUE website based on a specified currency and date range.

    Args:
        currency (str): The currency for which messages are to be downloaded.
        start_moment (datetime.datetime): The start date for fetching messages (inclusive).
        end_moment (datetime.datetime): The end date for fetching messages (inclusive).

    Returns:
        MessagesStep: A dataclass containing the raw messages fetched.
    
    Raises:
        HTTPError: If the HTTP request fails.
        Exception: For any other errors during the fetching process.
    """
    start_str, end_str = formaters.datetime_to_str(start_moment), formaters.datetime_to_str(end_moment)


    print(f"Fetching data for {end_str}")
    try:
        response = requests.get(
            f"{const.SOURCE_URL}?" + "&".join(
                [
                    f"token={const.ACCESS_TOKEN}",
                    f"date_from={start_str}%2000:00:00",
                    f"date_to={end_str}%2000:00:00"
                ]
            )
        )
        response.raise_for_status()
        messages = response.json()["statistics"][currency]["messages"]

        return types.MessagesStep(
            end=end_str,
            start=start_str,
            messages=messages
        )
    except requests.exceptions.HTTPError as error:
        print(f"HTTP error occurred: {error}")
    except Exception as error:
        print(f"An error occurred: {error}")


def fetch_exchange_rate_data(api_url: str):
    """
    Downloads exchange rate data from the specified API URL.

    Args:
        api_url (str): The API endpoint for fetching exchange rate data.

    Raises:
        ValueError: If the API response is empty or invalid.

    Returns:
        Dict[str, Any]: A dictionary containing the exchange rate data.
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise ValueError("API response is empty")
        return data
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Error fetching exchange rate data: {e}")
        return None
