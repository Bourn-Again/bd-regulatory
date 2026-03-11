"""
FOCUS Report Part II — Key regulatory reporting line items.
Assembles outputs from all calculators into FOCUS line item format.
"""
from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import date
from typing import Dict, Optional

import config
from models.book_of_record import BookOfRecord
from .net_capital import NetCapitalResult
from .customer_reserve import CustomerReserveResult
from .margin import MarginSummary


@dataclass
class FOCUSLineItem:
    line: str
    description: str
    amount: float
    note: str = ""


@dataclass
class FOCUSReportResult:
    firm_name: str
    broker_dealer_id: str
    report_period: str
    as_of_date: date
    line_items: Dict[str, FOCUSLineItem]

    def get(self, line: str) -> Optional[FOCUSLineItem]:
        return self.line_items.get(line)


class FOCUSReportAssembler:
    def __init__(
        self,
        bor: BookOfRecord,
        nc_result: NetCapitalResult,
        reserve_result: CustomerReserveResult,
        margin_summary: MarginSummary,
        as_of: date = None,
    ):
        self.bor = bor
        self.nc = nc_result
        self.reserve = reserve_result
        self.margin = margin_summary
        self.as_of = as_of or config.CALCULATION_DATE

    def assemble(self) -> FOCUSReportResult:
        items: Dict[str, FOCUSLineItem] = {}

        def add(line: str, desc: str, amount: float, note: str = "") -> None:
            items[line] = FOCUSLineItem(line=line, description=desc, amount=round(amount, 2), note=note)

        total_assets = self.bor.get_total_assets()
        total_liabilities = self.bor.get_total_liabilities()

        # ── Balance Sheet ──────────────────────────────────────────────────────
        add("1",    "Total Assets",                         total_assets)
        add("2",    "Cash and Cash Equivalents",
            sum(a.cash_balance for a in self.bor.accounts.values() if a.cash_balance > 0))
        add("3",    "Receivables from Customers",
            sum(a.margin_debit for a in self.bor.get_customer_accounts()))
        add("4",    "Receivables from Brokers-Dealers",
            sum(r.cash_amount for r in self.bor.repo_positions if r.direction == "REVERSE"))
        add("5",    "Securities Owned (MV)",
            sum(p.market_value for p in self.bor.positions if p.side.value == "LONG"))
        add("8",    "Total Liabilities",                    total_liabilities)
        add("9",    "Payables to Customers",
            sum(max(a.cash_balance, 0) for a in self.bor.get_customer_accounts()))
        add("10",   "Payables to Broker-Dealers",
            sum(r.cash_amount for r in self.bor.repo_positions if r.direction == "REPO"))
        add("16",   "Stockholders' Equity / Net Worth",     self.nc.stockholders_equity)

        # ── Net Capital (Part II — Lines 3200–3400) ────────────────────────────
        add("3210", "Stockholders' Equity",                 self.nc.stockholders_equity)
        add("3215", "Allowable Subordinated Debt",          self.nc.allowable_sub_debt)
        add("3220", "Total Capital",                        self.nc.total_capital)
        add("3221", "Less: Non-Allowable Assets",           self.nc.total_non_allowable)
        add("3225", "Tentative Net Capital",                self.nc.tentative_net_capital)
        add("3226", "Less: Haircuts on Securities",         self.nc.total_haircuts)
        add("3230", "Net Capital",                          self.nc.net_capital)
        add("3240", "Required Net Capital (2% of ADI)",     self.nc.required_net_capital,
            "Alternative Method")
        add("3250", "Excess Net Capital",                   self.nc.excess_net_capital)
        add("3260", "Net Capital as % of Agg Debit Items",
            self.nc.cushion_pct * 100 if self.nc.cushion_pct != float("inf") else 0.0,
            "Percentage")
        add("3400", "Aggregate Debit Items",                self.nc.aggregate_debit_items)
        add("3410", "Early Warning Level (5% of ADI)",      self.nc.early_warning_level)

        # ── Customer Reserve (Part II — Lines 2000–2100) ──────────────────────
        add("2010", "Customer Credit Balances (Free)",      self.reserve.customer.free_credit_balances)
        add("2015", "Customer Net Credit (Margin Accts)",   self.reserve.customer.net_credit_margin_accounts)
        add("2016", "Amounts Payable — Short Sales",        self.reserve.customer.amounts_payable_short_sales)
        add("2017", "Stock Borrowed from Customers",        self.reserve.customer.stock_borrowed_from_customers)
        add("2020", "Total Customer Credit Items",          self.reserve.customer.total_credits)
        add("2030", "Total Customer Debit Items",           self.reserve.customer.total_debits)
        add("2035", "Customer Debit Balances",              self.reserve.customer.customer_debit_balances)
        add("2040", "Net Customer Reserve Required",        self.reserve.customer.reserve_required)
        add("2041", "Current Customer Reserve Deposit",     self.reserve.current_reserve_deposit)
        add("2042", "Reserve Surplus / (Deficiency)",       self.reserve.reserve_surplus - self.reserve.reserve_deficiency)
        add("2060", "PAB Reserve Required",                 self.reserve.pab.reserve_required)
        add("2061", "PAB Credits",                          self.reserve.pab.total_credits)
        add("2062", "PAB Debits",                           self.reserve.pab.total_debits)

        # ── Margin Summary ─────────────────────────────────────────────────────
        add("4010", "Total Customer Long Market Value",     self.margin.total_long_mv)
        add("4020", "Total Customer Equity",                self.margin.total_equity)
        add("4030", "Accounts with Margin Calls",           self.margin.accounts_with_margin_calls,
            "Count")
        add("4040", "Total Margin Call Amount",             self.margin.total_margin_call_amount)

        # ── Revenue / P&L (simplified) ────────────────────────────────────────
        # Estimated from repo income + haircut data (placeholder values)
        repo_income = sum(
            r.cash_amount * r.rate * 1 / 365
            for r in self.bor.repo_positions
        )
        add("4800", "Net Revenue — Repo / Financing",       repo_income, "Daily accrual")
        add("4810", "Net Revenue — Market Making",          0.0, "Not computed in this model")
        add("4820", "Net Revenue — Prime Brokerage",        0.0, "Not computed in this model")

        return FOCUSReportResult(
            firm_name=config.FIRM_NAME,
            broker_dealer_id=config.BROKER_DEALER_ID,
            report_period=config.REPORT_PERIOD,
            as_of_date=self.as_of,
            line_items=items,
        )

    def export_csv(self, result: FOCUSReportResult, output_path: str) -> None:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Firm", result.firm_name])
            writer.writerow(["BD ID", result.broker_dealer_id])
            writer.writerow(["Period", result.report_period])
            writer.writerow(["As Of", result.as_of_date.isoformat()])
            writer.writerow([])
            writer.writerow(["Line", "Description", "Amount ($)", "Note"])
            for item in sorted(result.line_items.values(), key=lambda x: x.line):
                writer.writerow([item.line, item.description, f"{item.amount:,.2f}", item.note])
        print(f"FOCUS Report exported → {output_path}")
