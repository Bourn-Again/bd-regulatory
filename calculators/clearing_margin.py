"""
DTC / NSCC / OCC / FICC Clearing Organization Margin.

These are separate from customer margin calls — they represent the firm's
obligations to clearing organizations based on its net settlement exposure,
portfolio risk, and capital adequacy metrics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List

import config
from models.book_of_record import BookOfRecord
from models.enums import SecurityType, PositionSide


@dataclass
class ClearingOrgCall:
    org: str                 # "NSCC", "DTC", "OCC", "FICC"
    component: str           # e.g. "Mark-to-Market", "VaR Charge", "ECP"
    description: str
    amount: float
    is_required: bool        # True = call must be met today
    due_by: str              # e.g. "10:00 AM" settlement window


@dataclass
class ClearingMarginSummary:
    # NSCC (equity settlement)
    nscc_mtm: float           # Mark-to-market on net unsettled equity positions
    nscc_var: float           # Value-at-risk component (99% 1-day)
    nscc_ecp: float           # Excess Capital Premium (charged when NC is thin)
    nscc_total: float

    # DTC (depository — securities settlement)
    dtc_net_debit_cap: float  # DTC net debit cap utilization
    dtc_collateral_monitor: float

    # OCC (options clearing)
    occ_span_margin: float    # SPAN margining on options portfolio
    occ_net_options_value: float

    # FICC (government securities)
    ficc_margin: float        # GSD clearing fund margin (govt/agency)

    # Aggregate
    total_clearing_margin: float
    calls: List[ClearingOrgCall]
    has_ecp_charge: bool      # True = firm is near capital threshold


class ClearingMarginCalculator:
    def __init__(self, bor: BookOfRecord, net_capital: float,
                 required_nc: float, as_of: date = None):
        self.bor        = bor
        self.net_capital = net_capital
        self.required_nc = required_nc
        self.as_of      = as_of or config.CALCULATION_DATE

    def calculate(self) -> ClearingMarginSummary:
        # Categorise firm positions by type
        eq_long_mv = eq_short_mv = 0.0
        fi_gov_mv = fi_corp_mv = 0.0
        opt_mv = 0.0

        for pos in self.bor.get_firm_positions():
            sec = self.bor.securities.get(pos.cusip)
            if sec is None:
                continue
            mv   = pos.market_value
            sign = 1 if pos.side == PositionSide.LONG else -1

            if sec.security_type in (SecurityType.EQUITY_LISTED,
                                      SecurityType.EQUITY_OTC, SecurityType.ETF):
                if pos.side == PositionSide.LONG:
                    eq_long_mv += mv
                else:
                    eq_short_mv += mv
            elif sec.security_type in (SecurityType.US_TREASURY,
                                        SecurityType.AGENCY):
                fi_gov_mv += mv
            elif sec.security_type in (SecurityType.CORP_IG,
                                        SecurityType.CORP_HY,
                                        SecurityType.MUNICIPAL,
                                        SecurityType.MBS):
                fi_corp_mv += mv
            elif sec.security_type == SecurityType.OPTION:
                opt_mv += mv

        net_eq_mv = eq_long_mv - eq_short_mv  # net equity exposure for NSCC

        # ── NSCC ────────────────────────────────────────────────────────────
        # MTM: daily mark on net unsettled CNS positions (≈ 2 days of net MV)
        nscc_mtm = abs(net_eq_mv) * 0.02

        # VaR component: 99% 1-day VaR approximated at 6% of gross equity MV
        nscc_var = (eq_long_mv + eq_short_mv) * 0.06

        # Excess Capital Premium: charged when net capital < 2× required
        # (i.e., cushion is thin). ECP = max(0, required × 1.5 - net_capital)
        ecp_threshold = self.required_nc * 1.5
        nscc_ecp = max(0.0, ecp_threshold - self.net_capital) * 0.10
        has_ecp = nscc_ecp > 0

        nscc_total = nscc_mtm + nscc_var + nscc_ecp

        # ── DTC ─────────────────────────────────────────────────────────────
        # Net debit cap: DTC limits intraday net debit to ~25% of firm's capital
        # We show current utilization vs. cap
        dtc_net_debit = (eq_long_mv + fi_corp_mv) * 0.005  # ~0.5% of settlement value
        dtc_coll_mon  = dtc_net_debit * 0.20               # collateral monitor add-on

        # ── OCC ─────────────────────────────────────────────────────────────
        # SPAN margin: roughly 15% of notional options MV (simplified)
        occ_span = opt_mv * 0.15
        # Net options value (premium at risk): options MV × 10%
        occ_nov  = opt_mv * 0.10

        # ── FICC ────────────────────────────────────────────────────────────
        # GSD clearing fund: based on DV01 exposure; simplified as 1% of govt MV
        ficc_margin = fi_gov_mv * 0.01

        total = nscc_total + dtc_net_debit + dtc_coll_mon + occ_span + ficc_margin

        # ── Build call objects ───────────────────────────────────────────────
        calls: List[ClearingOrgCall] = []

        if nscc_mtm > 0:
            calls.append(ClearingOrgCall(
                org="NSCC", component="Mark-to-Market",
                description="Daily MTM on net unsettled CNS equity positions",
                amount=nscc_mtm, is_required=True, due_by="10:00 AM"))
        if nscc_var > 0:
            calls.append(ClearingOrgCall(
                org="NSCC", component="VaR Charge",
                description="99% 1-day VaR on gross equity clearing exposure",
                amount=nscc_var, is_required=True, due_by="10:00 AM"))
        if nscc_ecp > 0:
            calls.append(ClearingOrgCall(
                org="NSCC", component="Excess Capital Premium",
                description="ECP assessed — net capital below 2× required minimum",
                amount=nscc_ecp, is_required=True, due_by="10:00 AM"))
        if dtc_net_debit > 0:
            calls.append(ClearingOrgCall(
                org="DTC", component="Net Debit Cap",
                description="Intraday net debit settlement exposure charge",
                amount=dtc_net_debit, is_required=False, due_by="12:00 PM"))
        if dtc_coll_mon > 0:
            calls.append(ClearingOrgCall(
                org="DTC", component="Collateral Monitor",
                description="Supplemental collateral for settlement risk monitoring",
                amount=dtc_coll_mon, is_required=False, due_by="12:00 PM"))
        if occ_span > 0:
            calls.append(ClearingOrgCall(
                org="OCC", component="SPAN Margin",
                description="Portfolio risk margin on firm options positions",
                amount=occ_span, is_required=True, due_by="9:00 AM"))
        if occ_nov > 0:
            calls.append(ClearingOrgCall(
                org="OCC", component="Net Options Value",
                description="Premium at risk on net short options positions",
                amount=occ_nov, is_required=False, due_by="9:00 AM"))
        if ficc_margin > 0:
            calls.append(ClearingOrgCall(
                org="FICC", component="GSD Clearing Fund",
                description="Govt securities division margin on net settlement exposure",
                amount=ficc_margin, is_required=True, due_by="1:00 PM"))

        return ClearingMarginSummary(
            nscc_mtm=nscc_mtm,
            nscc_var=nscc_var,
            nscc_ecp=nscc_ecp,
            nscc_total=nscc_total,
            dtc_net_debit_cap=dtc_net_debit,
            dtc_collateral_monitor=dtc_coll_mon,
            occ_span_margin=occ_span,
            occ_net_options_value=occ_nov,
            ficc_margin=ficc_margin,
            total_clearing_margin=total,
            calls=calls,
            has_ecp_charge=has_ecp,
        )
