"""
Regulatory thresholds, rate tables, and firm-level constants.
"""
from datetime import date

# ── Firm Balance Sheet (simulated) ───────────────────────────────────────────
STOCKHOLDERS_EQUITY = 150_000_000.0          # $150M equity
ALLOWABLE_SUBORDINATED_DEBT = 25_000_000.0   # $25M sub-debt

# Non-allowable assets (deducted from equity)
NON_ALLOWABLE_ASSETS = {
    "goodwill":              5_000_000.0,
    "intangibles":           2_000_000.0,
    "unsecured_receivables": 1_500_000.0,
    "deferred_charges":        750_000.0,
    "exchange_memberships":    500_000.0,
    "fixed_assets":          3_000_000.0,
}

# ── 15c3-1 Thresholds ─────────────────────────────────────────────────────────
NET_CAPITAL_MIN_DOLLAR = 250_000.0           # Minimum dollar requirement
NET_CAPITAL_ALT_METHOD_PCT = 0.02            # 2% of aggregate debit items
EARLY_WARNING_PCT = 0.05                     # 5% early warning level
NET_CAPITAL_RATIO_MAX = 0.15                 # PAIB distributions suspended above 15x

# ── Regulation T ─────────────────────────────────────────────────────────────
REG_T_INITIAL_MARGIN = 0.50                  # 50% initial margin requirement
MAINTENANCE_MARGIN = 0.25                    # 25% FINRA Rule 4210 minimum
HOUSE_MARGIN = 0.30                          # Firm house maintenance requirement
PRIME_BROKERAGE_MARGIN = 0.30               # Prime brokerage house margin

# Concentration charge threshold: single stock > X% of portfolio
CONCENTRATION_THRESHOLD = 0.20              # 20% of portfolio value
CONCENTRATION_CHARGE_RATE = 0.05            # Additional 5% charge

# ── Repo Margin ───────────────────────────────────────────────────────────────
REPO_MARGIN_CALL_THRESHOLD = 0.02           # 2% variation margin call trigger

# ── Calculation Date ──────────────────────────────────────────────────────────
CALCULATION_DATE = date(2026, 3, 4)

# ── Data Paths ────────────────────────────────────────────────────────────────
DATA_DIR = "data/csv"
SECURITIES_FILE = "data/csv/securities.csv"
ACCOUNTS_FILE = "data/csv/accounts.csv"
POSITIONS_FILE = "data/csv/positions.csv"
REPO_POSITIONS_FILE = "data/csv/repo_positions.csv"
FIRM_BALANCE_SHEET_FILE = "data/csv/firm_balance_sheet.csv"
FAIL_POSITIONS_FILE = "data/csv/fail_positions.csv"

# ── FOCUS Report Metadata ─────────────────────────────────────────────────────
FIRM_NAME = "Acme Securities LLC"
BROKER_DEALER_ID = "8-12345"
REPORT_PERIOD = "2026-03"

# ── OTC Equity Haircut Tiers ──────────────────────────────────────────────────
# Based on bid price buckets per 15c3-1 Appendix A
OTC_HAIRCUT_SCHEDULE = [
    (2.50,  0.40),   # bid < $2.50 → 40%
    (5.00,  0.25),   # $2.50 ≤ bid < $5.00 → 25%
    (10.00, 0.20),   # $5.00 ≤ bid < $10.00 → 20%
    (float("inf"), 0.15),  # bid ≥ $10.00 → 15%
]

# ── Corp Bond Haircut by Maturity ─────────────────────────────────────────────
CORP_IG_HAIRCUT_SCHEDULE = [
    (1,   0.02),
    (2,   0.03),
    (3,   0.04),
    (5,   0.05),
    (7,   0.07),
    (10,  0.08),
    (float("inf"), 0.09),
]

# ── MBS/CMO Haircuts ──────────────────────────────────────────────────────────
MBS_HAIRCUT = 0.07   # 7% (blended)
CMO_HAIRCUT = 0.10   # 10%
