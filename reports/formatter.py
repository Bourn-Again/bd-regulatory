"""
Console and CSV report output formatting.
"""
from __future__ import annotations

from typing import List

from calculators.net_capital import NetCapitalResult
from calculators.customer_reserve import CustomerReserveResult
from calculators.margin import MarginSummary, MarginResult
from calculators.focus_report import FOCUSReportResult


_W = 70   # console width


def _header(title: str) -> None:
    print()
    print("=" * _W)
    print(f"  {title}")
    print("=" * _W)


def _section(title: str) -> None:
    print(f"\n  ── {title} {'─' * (_W - len(title) - 7)}")


def _row(label: str, value: float, flag: str = "") -> None:
    vstr = f"${value:>20,.2f}"
    print(f"  {label:<42} {vstr}  {flag}")


def _pct_row(label: str, pct: float, flag: str = "") -> None:
    print(f"  {label:<42} {pct:>18.2f}%  {flag}")


def _bool_flag(ok: bool) -> str:
    return "✓ PASS" if ok else "✗ FAIL"


def print_net_capital(result: NetCapitalResult) -> None:
    _header("NET CAPITAL — SEC Rule 15c3-1 (Alternative Method)")

    _section("Capital Base")
    _row("Stockholders' Equity",        result.stockholders_equity)
    _row("Allowable Subordinated Debt", result.allowable_sub_debt)
    _row("Total Capital",               result.total_capital)

    _section("Non-Allowable Asset Deductions")
    for name, amt in result.non_allowable_assets.items():
        _row(f"  {name.replace('_', ' ').title()}", -amt)
    _row("Total Non-Allowable Assets",  -result.total_non_allowable)
    _row("Tentative Net Capital",       result.tentative_net_capital)

    _section("Haircut Summary by Type")
    by_type: dict = {}
    for h in result.haircut_details:
        by_type.setdefault(h.security_type, [0.0, 0.0])
        by_type[h.security_type][0] += h.market_value
        by_type[h.security_type][1] += h.haircut_amount
    for stype, (mv, hc) in sorted(by_type.items()):
        pct = (hc / mv * 100) if mv > 0 else 0
        print(f"  {'  ' + stype:<40} MV: ${mv:>14,.0f}  HC: ${hc:>12,.0f}  ({pct:.1f}%)")
    _row("Total Haircuts",              -result.total_haircuts)

    _section("Net Capital Result")
    _row("Net Capital",                 result.net_capital)
    _row("Aggregate Debit Items",       result.aggregate_debit_items)
    _row("Required Net Capital (2%)",   result.required_net_capital)
    _row("Early Warning Level (5%)",    result.early_warning_level)
    _row("Excess Net Capital",          result.excess_net_capital,
         _bool_flag(result.is_compliant))

    cushion = result.cushion_pct
    if cushion != float("inf"):
        _pct_row("Net Capital as % of ADI",     cushion * 100,
                 "⚠ EARLY WARNING" if result.is_early_warning else "")
    else:
        print(f"  {'Net Capital as % of ADI':<42} {'N/A (no ADI)':>21}")

    print()
    status = "✓ COMPLIANT" if result.is_compliant else "✗ NON-COMPLIANT"
    print(f"  STATUS: {status}")
    if result.is_early_warning:
        print("  ⚠  EARLY WARNING THRESHOLD BREACHED — notify regulators")


def print_customer_reserve(result: CustomerReserveResult) -> None:
    _header("CUSTOMER RESERVE — SEC Rule 15c3-3")

    for label, items in [("Customer", result.customer), ("PAB", result.pab)]:
        _section(f"{label} Reserve Formula")
        print(f"  {'CREDITS':}")
        _row("  Free Credit Balances",           items.free_credit_balances)
        _row("  Net Credit (Margin Accounts)",   items.net_credit_margin_accounts)
        _row("  Amounts Payable — Short Sales",  items.amounts_payable_short_sales)
        _row("  Stock Borrowed from Customers",  items.stock_borrowed_from_customers)
        _row("  Fails to Receive (firm owes)",   items.customer_fails_to_receive)
        _row("  Accrued Interest Payable",       items.accrued_interest_payable)
        _row("  Total Credits",                  items.total_credits)
        print()
        print(f"  {'DEBITS':}")
        _row("  Customer Debit Balances",        items.customer_debit_balances)
        _row("  Securities Borrowed (shorts)",   items.securities_borrowed_cover_shorts)
        _row("  Cash at Clearing Orgs",          items.cash_at_clearing_orgs)
        _row("  Securities Loaned to Cust.",     items.securities_loaned_to_customers)
        _row("  Fails to Deliver (firm recv.)",  items.customer_fails_to_deliver)
        _row("  Total Debits",                   items.total_debits)
        print()
        _row(f"  {label} Reserve Required",      items.reserve_required)

    _section("Combined Reserve Position")
    _row("Total Reserve Required",              result.total_reserve_required)
    _row("Current Reserve Deposit",             result.current_reserve_deposit)
    if result.reserve_deficiency > 0:
        _row("Reserve Deficiency",              -result.reserve_deficiency, "✗ DEFICIENT")
    else:
        _row("Reserve Surplus",                 result.reserve_surplus, "✓ FUNDED")

    print()
    print(f"  STATUS: {'✓ COMPLIANT' if result.is_compliant else '✗ NON-COMPLIANT — FUND DEFICIENCY'}")


