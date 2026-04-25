from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Iterable


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


class ValidationError(ValueError):
    """Raised when CLI input or exchange-rule validation fails."""


@dataclass
class ValidatedOrder:
    symbol: str
    side: str
    order_type: str
    quantity: Decimal
    price: Decimal | None = None
    time_in_force: str | None = None


def _to_decimal(value: Any, field_name: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise ValidationError(f"{field_name} must be a valid number.") from exc



def _require_positive(value: Decimal, field_name: str) -> Decimal:
    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than 0.")
    return value



def _get_filter(filters: Iterable[Dict[str, Any]], filter_type: str) -> Dict[str, Any] | None:
    for entry in filters:
        if entry.get("filterType") == filter_type:
            return entry
    return None



def _check_step(value: Decimal, min_value: Decimal, step: Decimal) -> bool:
    if step == 0:
        return True
    normalized = (value - min_value) / step
    return normalized == normalized.to_integral_value()



def validate_basic_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: str | float | None,
) -> ValidatedOrder:
    symbol = symbol.strip().upper()
    side = side.strip().upper()
    order_type = order_type.strip().upper()

    if not symbol:
        raise ValidationError("symbol is required.")
    if side not in VALID_SIDES:
        raise ValidationError(f"side must be one of: {', '.join(sorted(VALID_SIDES))}.")
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"order_type must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )

    qty_decimal = _require_positive(_to_decimal(quantity, "quantity"), "quantity")

    price_decimal: Decimal | None = None
    tif: str | None = None
    if order_type == "LIMIT":
        if price is None:
            raise ValidationError("price is required for LIMIT orders.")
        price_decimal = _require_positive(_to_decimal(price, "price"), "price")
        tif = "GTC"

    if order_type == "MARKET" and price is not None:
        raise ValidationError("price must not be provided for MARKET orders.")

    return ValidatedOrder(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=qty_decimal,
        price=price_decimal,
        time_in_force=tif,
    )



def validate_against_exchange_info(order: ValidatedOrder, exchange_info: Dict[str, Any]) -> None:
    symbols = exchange_info.get("symbols", [])
    symbol_info = next((item for item in symbols if item.get("symbol") == order.symbol), None)

    if symbol_info is None:
        raise ValidationError(f"Symbol '{order.symbol}' is not available on the selected Futures endpoint.")

    if symbol_info.get("status") != "TRADING":
        raise ValidationError(f"Symbol '{order.symbol}' is not tradable right now.")

    filters = symbol_info.get("filters", [])

    qty_filter_type = "MARKET_LOT_SIZE" if order.order_type == "MARKET" else "LOT_SIZE"
    qty_filter = _get_filter(filters, qty_filter_type) or _get_filter(filters, "LOT_SIZE")
    if qty_filter:
        min_qty = Decimal(qty_filter["minQty"])
        max_qty = Decimal(qty_filter["maxQty"])
        step_size = Decimal(qty_filter["stepSize"])
        if order.quantity < min_qty or order.quantity > max_qty:
            raise ValidationError(
                f"quantity must be between {min_qty} and {max_qty} for {order.symbol}."
            )
        if not _check_step(order.quantity, min_qty, step_size):
            raise ValidationError(
                f"quantity must follow step size {step_size} for {order.symbol}."
            )

    if order.order_type == "LIMIT" and order.price is not None:
        price_filter = _get_filter(filters, "PRICE_FILTER")
        if price_filter:
            min_price = Decimal(price_filter["minPrice"])
            max_price = Decimal(price_filter["maxPrice"])
            tick_size = Decimal(price_filter["tickSize"])
            if order.price < min_price or order.price > max_price:
                raise ValidationError(
                    f"price must be between {min_price} and {max_price} for {order.symbol}."
                )
            if not _check_step(order.price, min_price, tick_size):
                raise ValidationError(
                    f"price must follow tick size {tick_size} for {order.symbol}."
                )
