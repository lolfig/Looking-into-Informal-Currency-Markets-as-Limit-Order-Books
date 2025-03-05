# Looking into Informal Currency Markets as Limit Order Books

## Project Overview

This project analyzes cuban informal currency market by modeling them as limit order books (LOBs). It processes financial messages, extracts structured data, simulates an order book, and applies analytical techniques to understand market microstructure dynamics.

## Features

- **Data Processing:** Extracts and processes historical financial messages.
- **Limit Order Book Simulation:** Implements a LOB model to track bid-ask prices and order execution.
- **Market Analytics:** Performs data analysis to identify market trends and liquidity properties.
- **Missing Data Handling:** Detects and processes missing data points.

## Project Structure

```
.
├── config/               # Configuration files and constants
├── data/                 # Raw and processed data storage
├── notebooks/            # Jupyter notebooks for exploratory analysis
├── services/             # Core services
│   ├── analytics/        # Data analytics module
│   ├── limit_order_book/ # Limit order book implementation
│   ├── scraping/         # Web scraping and data collection
├── tools/                # Utility scripts and helper functions
├── main.py               # Main execution script
├── requirements.txt      # Required Python packages
├── environment.yml       # Conda environment configuration
```

## Installation

### Prerequisites

Ensure you have Python 3.12.9 installed.

### Virtual Environment Setup

Using Conda:

```sh
conda create --name lob_env python=3.12.9
conda activate lob_env
conda env update --file environment.yml
```

Using venv:

```sh
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
pip install -r requirements.txt
```

## Usage

Run the main script:

```sh
python main.py
```

You can set the currency environment variable before execution:

```sh
export CURRENCY=EUR  # For Linux/macOS
set CURRENCY=EUR     # For Windows
python main.py
```

## Main Functions

- `process_missing_dates(currency: Literal["USD", "EUR"])`: Handles missing dates in the dataset.
- `run_analytics()`: Executes data analysis and stores results.
- `process_orders(lob: LimitOrderBook, orders: list)`: Processes orders and updates the order book.
- `save_lob_data(daily_info: dict, output_dir: str)`: Serializes and saves the limit order book data.
- `main(currency: Literal["USD", "EUR"])`: Runs the complete data processing and analysis workflow.

## Dependencies

The project requires the following Python packages (see `requirements.txt` for details):

- `numpy`, `pandas`, `scipy` for data analysis
- `matplotlib`, `scienceplots` for visualization
- `pyarrow` for data storage
- `requests` for web scraping

## Contributing

Feel free to contribute by improving the data processing pipeline, adding new analytics, or refining the limit order book model.

## License

This project is open-source under the MIT License.

