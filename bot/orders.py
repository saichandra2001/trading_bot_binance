from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from .client import BinanceFuturesClient
from .validators import ValidatedOrder, validate_against_exchange_info


def decimal_to_str(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value.normalize(), "f")



def build_order_payload(order: ValidatedOrder) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "symbol": order.symbol,
        "side": order.side,
        "type": order.order_type,
        "quantity": decimal_to_str(order.quantity),
    }

    if order.order_type == "LIMIT":
        payload["price"] = decimal_to_str(order.price)
        payload["timeInForce"] = order.time_in_force or "GTC"

    return payload



def place_validated_order(client: BinanceFuturesClient, order: ValidatedOrder) -> Dict[str, Any]:
    exchange_info = client.get_exchange_info()
    validate_against_exchange_info(order, exchange_info)
    payload = build_order_payload(order)
    return client.place_order(payload)



def summarize_order_response(response: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "orderId": response.get("orderId"),
        "symbol": response.get("symbol"),
        "status": response.get("status"),
        "side": response.get("side"),
        "type": response.get("type"),
        "origQty": response.get("origQty"),
        "executedQty": response.get("executedQty"),
        "price": response.get("price"),
        "avgPrice": response.get("avgPrice"),
        "clientOrderId": response.get("clientOrderId"),
        "updateTime": response.get("updateTime"),
    }
