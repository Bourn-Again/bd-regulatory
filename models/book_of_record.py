"""
BookOfRecord: aggregated view of all positions, accounts, and repos.
Provides DataFrames and filtered views for calculator consumption.
"""
from __future__ import annotations

from typing import List, Dict
import pandas as pd

from .account import Account
from .position import Position
from .repo_position import RepoPosition
from .security_master import SecurityMaster
from .enums import AccountType, PositionSide


class BookOfRecord:
    def __init__(
        self,
        securities: Dict[str, SecurityMaster],
        accounts: Dict[str, Account],
        positions: List[Position],
        repo_positions: List[RepoPosition],
        firm_balance_sheet: Dict[str, float],
    ):
        self.securities = securities
        self.accounts = accounts
        self.positions = positions
        self.repo_positions = repo_positions
        self.firm_balance_sheet = firm_balance_sheet

        self._positions_df: pd.DataFrame | None = None
        self._repos_df: pd.DataFrame | None = None

    # ── DataFrames ─────────────────────────────────────────────────────────────

    def positions_df(self) -> pd.DataFrame:
        if self._positions_df is None:
            rows = []
            for p in self.positions:
                sec = self.securities.get(p.cusip)
                acct = self.accounts.get(p.account_id)
                rows.append({
                    "position_id":    p.position_id,
                    "account_id":     p.account_id,
                    "cusip":          p.cusip,
                    "side":           p.side.value,
                    "quantity":       p.quantity,
                    "market_value":   p.market_value,
                    "cost_basis":     p.cost_basis,
                    "business_line":  p.business_line.value,
                    "as_of_date":     p.as_of_date,
                    "security_type":  sec.security_type.value if sec else None,
                    "asset_class":    sec.asset_class if sec else None,
                    "maturity_date":  sec.maturity_date if sec else None,
                    "price":          sec.price if sec else None,
                    "rating":         sec.rating if sec else None,
                    "account_type":   acct.account_type.value if acct else None,
                })
            self._positions_df = pd.DataFrame(rows)
        return self._positions_df

    def repos_df(self) -> pd.DataFrame:
        if self._repos_df is None:
            rows = []
            for r in self.repo_positions:
                rows.append({
                    "repo_id":                  r.repo_id,
                    "direction":                r.direction,
                    "collateral_cusip":         r.collateral_cusip,
                    "collateral_market_value":  r.collateral_market_value,
                    "collateral_type":          r.collateral_type.value,
                    "cash_amount":              r.cash_amount,
                    "rate":                     r.rate,
                    "start_date":               r.start_date,
                    "end_date":                 r.end_date,
                    "counterparty":             r.counterparty,
                    "account_type":             r.account_type.value,
                })
            self._repos_df = pd.DataFrame(rows)
        return self._repos_df

    # ── Filtered Views ─────────────────────────────────────────────────────────

    def get_customer_positions(self) -> List[Position]:
        return [
            p for p in self.positions
            if self.accounts.get(p.account_id) and
               self.accounts[p.account_id].account_type == AccountType.CUSTOMER
        ]

    def get_pab_positions(self) -> List[Position]:
        return [
            p for p in self.positions
            if self.accounts.get(p.account_id) and
               self.accounts[p.account_id].account_type == AccountType.PAB
        ]

    def get_firm_positions(self) -> List[Position]:
        return [
            p for p in self.positions
            if self.accounts.get(p.account_id) and
               self.accounts[p.account_id].account_type == AccountType.FIRM
        ]

    def get_repo_positions(self) -> List[RepoPosition]:
        return self.repo_positions

    def get_customer_accounts(self) -> List[Account]:
        return [a for a in self.accounts.values() if a.account_type == AccountType.CUSTOMER]

    def get_pab_accounts(self) -> List[Account]:
        return [a for a in self.accounts.values() if a.account_type == AccountType.PAB]

    # ── Aggregate Debit Items (15c3-1) ─────────────────────────────────────────

    def get_aggregate_debit_items(self) -> float:
        """
        Aggregate debit items per 15c3-1 Appendix C.
        Approximated as total customer + PAB margin debit balances.
        """
        return sum(
            a.margin_debit
            for a in self.get_customer_accounts() + self.get_pab_accounts()
            if a.margin_debit > 0
        )

    # ── Firm Equity / Balance Sheet ────────────────────────────────────────────

    def get_stockholders_equity(self) -> float:
        return self.firm_balance_sheet.get("stockholders_equity", 0.0)

    def get_allowable_sub_debt(self) -> float:
        return self.firm_balance_sheet.get("allowable_subordinated_debt", 0.0)

    def get_non_allowable_assets(self) -> Dict[str, float]:
        keys = [
            "goodwill", "intangibles", "unsecured_receivables",
            "deferred_charges", "exchange_memberships", "fixed_assets"
        ]
        return {k: self.firm_balance_sheet.get(k, 0.0) for k in keys}

    def get_total_assets(self) -> float:
        lmv = sum(p.market_value for p in self.positions if p.side == PositionSide.LONG)
        cash = sum(
            a.cash_balance for a in self.accounts.values() if a.cash_balance > 0
        )
        repo_reverse = sum(
            r.cash_amount for r in self.repo_positions if r.direction == "REVERSE"
        )
        return lmv + cash + repo_reverse

    def get_total_liabilities(self) -> float:
        smv = sum(p.market_value for p in self.positions if p.side == PositionSide.SHORT)
        debit_cash = sum(
            abs(a.cash_balance) for a in self.accounts.values() if a.cash_balance < 0
        )
        repo_payable = sum(
            r.cash_amount for r in self.repo_positions if r.direction == "REPO"
        )
        return smv + debit_cash + repo_payable
