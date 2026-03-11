"""
Generates realistic mock CSV data with named buyside clients and specific assets.
"""
from __future__ import annotations

import csv
import math
import os
import random
from datetime import date, timedelta
from typing import List

import config

random.seed(42)
CALC_DATE = config.CALCULATION_DATE
DATA_DIR = config.DATA_DIR


def _future_date(years: float) -> date:
    return CALC_DATE + timedelta(days=int(years * 365.25))

def _write_csv(path: str, rows: List[dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


# ── Named Security Universes ──────────────────────────────────────────────────

# (cusip, description, security_type, price)
EQUITY_UNIVERSE = [
    ("037833100", "Apple Inc. (AAPL)",           "EQUITY_LISTED", 226.50),
    ("594918104", "Microsoft Corp. (MSFT)",      "EQUITY_LISTED", 415.80),
    ("02079K305", "Alphabet Inc. (GOOGL)",       "EQUITY_LISTED", 175.30),
    ("023135106", "Amazon.com Inc. (AMZN)",      "EQUITY_LISTED", 222.40),
    ("67066G104", "NVIDIA Corp. (NVDA)",         "EQUITY_LISTED", 138.50),
    ("30303M102", "Meta Platforms (META)",       "EQUITY_LISTED", 655.20),
    ("88160R101", "Tesla Inc. (TSLA)",           "EQUITY_LISTED", 285.60),
    ("084670702", "Berkshire Hathaway B (BRK)",  "EQUITY_LISTED", 478.50),
    ("46625H100", "JPMorgan Chase (JPM)",        "EQUITY_LISTED", 245.80),
    ("92826C839", "Visa Inc. (V)",               "EQUITY_LISTED", 336.40),
    ("38141G104", "Goldman Sachs (GS)",          "EQUITY_LISTED", 582.30),
    ("617446448", "Morgan Stanley (MS)",         "EQUITY_LISTED", 124.60),
    ("91324P102", "UnitedHealth Group (UNH)",    "EQUITY_LISTED", 528.90),
    ("532457108", "Eli Lilly & Co. (LLY)",       "EQUITY_LISTED", 875.40),
    ("30231G102", "Exxon Mobil (XOM)",           "EQUITY_LISTED", 113.20),
]

ETF_UNIVERSE = [
    ("78462F103", "SPDR S&P 500 ETF (SPY)",          "ETF", 589.20),
    ("46090E103", "Invesco QQQ Trust (QQQ)",          "ETF", 508.30),
    ("464287614", "iShares Russell 2000 (IWM)",       "ETF", 225.40),
    ("464287440", "iShares 20+ Yr Treasury (TLT)",    "ETF", 89.50),
    ("46434G103", "iShares iBoxx HY Bond (HYG)",      "ETF", 77.80),
    ("78463V107", "SPDR Gold Shares (GLD)",           "ETF", 256.30),
]

# (cusip, description, security_type, mat_years, price, coupon, rating)
UST_UNIVERSE = [
    ("912796YB0", "US Treasury Bill 3M",          "US_TREASURY", 0.25,  99.18,  None,  "AAA"),
    ("91282CJW8", "US Treasury Note 2Y 4.625%",   "US_TREASURY", 2.0,   99.84,  4.625, "AAA"),
    ("91282CKB2", "US Treasury Note 3Y 4.375%",   "US_TREASURY", 3.0,   99.62,  4.375, "AAA"),
    ("91282CJZ1", "US Treasury Note 5Y 4.250%",   "US_TREASURY", 5.0,   99.45,  4.250, "AAA"),
    ("91282CKA4", "US Treasury Note 7Y 4.375%",   "US_TREASURY", 7.0,   98.91,  4.375, "AAA"),
    ("91282CJX6", "US Treasury Note 10Y 4.500%",  "US_TREASURY", 10.0,  98.34,  4.500, "AAA"),
    ("912810TW8", "US Treasury Bond 20Y 4.750%",  "US_TREASURY", 20.0,  96.12,  4.750, "AAA"),
    ("912810TZ1", "US Treasury Bond 30Y 4.625%",  "US_TREASURY", 30.0,  94.88,  4.625, "AAA"),
]

AGENCY_UNIVERSE = [
    ("3135G0W33", "FNMA Note 3Y 4.500%",   "AGENCY", 3.0,  99.95, 4.500, "AA+"),
    ("3135G0X24", "FNMA Note 5Y 4.375%",   "AGENCY", 5.0,  99.62, 4.375, "AA+"),
    ("3135G0Y35", "FNMA Note 10Y 4.500%",  "AGENCY", 10.0, 98.45, 4.500, "AA+"),
    ("3137EAEX3", "FHLMC Note 3Y 4.250%",  "AGENCY", 3.0,  99.88, 4.250, "AA+"),
    ("3137EAEY1", "FHLMC Note 7Y 4.625%",  "AGENCY", 7.0,  98.92, 4.625, "AA+"),
]

MUNI_UNIVERSE = [
    ("MUN00100X", "New York State GO Bond 5Y 3.500%",  "MUNICIPAL", 5.0,  101.25, 3.500, "AA"),
    ("MUN00200X", "CA Water Auth Rev Bond 10Y 3.750%", "MUNICIPAL", 10.0, 100.85, 3.750, "AAA"),
    ("MUN00300X", "Texas GO Bond 7Y 3.625%",           "MUNICIPAL", 7.0,  100.40, 3.625, "AAA"),
    ("MUN00400X", "Illinois GO Bond 5Y 4.000%",        "MUNICIPAL", 5.0,   98.75, 4.000, "A"),
]

CORP_IG_UNIVERSE = [
    ("037833DV9", "Apple Inc. 3.200% Notes 2030",        "CORP_IG", 4.0,  98.45, 3.200, "AAA"),
    ("594918BV5", "Microsoft Corp. 3.000% Notes 2032",   "CORP_IG", 6.0,  97.82, 3.000, "AAA"),
    ("023135BW5", "Amazon.com Inc. 2.500% Notes 2031",   "CORP_IG", 5.0,  96.35, 2.500, "AA"),
    ("46625HKE3", "JPMorgan Chase 3.500% Notes 2028",    "CORP_IG", 2.0,  99.12, 3.500, "A+"),
    ("38141GXP5", "Goldman Sachs 4.000% Notes 2033",     "CORP_IG", 7.0,  97.65, 4.000, "BBB+"),
    ("92343VGC2", "Verizon Comms. 3.875% Notes 2029",    "CORP_IG", 3.0,  98.75, 3.875, "BBB+"),
    ("00206RMK5", "AT&T Inc. 3.500% Notes 2032",         "CORP_IG", 6.0,  96.20, 3.500, "BBB"),
    ("097023BW3", "Boeing Co. 5.150% Notes 2030",        "CORP_IG", 4.0, 101.25, 5.150, "BBB-"),
]

CORP_HY_UNIVERSE = [
    ("345370CR6", "Ford Motor Credit 4.950% 2027",       "CORP_HY", 1.0, 99.25, 4.950, "BB+"),
    ("143658BM8", "Carnival Corp. 5.750% 2027",          "CORP_HY", 1.0, 98.50, 5.750, "BB"),
    ("001957AH0", "AMC Networks 4.750% 2026",            "CORP_HY", 0.5, 95.25, 4.750, "B+"),
    ("35906AAX7", "Frontier Comms. 5.875% 2030",         "CORP_HY", 4.0, 96.75, 5.875, "B"),
    ("25470DAJ8", "DISH DBS Corp. 5.125% 2029",          "CORP_HY", 3.0, 88.50, 5.125, "B-"),
]

MBS_UNIVERSE = [
    ("36179MU32", "GNMA Pool MA8234 6.000% TBA",  "MBS", 28.0, 101.25, 6.000, "AAA"),
    ("36179MU33", "GNMA Pool MA8891 5.500% TBA",  "MBS", 26.0,  99.75, 5.500, "AAA"),
    ("31418DXH3", "FNMA Pool BM6234 5.000% TBA",  "MBS", 25.0,  98.50, 5.000, "AAA"),
]

# (cusip, description, security_type, expiry_years, premium, strike)
OPTIONS_UNIVERSE = [
    ("SPX260320P0", "SPX Index 5200 Put Mar2026",    "OPTION", 0.04, 45.20,  5200),
    ("SPX260619C0", "SPX Index 5500 Call Jun2026",   "OPTION", 0.29, 38.50,  5500),
    ("AAPL26620P0", "Apple Inc. (AAPL) 200 Put Jun2026",  "OPTION", 0.29,  8.40,  200),
    ("NVDA26320C0", "NVIDIA Corp. (NVDA) 130 Call Mar2026","OPTION", 0.04, 12.80, 130),
    ("QQQ261218P0", "Invesco QQQ (QQQ) 480 Put Dec2026",  "OPTION", 0.79, 22.30, 480),
    ("TSLA26620P0", "Tesla Inc. (TSLA) 250 Put Jun2026",  "OPTION", 0.29, 18.60, 250),
    ("META26620C0", "Meta Platforms (META) 680 Call Jun2026","OPTION",0.29,24.50, 680),
    ("GS26919C00",  "Goldman Sachs (GS) 620 Call Sep2026","OPTION", 0.54, 15.30, 620),
]

# ── Named Buyside Accounts ────────────────────────────────────────────────────
# (account_id, client_name, account_type, style, lmv_min, lmv_max, margin_pct)
# style: HF=hedge fund, LO=long-only, FI=fixed-income, MACRO=macro
BUYSIDE_FIRMS = [
    # PAB — broker-dealer / hedge fund counterparties
    ("PAB_CITADEL", "Citadel LLC",              "PAB",  "HF",    250e6, 550e6, 0.45),
    ("PAB_MILLNM",  "Millennium Management",    "PAB",  "HF",    180e6, 420e6, 0.40),
    ("PAB_POINT72", "Point72 Asset Management", "PAB",  "HF",    120e6, 310e6, 0.42),
    ("PAB_DESHAW",  "D.E. Shaw Group",          "PAB",  "HF",     90e6, 260e6, 0.38),
    ("PAB_TWOSIG",  "Two Sigma Investments",    "PAB",  "HF",    140e6, 360e6, 0.44),
    ("PAB_AQR",     "AQR Capital Management",   "PAB",  "HF",     80e6, 200e6, 0.35),
    ("PAB_RENAISS", "Renaissance Technologies", "PAB",  "HF",    220e6, 620e6, 0.50),
    ("PAB_ELLIOTT", "Elliott Management",       "PAB",  "HF",     70e6, 190e6, 0.36),
    ("PAB_THIRDPT", "Third Point LLC",          "PAB",  "HF",     50e6, 160e6, 0.30),
    ("PAB_MANGA",   "Man Group plc",            "PAB",  "HF",     85e6, 230e6, 0.40),
    # CUSTOMER — long-only, mutual funds, macro
    ("CUST_BLKRK",  "BlackRock Inc.",           "CUSTOMER", "LO",    350e6, 850e6, 0.20),
    ("CUST_VANGRD", "Vanguard Group",           "CUSTOMER", "LO",    420e6, 920e6, 0.15),
    ("CUST_FIDELTY","Fidelity Investments",     "CUSTOMER", "LO",    200e6, 580e6, 0.22),
    ("CUST_PIMCO",  "PIMCO",                    "CUSTOMER", "FI",    500e6, 1.2e9, 0.25),
    ("CUST_BRIDGW", "Bridgewater Associates",   "CUSTOMER", "MACRO", 160e6, 420e6, 0.30),
    ("CUST_BAUPOS", "Baupost Group",            "CUSTOMER", "LO",     80e6, 210e6, 0.18),
    ("CUST_VIKING", "Viking Global Investors",  "CUSTOMER", "LO",    110e6, 290e6, 0.20),
    ("CUST_LONEP",  "Lone Pine Capital",        "CUSTOMER", "LO",     90e6, 250e6, 0.20),
    ("CUST_TIGER",  "Tiger Global Management",  "CUSTOMER", "LO",     60e6, 180e6, 0.25),
    ("CUST_COATUE", "Coatue Management",        "CUSTOMER", "LO",     70e6, 195e6, 0.22),
]


# ── BSM Greeks ───────────────────────────────────────────────────────────────

def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)

def _bsm_greeks(S: float, K: float, T: float, sigma: float = 0.25,
                r: float = 0.05, option_type: str = "C"):
    """Return (delta, gamma, vega, theta_per_day) or zeros on bad input."""
    if T <= 0 or S <= 0 or K <= 0:
        return 0.0, 0.0, 0.0, 0.0
    sqrt_T = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T
    npd1 = _norm_pdf(d1)
    if option_type == "C":
        delta = _norm_cdf(d1)
        theta = ((-S * npd1 * sigma / (2.0 * sqrt_T)
                  - r * K * math.exp(-r * T) * _norm_cdf(d2)) / 365.0)
    else:
        delta = _norm_cdf(d1) - 1.0
        theta = ((-S * npd1 * sigma / (2.0 * sqrt_T)
                  + r * K * math.exp(-r * T) * _norm_cdf(-d2)) / 365.0)
    gamma = npd1 / (S * sigma * sqrt_T)
    vega  = S * npd1 * sqrt_T / 100.0   # per 1% change in IV
    return delta, gamma, vega, theta

# Spot prices for each option's underlying
_OPTION_SPOT = {
    "SPX260320P0": 5400.0,   # SPX index
    "SPX260619C0": 5400.0,
    "AAPL26620P0":  226.50,
    "NVDA26320C0":  138.50,
    "QQQ261218P0":  508.30,
    "TSLA26620P0":  285.60,
    "META26620C0":  655.20,
    "GS26919C00":   582.30,
}

# ── Securities CSV ────────────────────────────────────────────────────────────

def _make_securities() -> List[dict]:
    rows = []

    def _add(cusip, desc, stype, price, mat_years=None, coupon=None, rating=None,
             asset_class=None, strike=None):
        if asset_class is None:
            if stype in ("EQUITY_LISTED", "ETF"):
                asset_class = "equity"
            elif stype == "OPTION":
                asset_class = "derivative"
            else:
                asset_class = "fixed_income"
        maturity_date = _future_date(mat_years).isoformat() if mat_years else ""
        delta = gamma = vega = theta = ""
        if stype == "OPTION" and strike is not None and mat_years is not None:
            S = _OPTION_SPOT.get(cusip, price * 10)
            K = float(strike)
            T = float(mat_years)
            otype = "P" if "Put" in desc else "C"
            d, g, v, th = _bsm_greeks(S, K, T, option_type=otype)
            delta, gamma, vega, theta = round(d, 6), round(g, 8), round(v, 6), round(th, 6)
        rows.append({
            "cusip": cusip, "description": desc, "security_type": stype,
            "asset_class": asset_class, "maturity_date": maturity_date,
            "coupon": coupon or "", "rating": rating or "",
            "price": price, "currency": "USD",
            "delta": delta, "gamma": gamma, "vega": vega, "theta": theta,
        })

    for (c, d, t, p) in EQUITY_UNIVERSE:
        _add(c, d, t, p)
    for (c, d, t, p) in ETF_UNIVERSE:
        _add(c, d, t, p)
    for (c, d, t, m, p, cpn, rat) in UST_UNIVERSE:
        _add(c, d, t, p, mat_years=m, coupon=cpn, rating=rat)
    for (c, d, t, m, p, cpn, rat) in AGENCY_UNIVERSE:
        _add(c, d, t, p, mat_years=m, coupon=cpn, rating=rat)
    for (c, d, t, m, p, cpn, rat) in MUNI_UNIVERSE:
        _add(c, d, t, p, mat_years=m, coupon=cpn, rating=rat)
    for (c, d, t, m, p, cpn, rat) in CORP_IG_UNIVERSE:
        _add(c, d, t, p, mat_years=m, coupon=cpn, rating=rat)
    for (c, d, t, m, p, cpn, rat) in CORP_HY_UNIVERSE:
        _add(c, d, t, p, mat_years=m, coupon=cpn, rating=rat)
    for (c, d, t, m, p, cpn, rat) in MBS_UNIVERSE:
        _add(c, d, t, p, mat_years=m, coupon=cpn, rating=rat)
    for (c, d, t, m, p, k) in OPTIONS_UNIVERSE:
        _add(c, d, t, p, mat_years=m, rating=None, strike=k)

    # Also add firm MM + repo collateral placeholders for firm accounts
    for (c, d, t, m, p, cpn, rat) in UST_UNIVERSE:
        pass  # already added above
    for (c, d, t, m, p, cpn, rat) in AGENCY_UNIVERSE:
        pass

    return rows


# ── Accounts CSV ──────────────────────────────────────────────────────────────

def _make_accounts(firms: List[tuple], positions_by_firm: dict) -> List[dict]:
    rows = []

    for (aid, cname, atype, style, lmv_min, lmv_max, mg_pct) in firms:
        pos = positions_by_firm.get(aid, [])
        lmv = sum(p["market_value"] for p in pos if p["side"] == "LONG")
        smv = sum(p["market_value"] for p in pos if p["side"] == "SHORT")

        if style == "LO":
            # Long-only mutual funds / asset managers: no margin borrowing.
            # They hold substantial free cash (dividends received, unsettled proceeds,
            # cash awaiting reinvestment) — these become 15c3-3 credit items.
            is_margin = False
            margin_debit = 0.0
            cash = round(lmv * random.uniform(0.08, 0.15), 2)
        elif style == "FI":
            # Fixed-income managers use modest leverage (repo financing, not margin)
            is_margin = True
            margin_debit = round(lmv * 0.12 * random.uniform(0.85, 1.15), 2)
            cash = round(lmv * random.uniform(0.04, 0.08), 2)
        else:
            # HF / MACRO: actively use margin — small free cash, large debit balances
            is_margin = True
            margin_debit = round(lmv * mg_pct * random.uniform(0.85, 1.15), 2)
            cash = round(random.uniform(-50_000, 200_000), 2)

        rows.append({
            "account_id":         aid,
            "client_name":        cname,
            "account_type":       atype,
            "business_line":      "PRIME_BROKERAGE",
            "cash_balance":       cash,
            "margin_debit":       margin_debit,
            "short_market_value": round(smv, 2),
            "long_market_value":  round(lmv, 2),
            "is_margin_account":  is_margin,
            "is_prime_brokerage": True,
        })

    # Firm accounts
    for (aid, atype, bline) in [
        ("FIRM_MM_EQ",   "FIRM", "MARKET_MAKING"),
        ("FIRM_MM_FI",   "FIRM", "INST_FIXED_INCOME"),
        ("FIRM_REPO",    "FIRM", "REPO"),
        ("FIRM_INST_EQ", "FIRM", "INSTITUTIONAL_EQUITY"),
    ]:
        rows.append({
            "account_id":         aid,
            "client_name":        f"Acme Securities — {bline.replace('_',' ').title()}",
            "account_type":       atype,
            "business_line":      bline,
            "cash_balance":       0,
            "margin_debit":       0,
            "short_market_value": 0,
            "long_market_value":  0,
            "is_margin_account":  False,
            "is_prime_brokerage": False,
        })

    return rows


# ── Positions CSV ─────────────────────────────────────────────────────────────

def _make_positions_for_firms(firms: List[tuple], securities: List[dict]) -> dict:
    """Returns {account_id: [position_dict, ...]}"""

    sec_map = {s["cusip"]: s for s in securities}

    eq_cusips  = [s["cusip"] for s in securities if s["security_type"] == "EQUITY_LISTED"]
    etf_cusips = [s["cusip"] for s in securities if s["security_type"] == "ETF"]
    ust_cusips = [s["cusip"] for s in securities if s["security_type"] == "US_TREASURY"]
    agy_cusips = [s["cusip"] for s in securities if s["security_type"] == "AGENCY"]
    mbs_cusips = [s["cusip"] for s in securities if s["security_type"] == "MBS"]
    ig_cusips  = [s["cusip"] for s in securities if s["security_type"] == "CORP_IG"]
    hy_cusips  = [s["cusip"] for s in securities if s["security_type"] == "CORP_HY"]
    opt_cusips = [s["cusip"] for s in securities if s["security_type"] == "OPTION"]
    muni_cusips= [s["cusip"] for s in securities if s["security_type"] == "MUNICIPAL"]

    all_positions: dict = {}
    pos_id = 1

    def _pos(account_id, cusip, side, quantity, bline):
        nonlocal pos_id
        s = sec_map[cusip]
        price = float(s["price"])
        stype = s["security_type"]
        # Bond: face value × price/100; Equity: shares × price; Option: contracts × 100 × premium
        if stype in ("EQUITY_LISTED", "ETF", "OPTION"):
            mv = abs(quantity) * price * (100 if stype == "OPTION" else 1)
        else:
            mv = abs(quantity) * (price / 100.0)  # face × price%
        p = {
            "position_id":  f"POS_{pos_id:06d}",
            "account_id":   account_id,
            "cusip":        cusip,
            "side":         side,
            "quantity":     round(quantity, 0),
            "market_value": round(mv, 2),
            "cost_basis":   round(mv * random.uniform(0.88, 1.08), 2),
            "business_line": bline,
            "as_of_date":   CALC_DATE.isoformat(),
        }
        pos_id += 1
        return p

    for (aid, cname, atype, style, lmv_min, lmv_max, mg_pct) in firms:
        target_lmv = random.uniform(lmv_min, lmv_max)
        positions = []
        remaining = target_lmv

        if style == "FI":
            # PIMCO-style: 60% UST, 20% Agency, 10% IG, 5% MBS, 5% Muni
            allocations = [
                (ust_cusips,  0.55, "LONG",  1e7, 5e7),
                (agy_cusips,  0.20, "LONG",  5e6, 2e7),
                (ig_cusips,   0.12, "LONG",  2e6, 1e7),
                (mbs_cusips,  0.08, "LONG",  5e6, 2e7),
                (muni_cusips, 0.05, "LONG",  2e6, 8e6),
            ]
            for (pool, alloc_pct, side, min_pos, max_pos) in allocations:
                alloc_amt = target_lmv * alloc_pct
                cusip_sample = random.sample(pool, min(len(pool), random.randint(3, len(pool))))
                per_pos = alloc_amt / len(cusip_sample)
                for cusip in cusip_sample:
                    face = round(per_pos / (float(sec_map[cusip]["price"]) / 100), -3)
                    positions.append(_pos(aid, cusip, side, max(face, 1_000_000), "INST_FIXED_INCOME"))

        elif style == "MACRO":
            # Bridgewater: mix equity + FI + some hedges
            eq_alloc = target_lmv * 0.40
            fi_alloc = target_lmv * 0.45
            hedge_alloc = target_lmv * 0.15

            for cusip in random.sample(eq_cusips, 6):
                qty = round(eq_alloc / 6 / float(sec_map[cusip]["price"]), 0)
                positions.append(_pos(aid, cusip, "LONG", max(qty, 100), "INSTITUTIONAL_EQUITY"))
            for cusip in random.sample(ust_cusips + agy_cusips, 5):
                face = round(fi_alloc / 5 / (float(sec_map[cusip]["price"]) / 100), -3)
                positions.append(_pos(aid, cusip, "LONG", max(face, 1_000_000), "INST_FIXED_INCOME"))
            for cusip in random.sample(etf_cusips, 2):
                qty = round(hedge_alloc / 2 / float(sec_map[cusip]["price"]), 0)
                positions.append(_pos(aid, cusip, "SHORT", max(qty, 100), "PRIME_BROKERAGE"))

        elif style == "HF":
            # Hedge fund: long equity + short equity + options
            long_alloc  = target_lmv * 0.60
            short_alloc = target_lmv * 0.30
            opt_alloc   = target_lmv * 0.10

            num_longs = random.randint(6, 12)
            for cusip in random.sample(eq_cusips + etf_cusips, num_longs):
                qty = round(long_alloc / num_longs / float(sec_map[cusip]["price"]), 0)
                positions.append(_pos(aid, cusip, "LONG", max(qty, 100), "PRIME_BROKERAGE"))

            num_shorts = random.randint(3, 8)
            for cusip in random.sample(eq_cusips + etf_cusips, num_shorts):
                qty = round(short_alloc / num_shorts / float(sec_map[cusip]["price"]), 0)
                positions.append(_pos(aid, cusip, "SHORT", max(qty, 100), "PRIME_BROKERAGE"))

            for cusip in random.sample(opt_cusips, random.randint(2, 4)):
                premium = float(sec_map[cusip]["price"])
                contracts = max(round(opt_alloc / len(opt_cusips) / (premium * 100), 0), 10)
                side = random.choice(["LONG", "SHORT"])
                positions.append(_pos(aid, cusip, side, contracts, "PRIME_BROKERAGE"))

        else:  # LO — long-only equity
            num_pos = random.randint(8, 15)
            pool = random.sample(eq_cusips + etf_cusips, num_pos)
            weights = [random.uniform(0.05, 0.20) for _ in pool]
            total_w = sum(weights)
            for cusip, w in zip(pool, weights):
                alloc = target_lmv * (w / total_w)
                qty = round(alloc / float(sec_map[cusip]["price"]), 0)
                positions.append(_pos(aid, cusip, "LONG", max(qty, 100), "PRIME_BROKERAGE"))

        all_positions[aid] = positions

    # ── Firm Market Making + Institutional positions ───────────────────────────
    firm_pos = []

    # MM Equity: mixed long/short large-cap
    for cusip in random.sample(eq_cusips + etf_cusips, 20):
        side = random.choice(["LONG", "SHORT"])
        qty = random.uniform(5_000, 80_000)
        firm_pos.append(_pos("FIRM_MM_EQ", cusip, side, qty, "MARKET_MAKING"))

    # MM Fixed Income: corp bonds inventory
    for cusip in random.sample(ig_cusips + hy_cusips, min(15, len(ig_cusips + hy_cusips))):
        side = random.choice(["LONG", "SHORT"])
        face = random.uniform(2_000_000, 15_000_000)
        firm_pos.append(_pos("FIRM_MM_FI", cusip, side, face, "MARKET_MAKING"))

    # Institutional FI: treasuries + agencies
    for cusip in ust_cusips + agy_cusips + mbs_cusips:
        face = random.uniform(5_000_000, 30_000_000)
        firm_pos.append(_pos("FIRM_INST_EQ", cusip, "LONG", face, "INST_FIXED_INCOME"))

    for account_id in ["FIRM_MM_EQ", "FIRM_MM_FI", "FIRM_INST_EQ"]:
        all_positions[account_id] = [p for p in firm_pos if p["account_id"] == account_id]

    return all_positions


def _make_repo_positions(securities: List[dict]) -> List[dict]:
    gov_secs = [s for s in securities if s["security_type"] in ("US_TREASURY", "AGENCY")]
    counterparties = [
        "Goldman Sachs & Co.", "Morgan Stanley", "JPMorgan Chase", "Citibank N.A.",
        "Deutsche Bank AG", "BNP Paribas", "HSBC Securities", "Barclays Capital",
        "Credit Suisse", "UBS Securities",
    ]
    rows = []
    for i in range(40):
        direction = "REPO" if i < 20 else "REVERSE"
        s = random.choice(gov_secs)
        coll_mv = round(random.uniform(10_000_000, 100_000_000), 2)
        cash = round(coll_mv * 0.98, 2)
        term_days = random.choice([1, 7, 14, 30, 90])
        rows.append({
            "repo_id":                  f"REPO_{i+1:04d}",
            "direction":                direction,
            "collateral_cusip":         s["cusip"],
            "collateral_market_value":  coll_mv,
            "collateral_type":          s["security_type"],
            "cash_amount":              cash,
            "rate":                     round(random.uniform(0.040, 0.055), 4),
            "start_date":               CALC_DATE.isoformat(),
            "end_date":                 (CALC_DATE + timedelta(days=term_days)).isoformat(),
            "counterparty":             random.choice(counterparties),
            "account_type":             random.choice(["CUSTOMER", "FIRM"]),
        })
    return rows


def _make_firm_balance_sheet() -> List[dict]:
    return [{"item": k, "value": v} for k, v in {
        "stockholders_equity":          config.STOCKHOLDERS_EQUITY,
        "allowable_subordinated_debt":  config.ALLOWABLE_SUBORDINATED_DEBT,
        **config.NON_ALLOWABLE_ASSETS,
    }.items()]


def _make_fail_positions(securities: List[dict], firms: List[tuple]) -> List[dict]:
    """
    Simulate realistic settlement fails across business lines.
    Equity/ETF fails are most common; FI fails are larger in notional.
    Aging spans T+1 through T+13+ to show the full Reg SHO picture.
    """
    eq_cusips  = [s["cusip"] for s in securities if s["security_type"] in ("EQUITY_LISTED", "ETF")]
    fi_cusips  = [s["cusip"] for s in securities
                  if s["security_type"] in ("US_TREASURY", "AGENCY", "CORP_IG", "CORP_HY", "MUNICIPAL")]
    sec_map    = {s["cusip"]: s for s in securities}
    accounts   = [(aid, atype) for (aid, _, atype, *_) in firms]
    contra_pts = [
        "Goldman Sachs & Co.", "Morgan Stanley", "JPMorgan Chase",
        "Citibank N.A.", "BNP Paribas", "Barclays Capital",
        "Deutsche Bank AG", "UBS Securities",
    ]
    reasons_eq = ["LATE_DELIVERY", "WRONG_CERT", "LOCATE_FAILURE",
                  "TRANSFER_AGENT_DELAY", "PARTIAL_FILL"]
    reasons_fi = ["LATE_DELIVERY", "WIRE_FAILURE", "WRONG_DENOMINATION",
                  "PARTIAL_FILL", "SYSTEM_ERROR"]

    rows = []
    fail_id = 1

    # Equity fails: 25 records, mix of FTR/FTD, various aging
    aging_days = [1, 1, 2, 2, 3, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16,
                  3, 4, 5, 1, 2, 3, 4, 7, 13, 15]
    for i, days in enumerate(aging_days):
        cusip = random.choice(eq_cusips)
        sec   = sec_map[cusip]
        direction = random.choice(["FTR", "FTD"])
        qty   = random.randint(100, 20_000)
        mv    = round(qty * float(sec["price"]), 2)
        settle_date = CALC_DATE - timedelta(days=days)
        trade_date  = settle_date - timedelta(days=2)  # T+2 settlement
        acct_id, acct_type = random.choice(
            [(a, t) for a, t in accounts if t in ("CUSTOMER", "PAB")]
        )
        rows.append({
            "fail_id":       f"FAIL_{fail_id:04d}",
            "account_id":    acct_id,
            "cusip":         cusip,
            "direction":     direction,
            "trade_date":    trade_date.isoformat(),
            "settle_date":   settle_date.isoformat(),
            "quantity":      qty,
            "market_value":  mv,
            "contra_party":  random.choice(contra_pts),
            "reason":        random.choice(reasons_eq),
            "business_line": random.choice(["PRIME_BROKERAGE", "MARKET_MAKING",
                                            "INSTITUTIONAL_EQUITY"]),
        })
        fail_id += 1

    # Fixed income fails: 15 records, larger notional
    fi_aging = [1, 2, 3, 4, 5, 3, 6, 8, 2, 1, 4, 7, 3, 2, 5]
    for i, days in enumerate(fi_aging):
        cusip = random.choice(fi_cusips)
        sec   = sec_map[cusip]
        face  = random.choice([1_000_000, 2_000_000, 5_000_000,
                               10_000_000, 25_000_000])
        mv    = round(face * float(sec["price"]) / 100, 2)
        direction   = random.choice(["FTR", "FTD"])
        settle_date = CALC_DATE - timedelta(days=days)
        trade_date  = settle_date - timedelta(days=1)  # T+1 for govts
        rows.append({
            "fail_id":       f"FAIL_{fail_id:04d}",
            "account_id":    random.choice(
                [a for a, t in accounts if t in ("CUSTOMER", "PAB")]
            ),
            "cusip":         cusip,
            "direction":     direction,
            "trade_date":    trade_date.isoformat(),
            "settle_date":   settle_date.isoformat(),
            "quantity":      face,
            "market_value":  mv,
            "contra_party":  random.choice(contra_pts),
            "reason":        random.choice(reasons_fi),
            "business_line": random.choice(["INST_FIXED_INCOME", "REPO",
                                            "MARKET_MAKING"]),
        })
        fail_id += 1

    return rows


# ── Main ──────────────────────────────────────────────────────────────────────

def generate_all() -> None:
    print("Generating mock data...")
    securities = _make_securities()
    positions_by_firm = _make_positions_for_firms(BUYSIDE_FIRMS, securities)
    accounts = _make_accounts(BUYSIDE_FIRMS, positions_by_firm)

    # Flatten all positions
    all_positions = []
    for pos_list in positions_by_firm.values():
        all_positions.extend(pos_list)

    repo_positions = _make_repo_positions(securities)
    firm_bs = _make_firm_balance_sheet()
    fail_positions = _make_fail_positions(securities, BUYSIDE_FIRMS)

    _write_csv(config.SECURITIES_FILE, securities)
    _write_csv(config.ACCOUNTS_FILE, accounts)
    _write_csv(config.POSITIONS_FILE, all_positions)
    _write_csv(config.REPO_POSITIONS_FILE, repo_positions)
    _write_csv(config.FIRM_BALANCE_SHEET_FILE, firm_bs)
    _write_csv(config.FAIL_POSITIONS_FILE, fail_positions)

    print(f"  Securities:     {len(securities):>6,}")
    print(f"  Accounts:       {len(accounts):>6,}")
    print(f"  Positions:      {len(all_positions):>6,}")
    print(f"  Repo Positions: {len(repo_positions):>6,}")
    print(f"  Fail Positions: {len(fail_positions):>6,}")
    print("Mock data written to data/csv/")


if __name__ == "__main__":
    generate_all()