def print_margin_summary(result: MarginSummary) -> None:
    _header("MARGIN SUMMARY — Reg T / FINRA Rule 4210")

    _section("Portfolio Overview")
    _row("Total Accounts Reviewed",             result.total_accounts)
    _row("Total Long Market Value",             result.total_long_mv)
    _row("Total Customer Equity",               result.total_equity)
    _row("Accounts with Margin Calls",          result.accounts_with_margin_calls)
    _row("Total Margin Call Amount",            result.total_margin_call_amount)

    calls = [r for r in result.account_details if r.has_margin_call]
    if calls:
        _section(f"Margin Calls ({len(calls)} accounts — showing top 10 by call size)")
        calls_sorted = sorted(calls, key=lambda x: -x.margin_call_amount)[:10]
        print(f"  {'Account':<14} {'Type':<12} {'LMV':>14} {'Equity':>14} {'Call Amt':>14} {'Call Type'}")
        print("  " + "-" * 66)
        for r in calls_sorted:
            print(
                f"  {r.account_id:<14} {r.account_type:<12} "
                f"${r.long_market_value:>12,.0f} ${r.equity:>12,.0f} "
                f"${r.margin_call_amount:>12,.0f} {r.margin_call_type}"
            )
    else:
        _section("Margin Calls")
        print("  No margin calls — all accounts within maintenance requirements.")

    # Repo margin summary
    repo_calls = [r for r in result.repo_details if not r.is_compliant]
    _section(f"Repo Variation Margin ({len(repo_calls)} calls)")
    if repo_calls:
        total_repo_call = sum(r.variation_margin_call for r in repo_calls)
        print(f"  {len(repo_calls)} repo positions require variation margin calls")
        _row("  Total Repo Variation Margin Call", total_repo_call)
    else:
        print("  All repo positions within margin requirements.")


def print_focus_report(result: FOCUSReportResult) -> None:
    _header(f"FOCUS REPORT Part II — {result.firm_name}")
    print(f"  BD ID: {result.broker_dealer_id}   Period: {result.report_period}   As Of: {result.as_of_date}")

    sections = [
        ("Balance Sheet",          ["1", "2", "3", "4", "5", "8", "9", "10", "16"]),
        ("Net Capital (15c3-1)",   ["3210","3215","3220","3221","3225","3226","3230","3240","3250","3260","3400","3410"]),
        ("Customer Reserve (15c3-3)", ["2010","2015","2016","2017","2020","2030","2035","2040","2041","2042","2060","2061","2062"]),
        ("Margin",                 ["4010","4020","4030","4040"]),
        ("Revenue",                ["4800","4810","4820"]),
    ]

    for sec_name, lines in sections:
        _section(sec_name)
        for line in lines:
            item = result.get(line)
            if item:
                note = f"  [{item.note}]" if item.note else ""
                if item.note == "Percentage":
                    _pct_row(f"  {item.line}  {item.description}", item.amount)
                elif item.note == "Count":
                    print(f"  {item.line}  {item.description:<38} {item.amount:>8.0f} accounts")
                else:
                    _row(f"  {item.line}  {item.description}", item.amount, note)


def print_compliance_dashboard(
    nc: NetCapitalResult,
    reserve: CustomerReserveResult,
    margin: MarginSummary,
) -> None:
    _header("CONSOLIDATED COMPLIANCE DASHBOARD")

    checks = [
        ("15c3-1  Net Capital (Alt. Method)",   nc.is_compliant),
        ("15c3-1  Early Warning Threshold",      not nc.is_early_warning),
        ("15c3-3  Customer Reserve Funded",      reserve.is_compliant),
        ("Margin  Accounts w/ Calls = 0",        margin.accounts_with_margin_calls == 0),
    ]

    all_pass = all(ok for _, ok in checks)

    for desc, ok in checks:
        status = "✓ PASS" if ok else "✗ FAIL"
        print(f"  {status}  {desc}")

    print()
    if all_pass:
        print("  ✓ ALL REGULATORY CHECKS PASSED")
    else:
        fail_count = sum(1 for _, ok in checks if not ok)
        print(f"  ✗ {fail_count} REGULATORY CHECK(S) FAILED — review required")
    print()
