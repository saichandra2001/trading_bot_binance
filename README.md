# Binance Futures Testnet Trading Bot

A small Python CLI application that places **MARKET** and **LIMIT** orders on **Binance USDⓈ-M Futures Testnet** with validation, logging, and structured code.

## Features

- Place **MARKET** and **LIMIT** orders
- Supports both **BUY** and **SELL**
- CLI input via `argparse`
- Input validation before request submission
- Exchange-rule validation using Binance `exchangeInfo`
- Structured logging of requests, responses, and errors
- Clean separation of concerns:
  - `client.py` → API wrapper
  - `orders.py` → order payload + orchestration
  - `validators.py` → input and exchange validation
  - `logging_config.py` → logger setup
  - `cli.py` → command-line entry point

## Project Structure

```text
trading_bot/
  bot/
    __init__.py
    client.py
    orders.py
    validators.py
    logging_config.py
  logs/
    market_order_example.log
    limit_order_example.log
  cli.py
  .env.example
  README.md
  requirements.txt
```

## Requirements

- Python 3.10+ recommended
- Binance Futures Testnet account
- Testnet API key and secret

## Setup

### 1) Clone or unzip the project

```bash
git clone <your-repo-url>
cd trading_bot
```

### 2) Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure environment variables

Copy `.env.example` to `.env` and add your Binance Futures Testnet credentials.

**Windows (PowerShell):**
```powershell
copy .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

Then update:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
BINANCE_BASE_URL=https://testnet.binancefuture.com
```

## How to Run

### Example 1: MARKET BUY order

```bash
python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001 --log-file logs/market_order.log
```

### Example 2: MARKET SELL order

```bash
python cli.py --symbol BTCUSDT --side SELL --order-type MARKET --quantity 0.001 --log-file logs/market_sell_order.log
```

### Example 3: LIMIT BUY order

```bash
python cli.py --symbol BTCUSDT --side BUY --order-type LIMIT --quantity 0.001 --price 50000 --log-file logs/limit_order.log
```

### Example 4: LIMIT SELL order

```bash
python cli.py --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 90000 --log-file logs/limit_sell_order.log
```

## Example Console Output

```text
Order Request Summary
---------------------
symbol: BTCUSDT
side: BUY
order_type: MARKET
quantity: 0.001
price: N/A
base_url: https://testnet.binancefuture.com

Order Response Details
----------------------
orderId: 123456789
symbol: BTCUSDT
status: FILLED
side: BUY
type: MARKET
origQty: 0.001
executedQty: 0.001
price: 0
avgPrice: 64321.50
clientOrderId: x-test-order-001
updateTime: 1713720000000

Success: order placed successfully on Binance Futures Testnet.
```

## Logging

Logs are written to the file you pass through `--log-file`.

Each log captures:
- API request metadata
- API response payload
- validation errors
- network/API exceptions

Two sample log files are included:
- `logs/market_order_example.log`
- `logs/limit_order_example.log`

> Before final submission, replace or supplement these with logs generated from your own successful MARKET and LIMIT orders using your testnet account.

## Validation Rules Implemented

### Basic CLI validation
- `symbol` required
- `side` must be `BUY` or `SELL`
- `order_type` must be `MARKET` or `LIMIT`
- `quantity` must be numeric and greater than 0
- `price` is required for `LIMIT`
- `price` is rejected for `MARKET`

### Exchange validation
The application calls Binance `exchangeInfo` and validates:
- symbol exists and is tradable
- quantity range and step size
- price range and tick size for LIMIT orders

## Assumptions

1. The assignment specifies `https://testnet.binancefuture.com` as the base URL, so this project uses that as the default.
2. Binance’s current USDⓈ-M futures documentation also lists `https://demo-fapi.binance.com` for REST testnet in some official docs. For compatibility, the base URL is configurable via `--base-url` or `BINANCE_BASE_URL`.
3. This project uses **direct REST calls** with `requests` instead of `python-binance` to keep the code lightweight and explicit.
4. For LIMIT orders, `timeInForce=GTC` is used by default.
5. Average price may be unavailable for newly accepted LIMIT orders until they are partially or fully executed.

## Notes for Reviewers

- Secrets are loaded from environment variables and are not hardcoded.
- Request signing is handled via HMAC SHA256.
- Signature values are not written to logs.
- Errors are surfaced clearly in both CLI output and log files.

## Possible Future Improvements

- Add stop-limit order support
- Add `cancel order` command
- Add richer CLI using `Typer`
- Add unit tests

## Submission Checklist

- [ ] Add your real Binance Testnet API credentials in `.env`
- [ ] Run one successful MARKET order and keep the generated log file
- [ ] Run one successful LIMIT order and keep the generated log file
- [ ] Push to a public GitHub repository or zip the folder
- [ ] Submit through the Google Form mentioned in the task
