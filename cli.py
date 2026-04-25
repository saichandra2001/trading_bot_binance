from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from dotenv import load_dotenv

from bot.client import BinanceAPIError, BinanceFuturesClient, BinanceRequestError
from bot.logging_config import setup_logging
from bot.orders import place_validated_order, summarize_order_response
from bot.validators import ValidationError, validate_basic_inputs


DEFAULT_BASE_URL = "https://testnet.binancefuture.com"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place Binance USDⓈ-M Futures Testnet orders from the command line.",
    )
    parser.add_argument("--symbol", required=True, help="Trading symbol, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL"], help="Order side")
    parser.add_argument(
        "--order-type",
        required=True,
        choices=["MARKET", "LIMIT"],
        help="Order type",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity, e.g. 0.001")
    parser.add_argument("--price", help="Limit price. Required for LIMIT orders.")
    parser.add_argument(
        "--base-url",
        default=os.getenv("BINANCE_BASE_URL", DEFAULT_BASE_URL),
        help="Binance Futures base URL (default: env BINANCE_BASE_URL or assignment URL)",
    )
    parser.add_argument(
        "--log-file",
        default="logs/trading_bot.log",
        help="Path to the log file.",
    )
    return parser



def print_summary(title: str, data: dict[str, Any]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    for key, value in data.items():
        print(f"{key}: {value}")



def main() -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    logger = setup_logging(args.log_file)

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        print("Error: BINANCE_API_KEY and BINANCE_API_SECRET must be set in your environment or .env file.")
        return 1

    try:
        order = validate_basic_inputs(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )

        client = BinanceFuturesClient(
            api_key=api_key,
            api_secret=api_secret,
            base_url=args.base_url,
            logger=logger,
        )

        request_summary = {
            "symbol": order.symbol,
            "side": order.side,
            "order_type": order.order_type,
            "quantity": str(order.quantity),
            "price": str(order.price) if order.price is not None else "N/A",
            "base_url": args.base_url,
        }
        print_summary("Order Request Summary", request_summary)

        response = place_validated_order(client, order)
        result = summarize_order_response(response)
        print_summary("Order Response Details", result)
        print("\nSuccess: order placed successfully on Binance Futures Testnet.")
        return 0

    except ValidationError as exc:
        logger.error("Validation error: %s", exc)
        print(f"Validation Error: {exc}")
        return 2
    except BinanceAPIError as exc:
        logger.error("Binance API error: %s", exc)
        print(f"API Error: {exc}")
        return 3
    except BinanceRequestError as exc:
        logger.error("Request error: %s", exc)
        print(f"Request Error: {exc}")
        return 4
    except Exception as exc:  # pragma: no cover
        logger.exception("Unexpected error")
        print(f"Unexpected Error: {exc}")
        return 99


if __name__ == "__main__":
    sys.exit(main())
