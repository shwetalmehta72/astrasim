from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

from app.core.config import Settings, get_settings

ChainKey = Tuple[str, str]

_last_chain_refresh: Dict[ChainKey, datetime] = {}
_last_atm_refresh: Dict[str, Tuple[datetime, Optional[float]]] = {}
_last_surface_refresh: Dict[str, datetime] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _symbol(symbol: str) -> str:
    return symbol.upper()


def should_refresh_chain(
    symbol: str,
    expiration: str,
    *,
    settings: Optional[Settings] = None,
    force: bool = False,
) -> bool:
    if force:
        return True
    settings = settings or get_settings()
    key = (_symbol(symbol), expiration)
    last = _last_chain_refresh.get(key)
    if last is None:
        return True
    return (_now() - last).total_seconds() >= settings.OPTIONS_CACHE_TTL_CHAIN


def record_chain_refresh(symbol: str, expiration: str) -> None:
    key = (_symbol(symbol), expiration)
    _last_chain_refresh[key] = _now()


def should_refresh_atm(
    symbol: str,
    underlying_price: Optional[float],
    *,
    settings: Optional[Settings] = None,
    force: bool = False,
) -> bool:
    if force:
        return True
    settings = settings or get_settings()
    entry = _last_atm_refresh.get(_symbol(symbol))
    now = _now()
    if entry is None:
        return True
    last_time, last_underlying = entry
    if (now - last_time).total_seconds() >= settings.ATM_REFRESH_INTERVAL:
        return True
    if (
        underlying_price
        and last_underlying
        and last_underlying > 0
        and abs(underlying_price - last_underlying) / last_underlying >= settings.MIN_UNDERLYING_MOVE
    ):
        return True
    return False


def record_atm_refresh(symbol: str, underlying_price: Optional[float]) -> None:
    _last_atm_refresh[_symbol(symbol)] = (_now(), underlying_price)


def should_refresh_surface(
    symbol: str,
    *,
    settings: Optional[Settings] = None,
    force: bool = False,
) -> bool:
    if force:
        return True
    settings = settings or get_settings()
    last = _last_surface_refresh.get(_symbol(symbol))
    if last is None:
        return True
    return (_now() - last).total_seconds() >= settings.SURFACE_REFRESH_INTERVAL


def record_surface_refresh(symbol: str) -> None:
    _last_surface_refresh[_symbol(symbol)] = _now()

