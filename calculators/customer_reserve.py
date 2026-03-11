"""
SEC Rule 15c3-3 — Customer Reserve + PAB Reserve Formula
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List

import config
from models.book_of_record import BookOfRecord
from models.enums import AccountType


@dataclass
class ReserveLineItems:
    # Credits
    free_credit_balances: float = 0.0
    net_credit_margin_accounts: float = 0.0
    amounts_payable_short_sales: float = 0.0
    stock_borrowed_from_customers: float = 0.0
    customer_fails_to_receive: float = 0.0
    accrued_interest_payable: float = 0.0
    total_credits: float = 0.0

    # Debits
    customer_debit_balances: float = 0.0
    securities_borrowed_cover_shorts: float = 0.0
    cash_at_clearing_orgs: float = 0.0
    securities_loaned_to_customers: float = 0.0
    customer_fails_to_deliver: float = 0.0
    total_debits: float = 0.0

    reserve_required: float = 0.0

    # Per-account / per-position detail (populated by calculator)
    detail_free_credits:       List[dict] = field(default_factory=list)
    detail_net_credit_margin:  List[dict] = field(default_factory=list)
    detail_short_sales:        List[dict] = field(default_factory=list)
    detail_stock_borrowed:     List[dict] = field(default_factory=list)
    detail_fails_receive:      List[dict] = field(default_factory=list)
    detail_accrued_interest:   List[dict] = field(default_factory=list)
    detail_debit_balances:     List[dict] = field(default_factory=list)
    detail_sec_borrowed_short: List[dict] = field(default_factory=list)
    detail_cash_clearing:      List[dict] = field(default_factory=list)
    detail_sec_loaned:         List[dict] = field(default_factory=list)
    detail_fails_deliver:      List[dict] = field(default_factory=list)


@dataclass
class RehypothecationResult:
    """Rule 15c3-3(b)(3) — firm may not rehypothecate > 140% of customer debit balances."""
    customer_debit_balances: float   # aggregate customer margin debit balances
    limit: float                     # 140% × customer_debit_balances
    pledged_amount: float            # estimated customer securities currently pledged
    headroom: float                  # limit - pledged_amount
    utilization_pct: float           # pledged / limit × 100
    is_compliant: bool               # pledged <= limit
    # Breakdown of pledged usage
    pledged_to_clearing_orgs: float  # securities pledged at DTC/NSCC as margin
    pledged_as_repo_collateral: float  # customer securities used in firm's repo borrows
    pledged_to_stock_loan: float     # customer securities lent out (stock loan)


@dataclass
class CustomerReserveResult:
    customer: ReserveLineItems
    pab: ReserveLineItems
    total_reserve_required: float
    current_reserve_deposit: float       # Simulated on-hand reserve
    reserve_surplus: float               # Positive = over-reserved (good)
    reserve_deficiency: float            # Positive = deficiency (bad)
    is_compliant: bool
    rehypothecation: RehypothecationResult


class CustomerReserveCalculator:
    def __init__(self, bor: BookOfRecord, as_of: date = None):
        self.bor = bor
        self.as_of = as_of or config.CALCULATION_DATE

    def _client(self, account_id: str) -> str:
        acct = self.bor.accounts.get(account_id)
        return (acct.client_name or account_id) if acct else account_id

    def _compute_reserve(self, account_type: AccountType) -> ReserveLineItems:
        if account_type == AccountType.CUSTOMER:
            accounts = self.bor.get_customer_accounts()
            positions = self.bor.get_customer_positions()
        else:
            accounts = self.bor.get_pab_accounts()
            positions = self.bor.get_pab_positions()

        items = ReserveLineItems()

        for acct in accounts:
            cash = acct.cash_balance
            name = acct.client_name or acct.account_id

            if not acct.is_margin_account:
                # Cash account — free credit balance
                if cash > 0:
                    items.free_credit_balances += cash
                    items.detail_free_credits.append({
                        "Client":      name,
                        "Account":     acct.account_id,
                        "Cash Balance": cash,
                        "Account Type": acct.account_type.value,
                    })
            else:
                # Margin account — positive cash is a credit
                if cash > 0:
                    items.net_credit_margin_accounts += cash
                    items.detail_net_credit_margin.append({
                        "Client":      name,
                        "Account":     acct.account_id,
                        "Net Credit":  cash,
                        "Account Type": acct.account_type.value,
                    })

            # Customer margin debit balances (debit item)
            if acct.margin_debit > 0:
                items.customer_debit_balances += acct.margin_debit
                items.detail_debit_balances.append({
                    "Client":       name,
                    "Account":      acct.account_id,
                    "Margin Debit": acct.margin_debit,
                    "Long MV":      acct.long_market_value,
                    "Leverage":     (acct.margin_debit / acct.long_market_value * 100
                                     if acct.long_market_value else 0),
                    "Account Type": acct.account_type.value,
                })

            # Amounts payable for short sales (credit)
            if acct.short_market_value > 0:
                items.amounts_payable_short_sales += acct.short_market_value
                items.detail_short_sales.append({
                    "Client":    name,
                    "Account":   acct.account_id,
                    "Short MV":  acct.short_market_value,
                    "Account Type": acct.account_type.value,
                })

            # Accrued interest per account (0.5% of margin debit)
            acct_interest = acct.margin_debit * 0.005
            if acct_interest > 0:
                items.detail_accrued_interest.append({
                    "Client":         name,
                    "Account":        acct.account_id,
                    "Margin Debit":   acct.margin_debit,
                    "Accrued Interest": acct_interest,
                })

        # Approximate: accrued interest = 0.5% of total debit balances
        items.accrued_interest_payable = items.customer_debit_balances * 0.005

        # Build long/short MV maps keyed by account_id from positions
        long_mv_by_acct:  Dict[str, float] = {}
        short_mv_by_acct: Dict[str, float] = {}
        # Also track top-N positions for FTR / FTD detail
        pos_detail: List[dict] = []

        for pos in positions:
            sec  = self.bor.securities.get(pos.cusip)
            name = self._client(pos.account_id)
            desc = sec.description if sec else pos.cusip
            if pos.side.value == "LONG":
                long_mv_by_acct[pos.account_id] = (
                    long_mv_by_acct.get(pos.account_id, 0) + pos.market_value)
                pos_detail.append({
                    "account_id": pos.account_id,
                    "client":     name,
                    "cusip":      pos.cusip,
                    "security":   desc,
                    "mv":         pos.market_value,
                    "side":       "LONG",
                })
            else:
                short_mv_by_acct[pos.account_id] = (
                    short_mv_by_acct.get(pos.account_id, 0) + pos.market_value)

        total_long_mv  = sum(long_mv_by_acct.values())
        total_short_mv = sum(short_mv_by_acct.values())

        # Stock borrowed from customers (credit) — 2% of long MV, per account
        items.stock_borrowed_from_customers = total_long_mv * 0.02
        for aid, lmv in sorted(long_mv_by_acct.items(), key=lambda x: -x[1]):
            items.detail_stock_borrowed.append({
                "Client":       self._client(aid),
                "Account":      aid,
                "Long MV":      lmv,
                "Est. Borrowed (2%)": lmv * 0.02,
            })

        # Fails to receive — 0.5% of long MV, broken out per position (top 25)
        items.customer_fails_to_receive = total_long_mv * 0.005
        top_pos = sorted(pos_detail, key=lambda x: -x["mv"])[:25]
        for p in top_pos:
            items.detail_fails_receive.append({
                "Client":    p["client"],
                "Security":  p["security"],
                "CUSIP":     p["cusip"],
                "Position MV": p["mv"],
                "Est. FTR (0.5%)": p["mv"] * 0.005,
            })

        # Securities borrowed to cover customer shorts (debit) — 80% of short MV
        items.securities_borrowed_cover_shorts = total_short_mv * 0.80
        for aid, smv in sorted(short_mv_by_acct.items(), key=lambda x: -x[1]):
            items.detail_sec_borrowed_short.append({
                "Client":          self._client(aid),
                "Account":         aid,
                "Short MV":        smv,
                "Sec. Borrowed (80%)": smv * 0.80,
            })

        # Cash at clearing organizations (15% of debit balances, capped at 50%)
        items.cash_at_clearing_orgs = min(
            items.customer_debit_balances * 0.15,
            items.customer_debit_balances * 0.50,
        )
        items.detail_cash_clearing = [
            {"Clearing Org": "DTC / NSCC",  "Amount": items.cash_at_clearing_orgs * 0.65,
             "Note": "Equity clearing"},
            {"Clearing Org": "FICC",         "Amount": items.cash_at_clearing_orgs * 0.25,
             "Note": "Fixed income clearing"},
            {"Clearing Org": "OCC",          "Amount": items.cash_at_clearing_orgs * 0.10,
             "Note": "Options clearing"},
        ]

        # Securities loaned to customers (debit) — 1% of long MV, per account
        items.securities_loaned_to_customers = total_long_mv * 0.01
        for aid, lmv in sorted(long_mv_by_acct.items(), key=lambda x: -x[1]):
            items.detail_sec_loaned.append({
                "Client":          self._client(aid),
                "Account":         aid,
                "Long MV":         lmv,
                "Est. Loaned (1%)": lmv * 0.01,
            })

        # Customer fails to deliver (debit) — 0.3% of long MV, broken out per position (top 25)
        items.customer_fails_to_deliver = total_long_mv * 0.003
        for p in top_pos:
            items.detail_fails_deliver.append({
                "Client":    p["client"],
                "Security":  p["security"],
                "CUSIP":     p["cusip"],
                "Position MV": p["mv"],
                "Est. FTD (0.3%)": p["mv"] * 0.003,
            })

        # Totals
        items.total_credits = (
            items.free_credit_balances +
            items.net_credit_margin_accounts +
            items.amounts_payable_short_sales +
            items.stock_borrowed_from_customers +
            items.customer_fails_to_receive +
            items.accrued_interest_payable
        )

        items.total_debits = (
            items.customer_debit_balances +
            items.securities_borrowed_cover_shorts +
            items.cash_at_clearing_orgs +
            items.securities_loaned_to_customers +
            items.customer_fails_to_deliver
        )

        items.reserve_required = max(items.total_credits - items.total_debits, 0.0)
        return items

    def _compute_rehypothecation(self, customer: ReserveLineItems) -> RehypothecationResult:
        """
        Rule 15c3-3(b)(3): firm may pledge/lend customer margin securities only up to
        140% of the aggregate customer debit balances (margin loans).

        Pledged amount breakdown (approximated from book):
          - Pledged to clearing orgs: ~30% of customer debit balances (margin collateral
            posted to DTC/NSCC for settlement/clearing fund purposes)
          - Pledged as repo collateral: customer longs used in firm's repo borrows (~25%)
          - Pledged to stock loan: customer securities lent to short-sellers (~20%)
        Total ≈ 75% of debit balances → well within 140% limit in a healthy book.
        """
        cdb = customer.customer_debit_balances
        # Simulate actual pledging activity at realistic fractions of debit balances
        to_clearing  = cdb * 0.30
        to_repo      = cdb * 0.25
        to_stock_loan = cdb * 0.20
        total_pledged = to_clearing + to_repo + to_stock_loan

        limit = cdb * 1.40
        headroom = limit - total_pledged
        util_pct = (total_pledged / limit * 100) if limit > 0 else 0.0

        return RehypothecationResult(
            customer_debit_balances=cdb,
            limit=limit,
            pledged_amount=total_pledged,
            headroom=headroom,
            utilization_pct=util_pct,
            is_compliant=total_pledged <= limit,
            pledged_to_clearing_orgs=to_clearing,
            pledged_as_repo_collateral=to_repo,
            pledged_to_stock_loan=to_stock_loan,
        )

    def calculate(self) -> CustomerReserveResult:
        customer = self._compute_reserve(AccountType.CUSTOMER)
        pab      = self._compute_reserve(AccountType.PAB)

        total_required = customer.reserve_required + pab.reserve_required

        # Simulated current deposit: assume 97% funded (slight underage for realism)
        current_deposit = total_required * 0.97

        surplus    = current_deposit - total_required
        deficiency = max(-surplus, 0.0)
        is_compliant = current_deposit >= total_required

        rehyp = self._compute_rehypothecation(customer)

        return CustomerReserveResult(
            customer=customer,
            pab=pab,
            total_reserve_required=total_required,
            current_reserve_deposit=current_deposit,
            reserve_surplus=max(surplus, 0.0),
            reserve_deficiency=deficiency,
            is_compliant=is_compliant,
            rehypothecation=rehyp,
        )
