"""
SEC Rule 15c3-1 — Net Capital (Alternative Method)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List

import config
from models.book_of_record import BookOfRecord
from models.enums import SecurityType
from .haircuts import compute_haircut


@dataclass
class HaircutDetail:
    position_id: str
    cusip: str
    security_type: str
    market_value: float
    haircut_pct: float
    haircut_amount: float


@dataclass
class NetCapitalResult:
    # Capital base
    stockholders_equity: float
    allowable_sub_debt: float
    total_capital: float

    # Non-allowable deductions
    non_allowable_assets: Dict[str, float]
    total_non_allowable: float
    tentative_net_capital: float

    # Haircut deductions
    haircut_details: List[HaircutDetail]
    total_haircuts: float

    # Net capital
    net_capital: float
    aggregate_debit_items: float
    required_net_capital: float
    early_warning_level: float
    excess_net_capital: float

    # Compliance
    is_compliant: bool
    is_early_warning: bool
    cushion_pct: float          # (net_capital / aggregate_debit_items) if ADI > 0


class NetCapitalCalculator:
    def __init__(self, bor: BookOfRecord, as_of: date = None):
        self.bor = bor
        self.as_of = as_of or config.CALCULATION_DATE

    def calculate(self) -> NetCapitalResult:
        # ── Step 1: Capital Base ──────────────────────────────────────────────
        equity = self.bor.get_stockholders_equity()
        sub_debt = self.bor.get_allowable_sub_debt()
        total_capital = equity + sub_debt

        # ── Step 2: Non-Allowable Assets ──────────────────────────────────────
        non_allow = self.bor.get_non_allowable_assets()
        total_non_allow = sum(non_allow.values())
        tentative_nc = total_capital - total_non_allow

        # ── Step 3: Haircuts on All Positions ─────────────────────────────────
        haircut_details: List[HaircutDetail] = []

        # Firm positions
        for pos in self.bor.get_firm_positions():
            sec = self.bor.securities.get(pos.cusip)
            if sec is None:
                continue
            ytm = sec.years_to_maturity(self.as_of)
            pct, amt = compute_haircut(
                security_type=sec.security_type,
                market_value=pos.market_value,
                years_to_maturity=ytm,
                price=sec.price,
            )
            haircut_details.append(HaircutDetail(
                position_id=pos.position_id,
                cusip=pos.cusip,
                security_type=sec.security_type.value,
                market_value=pos.market_value,
                haircut_pct=pct,
                haircut_amount=amt,
            ))

        # NOTE: Customer and PAB positions are customer property segregated under Rule 15c3-3.
        # They are NOT the firm's assets and are NOT haircut in the net capital calculation.
        # Only firm proprietary positions (above) and repo collateral (below) are subject
        # to the 15c3-1 Appendix A haircut deductions.

        # Repo collateral haircuts (apply haircut to collateral MV)
        for repo in self.bor.get_repo_positions():
            sec = self.bor.securities.get(repo.collateral_cusip)
            coll_type = repo.collateral_type
            ytm = sec.years_to_maturity(self.as_of) if sec else None
            price = sec.price if sec else None
            pct, amt = compute_haircut(
                security_type=coll_type,
                market_value=repo.collateral_market_value,
                years_to_maturity=ytm,
                price=price,
            )
            haircut_details.append(HaircutDetail(
                position_id=repo.repo_id,
                cusip=repo.collateral_cusip,
                security_type=coll_type.value,
                market_value=repo.collateral_market_value,
                haircut_pct=pct,
                haircut_amount=amt,
            ))

        total_haircuts = sum(h.haircut_amount for h in haircut_details)

        # ── Step 4: Net Capital ───────────────────────────────────────────────
        net_capital = tentative_nc - total_haircuts

        # ── Step 5: Required Net Capital (Alternative Method) ─────────────────
        aggregate_debit_items = self.bor.get_aggregate_debit_items()
        required_pct = config.NET_CAPITAL_ALT_METHOD_PCT * aggregate_debit_items
        required_nc = max(required_pct, config.NET_CAPITAL_MIN_DOLLAR)
        early_warning = config.EARLY_WARNING_PCT * aggregate_debit_items

        excess = net_capital - required_nc
        is_compliant = net_capital >= required_nc
        is_early_warning = net_capital < early_warning

        if aggregate_debit_items > 0:
            cushion_pct = net_capital / aggregate_debit_items
        else:
            cushion_pct = float("inf")

        return NetCapitalResult(
            stockholders_equity=equity,
            allowable_sub_debt=sub_debt,
            total_capital=total_capital,
            non_allowable_assets=non_allow,
            total_non_allowable=total_non_allow,
            tentative_net_capital=tentative_nc,
            haircut_details=haircut_details,
            total_haircuts=total_haircuts,
            net_capital=net_capital,
            aggregate_debit_items=aggregate_debit_items,
            required_net_capital=required_nc,
            early_warning_level=early_warning,
            excess_net_capital=excess,
            is_compliant=is_compliant,
            is_early_warning=is_early_warning,
            cushion_pct=cushion_pct,
        )
