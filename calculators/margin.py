"""
Regulation T & FINRA Rule 4210 — Margin calculations.
Covers customer accounts, prime brokerage, and repo margin.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional

import config
from models.book_of_record import BookOfRecord
from models.account import Account
from models.enums import AccountType, PositionSide


@dataclass
class MarginResult:
    account_id: str
    account_type: str
    long_market_value: float
    short_market_value: float
    debit_balance: float
    equity: float
    reg_t_initial_required: float
    maintenance_required: float
    house_required: float
    excess_equity: float           # Equity above maintenance
    buying_power: float
    has_margin_call: bool
    margin_call_amount: float
    margin_call_type: str          # "REG_T", "MAINTENANCE", "HOUSE", or ""
    concentration_charge: float


@dataclass
class RepoMarginResult:
    repo_id: str
    direction: str
    collateral_mv: float
    cash_amount: float
    haircut_applied: float          # Haircut %
    required_collateral: float      # Cash / (1 - haircut)
    variation_margin_call: float    # Positive = call required
    is_compliant: bool


@dataclass
class MarginSummary:
    total_accounts: int
    accounts_with_margin_calls: int
    total_margin_call_amount: float
    total_long_mv: float
    total_equity: float
    account_details: List[MarginResult]
    repo_details: List[RepoMarginResult]


class MarginCalculator:
    def __init__(self, bor: BookOfRecord, as_of: date = None):
        self.bor = bor
        self.as_of = as_of or config.CALCULATION_DATE

    def _account_margin(self, acct: Account) -> MarginResult:
        lmv = acct.long_market_value
        smv = acct.short_market_value
        debit = acct.margin_debit
        equity = acct.equity

        # Initial Reg T (new purchases only — approximated on full LMV)
        reg_t_initial = config.REG_T_INITIAL_MARGIN * lmv

        # Maintenance minimum (FINRA 4210)
        maint_required = config.MAINTENANCE_MARGIN * lmv

        # House requirement (firm policy — higher)
        house_required = config.HOUSE_MARGIN * lmv

        # Concentration charge: if any single position > threshold% of portfolio
        conc_charge = self._concentration_charge(acct)

        effective_maint = house_required + conc_charge

        # Excess equity
        excess = equity - effective_maint

        # Buying power (50% initial → each $1 equity supports $2 buying power)
        buying_power = max(excess / config.REG_T_INITIAL_MARGIN, 0.0)

        # Determine margin call
        margin_call = 0.0
        call_type = ""
        has_call = False

        if equity < 0:
            # Deficit — full house call
            margin_call = effective_maint - equity
            call_type = "HOUSE"
            has_call = True
        elif equity < effective_maint:
            margin_call = effective_maint - equity
            call_type = "HOUSE"
            has_call = True
        elif equity < maint_required:
            margin_call = maint_required - equity
            call_type = "MAINTENANCE"
            has_call = True

        return MarginResult(
            account_id=acct.account_id,
            account_type=acct.account_type.value,
            long_market_value=lmv,
            short_market_value=smv,
            debit_balance=debit,
            equity=equity,
            reg_t_initial_required=reg_t_initial,
            maintenance_required=maint_required,
            house_required=house_required,
            excess_equity=max(excess, 0.0),
            buying_power=buying_power,
            has_margin_call=has_call,
            margin_call_amount=round(margin_call, 2),
            margin_call_type=call_type,
            concentration_charge=round(conc_charge, 2),
        )

    def _concentration_charge(self, acct: Account) -> float:
        """
        Extra charge if any position > CONCENTRATION_THRESHOLD of portfolio.
        """
        total_lmv = acct.long_market_value
        if total_lmv <= 0:
            return 0.0

        # Get positions for this account
        acct_positions = [
            p for p in self.bor.positions
            if p.account_id == acct.account_id and p.side == PositionSide.LONG
        ]

        max_position_pct = 0.0
        for pos in acct_positions:
            pct = pos.market_value / total_lmv
            if pct > max_position_pct:
                max_position_pct = pct

        if max_position_pct > config.CONCENTRATION_THRESHOLD:
            excess_pct = max_position_pct - config.CONCENTRATION_THRESHOLD
            return total_lmv * excess_pct * config.CONCENTRATION_CHARGE_RATE
        return 0.0

    def _repo_margin(self) -> List[RepoMarginResult]:
        from .haircuts import compute_haircut
        results = []
        for repo in self.bor.get_repo_positions():
            sec = self.bor.securities.get(repo.collateral_cusip)
            ytm = sec.years_to_maturity(self.as_of) if sec else None
            price = sec.price if sec else None
            hc_pct, _ = compute_haircut(
                security_type=repo.collateral_type,
                market_value=repo.collateral_market_value,
                years_to_maturity=ytm,
                price=price,
            )
            required_collateral = repo.cash_amount / (1 - hc_pct) if hc_pct < 1 else float("inf")
            variation_call = max(required_collateral - repo.collateral_market_value, 0.0)
            threshold = repo.cash_amount * config.REPO_MARGIN_CALL_THRESHOLD
            trigger_call = variation_call > threshold

            results.append(RepoMarginResult(
                repo_id=repo.repo_id,
                direction=repo.direction,
                collateral_mv=repo.collateral_market_value,
                cash_amount=repo.cash_amount,
                haircut_applied=hc_pct,
                required_collateral=round(required_collateral, 2),
                variation_margin_call=round(variation_call, 2) if trigger_call else 0.0,
                is_compliant=not trigger_call,
            ))
        return results

    def calculate(self) -> MarginSummary:
        all_accts = (
            self.bor.get_customer_accounts() +
            self.bor.get_pab_accounts()
        )

        margin_results: List[MarginResult] = []
        for acct in all_accts:
            if acct.is_margin_account:
                margin_results.append(self._account_margin(acct))

        calls = [r for r in margin_results if r.has_margin_call]
        repo_results = self._repo_margin()

        return MarginSummary(
            total_accounts=len(margin_results),
            accounts_with_margin_calls=len(calls),
            total_margin_call_amount=sum(r.margin_call_amount for r in calls),
            total_long_mv=sum(r.long_market_value for r in margin_results),
            total_equity=sum(r.equity for r in margin_results),
            account_details=margin_results,
            repo_details=repo_results,
        )
