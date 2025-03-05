import json
import os
import pickle
from typing import Literal
import logging
from datetime import datetime

# conf logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

from services.analytics.data_analytics import DataAnalytics
from services.limit_order_book.limit_order_book import LimitOrderBook
from services.limit_order_book.tools.data_loader import load_orders
from config.const import DIR_DATA_MESSAGES, DIR_DATA_ANALYTICS, CURRENCIES
from services.scraping.data_processing import DataProcessing
from services.scraping.tools.missing_dates import get_missing_dates
from tools.const import DIR_DATA, PATH_ORDERS
from tools.helpers import timing_decorator


DAILY_INFO_PICKLE_PATH = os.path.join(DIR_DATA_ANALYTICS, "daily_info.pickle")
os.makedirs(DIR_DATA_ANALYTICS, exist_ok=True)


def process_missing_dates(currency: Literal["USD", "EUR"] = "USD") -> None:
    """Procesa las fechas faltantes detectadas en los datos."""
    reporter_dates = get_missing_dates(DIR_DATA_MESSAGES)
    missing_dates = [day for (day, is_in) in reporter_dates.dates if not is_in]

    if not missing_dates:
        logging.info("No hay fechas faltantes para procesar")
        return

    logging.info(f"Procesando {len(missing_dates)} fechas faltantes")
    data_processor = DataProcessing(end_dates=missing_dates, currency=currency)

    for i, processed_date in enumerate(data_processor.do_process_messages(), 1):
        logging.info(
            f"Procesada fecha: {processed_date.strftime('%Y-%m-%d')} ({i}/{len(missing_dates)})"
        )


def run_analytics() -> None:
    """Ejecuta el análisis de datos y guarda los resultados."""
    analytics = DataAnalytics(DIR_DATA_MESSAGES)
    analytics.do_analytics()

    # Guardar resultados
    analytics_path = os.path.join(DIR_DATA_ANALYTICS, "analytics.pickle")
    orders_path = os.path.join(DIR_DATA_ANALYTICS, "all_orders.json")

    analytics.dataframe.to_pickle(analytics_path)
    with open(orders_path, "w") as f:
        json.dump(analytics.orders, f, indent=2)

    logging.info(f"Análisis guardado en {analytics_path} y {orders_path}")


@timing_decorator
def process_orders(lob: LimitOrderBook, orders: list) -> None:
    """Procesa órdenes en el libro con manejo de errores."""
    try:
        lob.add_orders_daily(orders)
        logging.info(f"Procesadas {len(orders)} órdenes correctamente")
    except Exception as e:
        logging.error("Error procesando órdenes", exc_info=True)
        raise


def save_lob_data(daily_info: dict, output_dir: str) -> None:
    """Guarda datos del libro de órdenes con formato serializable."""
    try:
        serialized_data = {
            date: {
                k: v
                for k, v in info.__dict__.items()
                if not k.startswith("_") and not callable(k)
            }
            for date, info in daily_info.items()
        }

        file_path = os.path.join(output_dir, "lob_data.pickle")
        with open(file_path, "wb") as f:
            pickle.dump(serialized_data, f, protocol=pickle.HIGHEST_PROTOCOL)

        logging.info(f"Datos LOB guardados en: {file_path}")
    except Exception as e:
        logging.error("Error guardando datos LOB", exc_info=True)
        raise


def main(currency: Literal["USD", "EUR"] = "USD") -> None:
    try:
        # Flujo principal
        process_missing_dates(currency)
        run_analytics()

        # Checkeo de ordenes
        if not os.path.exists(PATH_ORDERS):
            logging.error(f"Archivo no encontrado: {PATH_ORDERS}")
            return

        orders = load_orders(PATH_ORDERS)
        if not orders:
            logging.warning("No hay órdenes para procesar")
            return

        logging.info(f"Cargadas {len(orders)} órdenes desde {PATH_ORDERS}")

        # Procesamiento de LOB
        lob = LimitOrderBook()
        process_orders(lob, orders)
        save_lob_data(lob.daily_info, DIR_DATA_ANALYTICS)

    except KeyboardInterrupt:
        logging.warning("Ejecución interrumpida por usuario")
    except Exception as e:
        logging.error("Error crítico en ejecución", exc_info=True)
    finally:
        logging.info("Proceso finalizado")


if __name__ == "__main__":
    selected_currency = os.getenv("CURRENCY", "USD")
    main(currency=selected_currency)
