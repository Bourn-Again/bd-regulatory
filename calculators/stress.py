"""
Pre-defined market stress scenarios.

Five scenarios shock position market values and rerun NC / Reserve / Margin
calculators, returning the impact delta vs baseline.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from models.book_of_record import BookOfRecord
from models.position import Position
from models.enums import SecurityType
from calculators.net_capital import NetCapitalCalculator, NetCapitalResult
from calculators.customer_reserve import CustomerReserveCalculator, CustomerReserveResult
from calculators.margin import MarginCalculator, MarginSummary

import config


# Average duration proxies (years) per security type
_DURATION: dict = {
    "US_TREASURY": 6.0,
    "AGENCY":      4.5,
    "CORP_IG":     5.0,
    "CORP_HY":     3.5,
    "MBS":         3.0,
    "MUNICIPAL":   7.0,
}

_EQUITY_TYPES = {"EQUITY_LISTED", "ETF"}
_FI_TYPES     = set(_DURATION.keys())

# (name, equity_factor, rate_shock_bps)
_SCENARIOS = [
    ("Equity -10%",     0.90, 0),
    ("Equity -20%",     0.80, 0),
    ("Rates +100bps",   1.00, 100),
    ("Rates +200bps",   1.00, 200),
    ("Combined Stress", 0.85, 100),
]


@dataclass
class StressScenarioResult:
    name: str
    delta_net_capital: float
    delta_reserve_required: float
    delta_margin_call_amount: float
    shocked_net_capital: float
    shocked_is_compliant: bool
    shocked_is_early_warning: bool
    shocked_reserve_required: float
    shocked_reserve_is_compliant: bool
    shocked_margin_call_count: int
    shocked_margin_call_amount: float


class StressCalculator:
    def __init__(
        self,
        bor: BookOfRecord,
        baseline_nc: NetCapitalResult,
        baseline_reserve: CustomerReserveResult,
        baseline_margin: MarginSummary,
    ):
        self.bor              = bor
        self.baseline_nc      = baseline_nc
        self.baseline_reserve = baseline_reserve
        self.baseline_margin  = baseline_margin

    def _shock_positions(self, eq_factor: float, rate_bps: int) -> List[Position]:
        """Return a new list of Position objects with shocked market values."""
        shocked = []
        for pos in self.bor.positions:
            sec = self.bor.securities.get(pos.cusip)
            stype = sec.security_type.value if sec else ""
            mv = pos.market_value

            if stype in _EQUITY_TYPES and eq_factor != 1.0:
                mv = mv * eq_factor
            elif stype in _FI_TYPES and rate_bps != 0:
                dur = _DURATION.get(stype, 5.0)
                rate_change = rate_bps / 10_000.0  # in decimal
                mv = max(mv * (1.0 - dur * rate_change), 0.0)

            # Build new Position with adjusted market_value
            shocked.append(Position(
                position_id=pos.position_id,
                account_id=pos.account_id,
                cusip=pos.cusip,
                side=pos.side,
                quantity=pos.quantity,
                market_value=round(mv, 2),
                cost_basis=pos.cost_basis,
                business_line=pos.business_line,
                as_of_date=pos.as_of_date,
            ))
        return shocked

    def _shocked_bor(self, eq_factor: float, rate_bps: int) -> BookOfRecord:
        shocked_positions = self._shock_positions(eq_factor, rate_bps)
        # Rebuild account long/short MV totals to match shocked positions
        from models.account import Account
        from models.enums import PositionSide

        lmv_by_acct: dict = {}
        smv_by_acct: dict = {}
        for pos in shocked_positions:
            if pos.side == PositionSide.LONG:
                lmv_by_acct[pos.account_id] = lmv_by_acct.get(pos.account_id, 0.0) + pos.market_value
            else:
                smv_by_acct[pos.account_id] = smv_by_acct.get(pos.account_id, 0.0) + pos.market_value

        shocked_accounts = {}
        for acct_id, acct in self.bor.accounts.items():
            shocked_accounts[acct_id] = Account(
                account_id=acct.account_id,
                account_type=acct.account_type,
                business_line=acct.business_line,
                cash_balance=acct.cash_balance,
                margin_debit=acct.margin_debit,
                short_market_value=smv_by_acct.get(acct_id, acct.short_market_value),
                long_market_value=lmv_by_acct.get(acct_id, acct.long_market_value),
                is_margin_account=acct.is_margin_account,
                is_prime_brokerage=acct.is_prime_brokerage,
                client_name=acct.client_name,
            )

        return BookOfRecord(
            securities=self.bor.securities,
            accounts=shocked_accounts,
            positions=shocked_positions,
            repo_positions=self.bor.repo_positions,
            firm_balance_sheet=self.bor.firm_balance_sheet,
        )

    def calculate(self) -> List[StressScenarioResult]:
        results = []
        for (name, eq_factor, rate_bps) in _SCENARIOS:
            sbor = self._shocked_bor(eq_factor, rate_bps)
            s_nc      = NetCapitalCalculator(sbor, config.CALCULATION_DATE).calculate()
            s_reserve = CustomerReserveCalculator(sbor, config.CALCULATION_DATE).calculate()
            s_margin  = MarginCalculator(sbor, config.CALCULATION_DATE).calculate()

            results.append(StressScenarioResult(
                name=name,
                delta_net_capital=(
                    s_nc.net_capital - self.baseline_nc.net_capital),
                delta_reserve_required=(
                    s_reserve.total_reserve_required - self.baseline_reserve.total_reserve_required),
                delta_margin_call_amount=(
                    s_margin.total_margin_call_amount - self.baseline_margin.total_margin_call_amount),
                shocked_net_capital=s_nc.net_capital,
                shocked_is_compliant=s_nc.is_compliant,
                shocked_is_early_warning=s_nc.is_early_warning,
                shocked_reserve_required=s_reserve.total_reserve_required,
                shocked_reserve_is_compliant=s_reserve.is_compliant,
                shocked_margin_call_count=s_margin.accounts_with_margin_calls,
                shocked_margin_call_amount=s_margin.total_margin_call_amount,
            ))
        return results
