"""
Loads CSV files produced by mock_generator into model objects.
"""
from __future__ import annotations

import csv
from datetime import date
from typing import Dict, List, Optional

import config
from models.enums import SecurityType, AccountType, BusinessLine, PositionSide
from models.security_master import SecurityMaster
from models.account import Account
from models.position import Position
from models.repo_position import RepoPosition
from models.fail_position import FailPosition
from models.book_of_record import BookOfRecord


def _parse_date(s: str) -> Optional[date]:
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def _parse_float(s: str, default: float = 0.0) -> float:
    try:
        return float(s)
    except (ValueError, TypeError):
        return default


def _parse_bool(s: str) -> bool:
    return s.strip().lower() in ("true", "1", "yes")


def load_securities(path: str = config.SECURITIES_FILE) -> Dict[str, SecurityMaster]:
    result: Dict[str, SecurityMaster] = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            def _opt(key):
                v = row.get(key, "")
                return _parse_float(v) if v else None
            sec = SecurityMaster(
                cusip=row["cusip"],
                description=row["description"],
                security_type=SecurityType(row["security_type"]),
                asset_class=row["asset_class"],
                price=_parse_float(row["price"]),
                maturity_date=_parse_date(row["maturity_date"]),
                coupon=_parse_float(row["coupon"]) if row["coupon"] else None,
                rating=row["rating"] or None,
                currency=row.get("currency", "USD"),
                delta=_opt("delta"),
                gamma=_opt("gamma"),
                vega=_opt("vega"),
                theta=_opt("theta"),
            )
            result[sec.cusip] = sec
    return result


def load_accounts(path: str = config.ACCOUNTS_FILE) -> Dict[str, Account]:
    result: Dict[str, Account] = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            acct = Account(
                account_id=row["account_id"],
                account_type=AccountType(row["account_type"]),
                business_line=BusinessLine(row["business_line"]),
                cash_balance=_parse_float(row["cash_balance"]),
                margin_debit=_parse_float(row["margin_debit"]),
                short_market_value=_parse_float(row["short_market_value"]),
                long_market_value=_parse_float(row["long_market_value"]),
                is_margin_account=_parse_bool(row["is_margin_account"]),
                is_prime_brokerage=_parse_bool(row["is_prime_brokerage"]),
                client_name=row.get("client_name", ""),
            )
            result[acct.account_id] = acct
    return result


def load_positions(path: str = config.POSITIONS_FILE) -> List[Position]:
    result: List[Position] = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            pos = Position(
                position_id=row["position_id"],
                account_id=row["account_id"],
                cusip=row["cusip"],
                side=PositionSide(row["side"]),
                quantity=_parse_float(row["quantity"]),
                market_value=_parse_float(row["market_value"]),
                cost_basis=_parse_float(row["cost_basis"]),
                business_line=BusinessLine(row["business_line"]),
                as_of_date=_parse_date(row["as_of_date"]) or config.CALCULATION_DATE,
            )
            result.append(pos)
    return result


def load_repo_positions(path: str = config.REPO_POSITIONS_FILE) -> List[RepoPosition]:
    result: List[RepoPosition] = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            repo = RepoPosition(
                repo_id=row["repo_id"],
                direction=row["direction"],
                collateral_cusip=row["collateral_cusip"],
                collateral_market_value=_parse_float(row["collateral_market_value"]),
                collateral_type=SecurityType(row["collateral_type"]),
                cash_amount=_parse_float(row["cash_amount"]),
                rate=_parse_float(row["rate"]),
                start_date=_parse_date(row["start_date"]) or config.CALCULATION_DATE,
                end_date=_parse_date(row["end_date"]) or config.CALCULATION_DATE,
                counterparty=row["counterparty"],
                account_type=AccountType(row["account_type"]),
            )
            result.append(repo)
    return result


def load_firm_balance_sheet(path: str = config.FIRM_BALANCE_SHEET_FILE) -> Dict[str, float]:
    result: Dict[str, float] = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            result[row["item"]] = _parse_float(row["value"])
    return result


def load_fail_positions(path: str = config.FAIL_POSITIONS_FILE) -> List[FailPosition]:
    import os
    if not os.path.exists(path):
        return []
    result: List[FailPosition] = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            fp = FailPosition(
                fail_id=row["fail_id"],
                account_id=row["account_id"],
                cusip=row["cusip"],
                direction=row["direction"],
                trade_date=_parse_date(row["trade_date"]) or config.CALCULATION_DATE,
                settle_date=_parse_date(row["settle_date"]) or config.CALCULATION_DATE,
                quantity=_parse_float(row["quantity"]),
                market_value=_parse_float(row["market_value"]),
                contra_party=row["contra_party"],
                reason=row["reason"],
                business_line=row["business_line"],
            )
            result.append(fp)
    return result


def load_book_of_record() -> BookOfRecord:
    print("Loading data...")
    securities = load_securities()
    accounts = load_accounts()
    positions = load_positions()
    repos = load_repo_positions()
    firm_bs = load_firm_balance_sheet()
    print(
        f"  Loaded {len(securities)} securities, {len(accounts)} accounts, "
        f"{len(positions)} positions, {len(repos)} repos"
    )
    return BookOfRecord(
        securities=securities,
        accounts=accounts,
        positions=positions,
        repo_positions=repos,
        firm_balance_sheet=firm_bs,
    )
