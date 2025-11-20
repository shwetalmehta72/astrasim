from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from app.core.config import Settings, get_settings


@dataclass
class CachedValue:
    value: Any
    metadata: Dict[str, Any]


@dataclass
class _CacheEntry:
    value: Any
    metadata: Dict[str, Any]
    expires_at: datetime


_chain_cache: Dict[Tuple[str, str], _CacheEntry] = {}
_atm_cache: Dict[str, _CacheEntry] = {}
_surface_cache: Dict[str, _CacheEntry] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _is_expired(entry: _CacheEntry) -> bool:
    return entry.expires_at <= _now()


def _ttl(seconds: int) -> timedelta:
    return timedelta(seconds=max(seconds, 0))


def _make_key(symbol: str, suffix: str) -> Tuple[str, str]:
    return (symbol.upper(), suffix)


def get_cached_chain(symbol: str, expiration: str, *, settings: Optional[Settings] = None) -> Optional[CachedValue]:
    key = _make_key(symbol, expiration)
    entry = _chain_cache.get(key)
    if not entry or _is_expired(entry):
        _chain_cache.pop(key, None)
        return None
    return CachedValue(entry.value, entry.metadata)


def set_cached_chain(
    symbol: str,
    expiration: str,
    value: Any,
    metadata: Optional[Dict[str, Any]] = None,
    *,
    settings: Optional[Settings] = None,
) -> None:
    settings = settings or get_settings()
    expires_at = _now() + _ttl(settings.OPTIONS_CACHE_TTL_CHAIN)
    key = _make_key(symbol, expiration)
    _chain_cache[key] = _CacheEntry(value=value, metadata=metadata or {}, expires_at=expires_at)


def get_cached_atm(symbol: str, *, settings: Optional[Settings] = None) -> Optional[CachedValue]:
    entry = _atm_cache.get(symbol.upper())
    if not entry or _is_expired(entry):
        _atm_cache.pop(symbol.upper(), None)
        return None
    return CachedValue(entry.value, entry.metadata)


def set_cached_atm(
    symbol: str,
    value: Any,
    metadata: Optional[Dict[str, Any]] = None,
    *,
    settings: Optional[Settings] = None,
) -> None:
    settings = settings or get_settings()
    expires_at = _now() + _ttl(settings.OPTIONS_CACHE_TTL_ATM)
    _atm_cache[symbol.upper()] = _CacheEntry(value=value, metadata=metadata or {}, expires_at=expires_at)


def get_cached_surface(symbol: str, *, settings: Optional[Settings] = None) -> Optional[CachedValue]:
    entry = _surface_cache.get(symbol.upper())
    if not entry or _is_expired(entry):
        _surface_cache.pop(symbol.upper(), None)
        return None
    return CachedValue(entry.value, entry.metadata)


def set_cached_surface(
    symbol: str,
    value: Any,
    metadata: Optional[Dict[str, Any]] = None,
    *,
    settings: Optional[Settings] = None,
) -> None:
    settings = settings or get_settings()
    expires_at = _now() + _ttl(settings.OPTIONS_CACHE_TTL_SURFACE)
    _surface_cache[symbol.upper()] = _CacheEntry(value=value, metadata=metadata or {}, expires_at=expires_at)


def invalidate_symbol(symbol: str) -> None:
    symbol_upper = symbol.upper()
    _atm_cache.pop(symbol_upper, None)
    _surface_cache.pop(symbol_upper, None)
    keys = [key for key in _chain_cache if key[0] == symbol_upper]
    for key in keys:
        _chain_cache.pop(key, None)


def invalidate_all() -> None:
    _atm_cache.clear()
    _surface_cache.clear()
    _chain_cache.clear()

