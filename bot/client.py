from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests


class BinanceAPIError(Exception):
    """Raised for Binance API-level errors."""


class BinanceRequestError(Exception):
    """Raised for connectivity or malformed response issues."""


class BinanceFuturesClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str,
        timeout: int = 15,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        if not api_key or not api_secret:
            raise ValueError("API key and API secret are required.")

        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.logger = logger or logging.getLogger("trading_bot")
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _sign(self, params: Dict[str, Any]) -> str:
        query_string = urlencode(params, doseq=True)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        params = params.copy() if params else {}
        url = f"{self.base_url}{path}"

        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params.setdefault("recvWindow", 5000)
            params["signature"] = self._sign(params)

        safe_params = {k: v for k, v in params.items() if k != "signature"}
        self.logger.info("API request | method=%s url=%s params=%s", method, url, safe_params)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            self.logger.exception("Network error during Binance request")
            raise BinanceRequestError(f"Network error while calling Binance API: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            self.logger.exception("Non-JSON response received from Binance")
            raise BinanceRequestError(
                f"Received non-JSON response from Binance (status code {response.status_code})."
            ) from exc

        self.logger.info(
            "API response | status_code=%s body=%s",
            response.status_code,
            data,
        )

        if response.status_code >= 400:
            message = data.get("msg", "Unknown Binance API error") if isinstance(data, dict) else str(data)
            code = data.get("code") if isinstance(data, dict) else None
            raise BinanceAPIError(f"Binance API error {code}: {message}")

        if not isinstance(data, dict):
            raise BinanceRequestError("Unexpected Binance response format.")

        return data

    def ping(self) -> Dict[str, Any]:
        return self._request("GET", "/fapi/v1/ping")

    def get_exchange_info(self) -> Dict[str, Any]:
        return self._request("GET", "/fapi/v1/exchangeInfo")

    def place_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/fapi/v1/order", params=payload, signed=True)
