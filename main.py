"""
Broker-Dealer Regulatory Calculator — Entry Point

Flow:
  1. Generate (or load) mock data
  2. Load BookOfRecord from CSVs
  3. Run NetCapitalCalculator       → Rule 15c3-1
  4. Run CustomerReserveCalculator  → Rule 15c3-3
  5. Run MarginCalculator           → Reg T / FINRA 4210
  6. Run FOCUSReportAssembler       → FOCUS Part II
  7. Print consolidated compliance dashboard
"""
import os
import sys

import config
from data.mock_generator import generate_all
from data.loader import load_book_of_record
from calculators.net_capital import NetCapitalCalculator
from calculators.customer_reserve import CustomerReserveCalculator
from calculators.margin import MarginCalculator
from calculators.focus_report import FOCUSReportAssembler
from reports.formatter import (
    print_net_capital,
    print_customer_reserve,
    print_margin_summary,
    print_focus_report,
    print_compliance_dashboard,
)


def main(regenerate: bool = True) -> None:
    # ── Step 1: Data Generation ───────────────────────────────────────────────
    if regenerate or not os.path.exists(config.SECURITIES_FILE):
        generate_all()

    # ── Step 2: Load BookOfRecord ─────────────────────────────────────────────
    bor = load_book_of_record()

    # ── Step 3: Net Capital ───────────────────────────────────────────────────
    print("\nRunning Rule 15c3-1 Net Capital calculation...")
    nc_calc = NetCapitalCalculator(bor, as_of=config.CALCULATION_DATE)
    nc_result = nc_calc.calculate()

    # ── Step 4: Customer Reserve ──────────────────────────────────────────────
    print("Running Rule 15c3-3 Customer Reserve calculation...")
    reserve_calc = CustomerReserveCalculator(bor, as_of=config.CALCULATION_DATE)
    reserve_result = reserve_calc.calculate()

    # ── Step 5: Margin ────────────────────────────────────────────────────────
    print("Running Reg T / Margin calculation...")
    margin_calc = MarginCalculator(bor, as_of=config.CALCULATION_DATE)
    margin_result = margin_calc.calculate()

    # ── Step 6: FOCUS Report ──────────────────────────────────────────────────
    print("Assembling FOCUS Report Part II...")
    focus_assembler = FOCUSReportAssembler(
        bor=bor,
        nc_result=nc_result,
        reserve_result=reserve_result,
        margin_summary=margin_result,
        as_of=config.CALCULATION_DATE,
    )
    focus_result = focus_assembler.assemble()
    focus_assembler.export_csv(focus_result, "data/csv/focus_report.csv")

    # ── Step 7: Print Reports ─────────────────────────────────────────────────
    print_net_capital(nc_result)
    print_customer_reserve(reserve_result)
    print_margin_summary(margin_result)
    print_focus_report(focus_result)
    print_compliance_dashboard(nc_result, reserve_result, margin_result)


if __name__ == "__main__":
    regenerate_flag = "--no-regen" not in sys.argv
    main(regenerate=regenerate_flag)
