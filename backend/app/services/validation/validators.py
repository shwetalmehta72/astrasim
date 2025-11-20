from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Sequence


def _issue(security_id: int, issue_type: str, severity: str, issue_timestamp: datetime, details: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "security_id": security_id,
        "issue_type": issue_type,
        "severity": severity,
        "issue_timestamp": issue_timestamp,
        "details": details,
    }


def validate_missing_timestamps(
    security_id: int,
    rows: Sequence[Dict[str, Any]],
    *,
    expected_interval: timedelta,
) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    if not rows:
        return issues

    sorted_rows = sorted(rows, key=lambda r: r["time"])
    for prev, nxt in zip(sorted_rows, sorted_rows[1:]):
        delta = nxt["time"] - prev["time"]
        if delta > expected_interval * 1.5:
            issues.append(
                _issue(
                    security_id,
                    "missing_timestamp",
                    "WARN",
                    nxt["time"],
                    {"expected_interval": expected_interval.total_seconds(), "gap_seconds": delta.total_seconds()},
                )
            )
    return issues


def validate_non_monotonic(
    security_id: int,
    rows: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    if not rows:
        return issues

    for prev, nxt in zip(rows, rows[1:]):
        if nxt["time"] <= prev["time"]:
            issues.append(
                _issue(
                    security_id,
                    "non_monotonic_timestamp",
                    "ALERT",
                    nxt["time"],
                    {"prev_time": prev["time"].isoformat(), "next_time": nxt["time"].isoformat()},
                )
            )
    return issues


def validate_zero_negative_prices(
    security_id: int,
    rows: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for row in rows:
        if row["close"] <= 0 or row["open"] <= 0 or row["high"] <= 0 or row["low"] <= 0:
            issues.append(
                _issue(
                    security_id,
                    "invalid_price",
                    "ALERT",
                    row["time"],
                    {"open": row["open"], "high": row["high"], "low": row["low"], "close": row["close"]},
                )
            )
    return issues


def validate_corp_actions_consistency(
    security_id: int,
    corp_actions: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    seen_dates = set()
    for action in corp_actions:
        key = (action.get("ex_date"), action.get("action_type"))
        if key in seen_dates:
            issues.append(
                _issue(
                    security_id,
                    "duplicate_corp_action",
                    "WARN",
                    datetime.fromisoformat(action["ex_date"]).replace(tzinfo=timezone.utc),
                    {"action_type": action.get("action_type"), "ex_date": action.get("ex_date")},
                )
            )
        else:
            seen_dates.add(key)
    return issues


def validate_index_vs_etf(
    index_security_id: int,
    index_rows: Sequence[Dict[str, Any]],
    etf_rows: Sequence[Dict[str, Any]],
    threshold: float,
) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    if not index_rows or not etf_rows:
        return issues

    etf_by_time = {row["time"]: row for row in etf_rows}
    for idx_row in index_rows:
        etf_row = etf_by_time.get(idx_row["time"])
        if not etf_row:
            continue
        index_return = _pct_change(idx_row)
        etf_return = _pct_change(etf_row)
        if abs(index_return - etf_return) > threshold:
            issues.append(
                _issue(
                    index_security_id,
                    "index_etf_drift",
                    "WARN",
                    idx_row["time"],
                    {"index_return": index_return, "etf_return": etf_return, "threshold": threshold},
                )
            )
    return issues


def _pct_change(row: Dict[str, Any]) -> float:
    open_price = row["open"]
    close_price = row["close"]
    if open_price == 0:
        return 0.0
    return (close_price - open_price) / open_price

