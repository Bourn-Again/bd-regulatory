"""
Broker-Dealer Regulatory Calculator — Professional Dashboard
Run: streamlit run app.py --server.port 8502
"""
import html as _html
import os
import random
import math
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="BD Regulatory | Acme Securities",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset chrome ────────────────────────────────────────────────── */
#MainMenu, footer, header { display: none !important; }
section[data-testid="stSidebar"],
[data-testid="collapsedControl"]     { display: none !important; }
.stDeployButton                      { display: none !important; }

/* ── Global ──────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    letter-spacing: -0.01em;
}
.main > div { background: #070c18 !important; }
.main .block-container {
    padding: 0 2.5rem 3rem !important;
    max-width: 100% !important;
}

/* ── Tab nav → professional navbar ──────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #060a12 !important;
    border-bottom: 1px solid #182035 !important;
    padding: 0 0 0 0 !important;
    margin: 0 -2.5rem 2rem !important;
    padding-left: 2.5rem !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px !important;
    color: #4a6585 !important;
    font-size: 11.5px !important;
    font-weight: 600 !important;
    padding: 13px 20px !important;
    letter-spacing: 0.09em !important;
    text-transform: uppercase !important;
    transition: color 0.15s !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #7a9fc0 !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"][data-baseweb="tab"] {
    color: #deeeff !important;
    border-bottom: 2px solid #3b82f6 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"]     { padding: 0 !important; }

/* ── Native Streamlit metrics (fallback) ─────────────────────────── */
[data-testid="metric-container"] {
    background: #0c1525 !important;
    border: 1px solid #182035 !important;
    border-radius: 5px !important;
    padding: 0.9rem 1.1rem !important;
}
[data-testid="stMetricLabel"] p {
    font-size: 10px !important; font-weight: 700 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    color: #4a6585 !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.35rem !important; font-weight: 600 !important;
    color: #deeeff !important; font-variant-numeric: tabular-nums !important;
    letter-spacing: -0.025em !important;
}

/* ── Typography ──────────────────────────────────────────────────── */
h2, h3 { color: #deeeff !important; font-weight: 600 !important; }
p, li   { color: #8ba3c0 !important; }
.stCaption, [data-testid="stCaptionContainer"] p {
    color: #2e4460 !important; font-size: 11px !important;
}

/* ── Dividers ────────────────────────────────────────────────────── */
[data-testid="stDivider"] hr, hr { border-color: #182035 !important; }

/* ── Expanders ───────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #0c1525 !important;
    border: 1px solid #182035 !important;
    border-radius: 5px !important;
}
[data-testid="stExpander"] summary {
    font-size: 11.5px !important; font-weight: 600 !important;
    letter-spacing: 0.06em !important; text-transform: uppercase !important;
    color: #4a6585 !important;
}

/* ── Buttons ─────────────────────────────────────────────────────── */
.stButton > button {
    background: #0c1525 !important; border: 1px solid #243558 !important;
    color: #7a9fc0 !important; font-size: 11px !important;
    font-weight: 600 !important; letter-spacing: 0.06em !important;
    text-transform: uppercase !important; border-radius: 4px !important;
    padding: 0.4rem 1rem !important;
}
.stButton > button:hover {
    background: #162040 !important; border-color: #3b82f6 !important;
    color: #deeeff !important;
}

/* ── Download button ─────────────────────────────────────────────── */
[data-testid="stDownloadButton"] > button {
    background: #0c1b38 !important; border: 1px solid #1e3a6e !important;
    color: #60a5fa !important; font-size: 11px !important;
    font-weight: 600 !important; letter-spacing: 0.06em !important;
    text-transform: uppercase !important; border-radius: 4px !important;
}

/* ── Form inputs ─────────────────────────────────────────────────── */
[data-testid="stForm"] {
    background: #0c1525 !important;
    border: 1px solid #182035 !important;
    border-radius: 6px !important;
    padding: 1.2rem !important;
}
[data-baseweb="select"] > div {
    background: #070c18 !important;
    border-color: #243558 !important;
}
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    background: #070c18 !important;
    border-color: #243558 !important;
    color: #deeeff !important;
    font-family: Inter, sans-serif !important;
    font-variant-numeric: tabular-nums !important;
}
[data-testid="stRadio"] label p {
    font-size: 12px !important; color: #8ba3c0 !important;
}
[data-testid="stCheckbox"] label p { font-size: 12px !important; color: #4a6585 !important; }

/* ── Selectbox labels ────────────────────────────────────────────── */
[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label,
[data-testid="stRadio"] label {
    font-size: 10px !important; font-weight: 700 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    color: #3d5878 !important;
}

/* ── Dataframes ──────────────────────────────────────────────────── */
[data-testid="stDataFrame"] > div {
    border: 1px solid #182035 !important; border-radius: 5px !important;
    overflow: hidden !important;
}

/* ── Scrollbar ───────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #070c18; }
::-webkit-scrollbar-thumb { background: #182035; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #243558; }
"""

DARK = "plotly_dark"

COLORS = {
    "blue":   "#3b82f6",
    "green":  "#10b981",
    "red":    "#ef4444",
    "amber":  "#f59e0b",
    "purple": "#8b5cf6",
    "teal":   "#06b6d4",
    "pink":   "#ec4899",
    "lime":   "#84cc16",
}
PALETTE = list(COLORS.values())

CHART_LAYOUT = dict(
    template=DARK,
    paper_bgcolor="#0c1525",
    plot_bgcolor="#0c1525",
    font=dict(family="Inter, system-ui, sans-serif", color="#8ba3c0", size=11),
    margin=dict(l=10, r=10, t=24, b=10),
    xaxis=dict(gridcolor="#182035", linecolor="#182035", zerolinecolor="#182035"),
    yaxis=dict(gridcolor="#182035", linecolor="#182035", zerolinecolor="#182035"),
)


# ── HTML component helpers ────────────────────────────────────────────────────

def _kpi(label: str, value: str, sub: str = "", accent: str = "#3b82f6",
         delta: str = "", delta_good: bool = True) -> str:
    delta_html = ""
    if delta:
        dc = COLORS["green"] if delta_good else COLORS["red"]
        delta_html = (f'<div style="font-size:10px;color:{dc};margin-top:0.2rem;'
                      f'font-weight:600;font-variant-numeric:tabular-nums">{delta}</div>')
    return f"""
    <div style="background:#0c1525;border:1px solid #182035;border-top:2px solid {accent};
                border-radius:5px;padding:1rem 1.2rem;min-height:96px">
      <div style="font-size:9.5px;font-weight:700;letter-spacing:0.12em;color:#3d5878;
                  text-transform:uppercase;margin-bottom:0.45rem">{label}</div>
      <div style="font-size:1.4rem;font-weight:600;color:#deeeff;font-variant-numeric:tabular-nums;
                  letter-spacing:-0.025em;line-height:1.15">{value}</div>
      <div style="font-size:11px;color:{accent};margin-top:0.3rem;font-weight:500">{sub}</div>
      {delta_html}
    </div>"""

def _badge(text: str, ok: bool) -> str:
    bg     = "#052e16" if ok else "#2d0a0a"
    color  = "#10b981" if ok else "#ef4444"
    border = "#064e2d" if ok else "#5c1414"
    return (f'<span style="background:{bg};color:{color};border:1px solid {border};'
            f'border-radius:3px;font-size:9.5px;font-weight:700;letter-spacing:0.1em;'
            f'padding:2px 8px;text-transform:uppercase;font-family:Inter,sans-serif">{text}</span>')

def _section(title: str) -> None:
    st.markdown(
        f'<div style="font-size:10px;font-weight:700;letter-spacing:0.13em;color:#2e4460;'
        f'text-transform:uppercase;padding:1.5rem 0 0.6rem;border-bottom:1px solid #182035;'
        f'margin-bottom:0.8rem">{title}</div>',
        unsafe_allow_html=True,
    )

def _kpi_row(items: list) -> None:
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        # item may be 4-tuple (label,value,sub,accent) or 6-tuple with (delta,delta_good)
        if len(item) == 6:
            col.markdown(_kpi(*item), unsafe_allow_html=True)
        else:
            col.markdown(_kpi(*item), unsafe_allow_html=True)

def _html_table(df: pd.DataFrame, col_fmts: dict = None,
                flag_col: str = None, flag_threshold: float = 0) -> None:
    col_fmts = col_fmts or {}

    def _fmt_val(col, val):
        if col in col_fmts and isinstance(val, (int, float)):
            return col_fmts[col].format(val)
        return val

    def _flag_row(row):
        if flag_col and flag_col in row.index:
            v = row[flag_col]
            if isinstance(v, (int, float)) and v > flag_threshold:
                return "background:#1a0808"
        return ""

    headers = "".join(
        f'<th style="background:#080e1c;color:#2e4460;font-size:9.5px;font-weight:700;'
        f'letter-spacing:0.12em;text-transform:uppercase;padding:8px 12px;'
        f'border-bottom:1px solid #182035;white-space:nowrap">{col}</th>'
        for col in df.columns
    )
    rows_html = ""
    for _, row in df.iterrows():
        bg = _flag_row(row)
        cells = ""
        for i, col in enumerate(df.columns):
            align = "left" if i == 0 else "right"
            cells += (
                f'<td style="padding:7px 12px;color:#c4d8ee;border-bottom:1px solid #0f1d32;'
                f'font-variant-numeric:tabular-nums;text-align:{align};font-size:12.5px;'
                f'white-space:nowrap">{_fmt_val(col, row[col])}</td>'
            )
        rows_html += f'<tr style="{bg}">{cells}</tr>'

    st.markdown(
        f'<div style="overflow-x:auto;border:1px solid #182035;border-radius:5px;margin-bottom:1rem">'
        f'<table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif">'
        f'<thead><tr>{headers}</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table></div>',
        unsafe_allow_html=True,
    )

def _chart(fig: go.Figure, height: int = 340) -> None:
    fig.update_layout(height=height, **CHART_LAYOUT)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── App bootstrap ─────────────────────────────────────────────────────────────

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

import config
from data.mock_generator import generate_all
from data.loader import load_book_of_record, load_fail_positions
from calculators.net_capital import NetCapitalCalculator
from calculators.customer_reserve import CustomerReserveCalculator
from calculators.margin import MarginCalculator
from calculators.focus_report import FOCUSReportAssembler
from calculators.scenario import ScenarioTrade, apply_scenario, new_trade_id
from calculators.fails import FailsCalculator
from calculators.clearing_margin import ClearingMarginCalculator
from calculators.stress import StressCalculator


@st.cache_data(show_spinner="Loading regulatory data…")
def run_all():
    if not os.path.exists(config.SECURITIES_FILE):
        generate_all()
    bor    = load_book_of_record()
    nc     = NetCapitalCalculator(bor, config.CALCULATION_DATE).calculate()
    res    = CustomerReserveCalculator(bor, config.CALCULATION_DATE).calculate()
    margin = MarginCalculator(bor, config.CALCULATION_DATE).calculate()
    focus  = FOCUSReportAssembler(bor, nc, res, margin, config.CALCULATION_DATE).assemble()
    fails_data = load_fail_positions()
    fails  = FailsCalculator(bor, fails_data, config.CALCULATION_DATE).calculate()
    cm     = ClearingMarginCalculator(bor, nc.net_capital,
                                       nc.required_net_capital,
                                       config.CALCULATION_DATE).calculate()
    return bor, nc, res, margin, focus, fails, cm


@st.cache_data(show_spinner="Running stress scenarios…")
def run_stress(_bor, _nc, _reserve, _margin):
    return StressCalculator(_bor, _nc, _reserve, _margin).calculate()


@st.cache_data
def _build_trend_figs(hist_key: tuple):
    """Build the 4 metrics-trend figures. Re-runs only when hist_key changes."""
    import pandas as _pd
    hdf = _pd.DataFrame(list(hist_key),
                        columns=["time", "net_capital", "required_nc",
                                 "cushion_pct", "reserve_req", "margin_calls"])
    _cl = {k: v for k, v in CHART_LAYOUT.items() if k != "title"}

    fig_nc = go.Figure()
    fig_nc.add_trace(go.Scatter(
        x=hdf["time"], y=hdf["net_capital"] / 1e6, name="Net Capital",
        line=dict(color=COLORS["blue"], width=2),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.08)",
    ))
    fig_nc.add_trace(go.Scatter(
        x=hdf["time"], y=hdf["required_nc"] / 1e6, name="Required NC",
        line=dict(color=COLORS["red"], width=1.5, dash="dash"),
    ))
    fig_nc.update_layout(
        title=dict(text="Net Capital vs Required ($M)", font=dict(size=11)),
        yaxis_title="$M", **_cl,
    )

    fig_cs = go.Figure()
    fig_cs.add_trace(go.Scatter(
        x=hdf["time"], y=hdf["cushion_pct"], name="Cushion %",
        line=dict(color=COLORS["green"], width=2),
        fill="tozeroy", fillcolor="rgba(16,185,129,0.08)",
    ))
    fig_cs.add_hline(y=5, line_color=COLORS["amber"], line_dash="dash",
                     annotation_text="Early Warning 5%", annotation_font_size=9)
    fig_cs.add_hline(y=2, line_color=COLORS["red"], line_dash="dash",
                     annotation_text="Min 2%", annotation_font_size=9)
    fig_cs.update_layout(
        title=dict(text="NC Cushion % of ADI", font=dict(size=11)),
        yaxis_title="%", **_cl,
    )

    fig_res = go.Figure(go.Scatter(
        x=hdf["time"], y=hdf["reserve_req"] / 1e6, name="Reserve Req",
        line=dict(color=COLORS["purple"], width=2),
        fill="tozeroy", fillcolor="rgba(139,92,246,0.08)",
    ))
    fig_res.update_layout(
        title=dict(text="Customer Reserve Required ($M)", font=dict(size=11)),
        yaxis_title="$M", **_cl,
    )

    fig_mg = go.Figure()
    fig_mg.add_trace(go.Bar(
        x=hdf["time"], y=hdf["margin_calls"] / 1e6,
        name="Margin Calls $M", marker_color=COLORS["amber"],
    ))
    fig_mg.update_layout(
        title=dict(text="Margin Call Amount ($M)", font=dict(size=11)),
        yaxis_title="$M", **_cl,
    )

    return fig_nc, fig_cs, fig_res, fig_mg


# ── Early session state (must exist before header widgets render) ──────────────
if "live_mode" not in st.session_state:
    st.session_state.live_mode = False
if "live_trades" not in st.session_state:
    st.session_state.live_trades = []
if "_live_rc" not in st.session_state:
    st.session_state._live_rc = 0

# ── Page header ───────────────────────────────────────────────────────────────

st.markdown(f"""
<div style="background:#060a12;border-bottom:1px solid #182035;margin:0 -2.5rem 0;
            padding:0.65rem 2.5rem;display:flex;justify-content:space-between;
            align-items:center;margin-top:-1px">
  <div style="display:flex;align-items:center;gap:1.5rem">
    <span style="font-size:13px;font-weight:700;color:#3b82f6;letter-spacing:0.06em">
      {config.FIRM_NAME.upper()}
    </span>
    <span style="font-size:10.5px;color:#2e4460;letter-spacing:0.04em">
      BD-{config.BROKER_DEALER_ID}
    </span>
    <span style="font-size:10.5px;color:#2e4460">
      Period: {config.REPORT_PERIOD}
    </span>
  </div>
  <span style="font-size:10.5px;color:#2e4460;letter-spacing:0.04em">
    As of {config.CALCULATION_DATE.strftime("%d %b %Y")}
  </span>
</div>
""", unsafe_allow_html=True)

col_title, col_live_toggle, col_live_status, col_regen = st.columns([6, 1, 1, 1])
with col_live_toggle:
    _toggle = st.toggle("Live Mode", value=st.session_state.live_mode, key="_live_toggle")
    if _toggle != st.session_state.live_mode:
        st.session_state.live_mode = _toggle
        st.rerun()
with col_live_status:
    if st.session_state.live_mode:
        _n_live = len(st.session_state.live_trades)
        st.markdown(
            f'<div style="padding-top:0.45rem;font-size:9.5px;font-weight:700;'
            f'letter-spacing:0.1em;color:#10b981">● LIVE&nbsp;&nbsp;'
            f'<span style="color:#4a6585">{_n_live} trade{"s" if _n_live!=1 else ""}</span></div>',
            unsafe_allow_html=True,
        )
with col_regen:
    if st.button("↺  Regenerate", use_container_width=True):
        st.cache_data.clear()
        generate_all()
        st.session_state.live_trades    = []
        st.session_state.metrics_history = []
        st.rerun()

# ── Auto-refresh + simulated live trades ──────────────────────────────────────
if st.session_state.live_mode:
    from streamlit_autorefresh import st_autorefresh
    _rc = st_autorefresh(interval=30_000, key="live_autorefresh")
    if _rc != st.session_state._live_rc:
        st.session_state._live_rc = _rc
        # Simulate a small batch of incoming trades each tick
        _eq_pool = [s for s in bor.securities.values()
                    if s.security_type.value in ("EQUITY_LISTED", "ETF", "CORP_IG")]
        _acct_ids = [a.account_id for a in bor.get_customer_accounts()]
        if _eq_pool and _acct_ids:
            import random as _rng
            _batch = []
            for _ in range(_rng.randint(2, 6)):
                _s  = _rng.choice(_eq_pool)
                _a  = _rng.choice(_acct_ids)
                _dir = _rng.choice(["BUY", "SELL"])
                _batch.append(ScenarioTrade(
                    trade_id=new_trade_id(),
                    account_id=_a,
                    client_name=(bor.accounts[_a].client_name if _a in bor.accounts else _a),
                    cusip=_s.cusip,
                    description=f"[Live] {_s.description}",
                    direction=_dir,
                    quantity=float(_rng.randint(100, 50_000) // 100 * 100),
                    price=_s.price * _rng.uniform(0.99, 1.01),
                    security_type=_s.security_type.value,
                    asset_class=_s.asset_class,
                    is_margin=True,
                ))
            st.session_state.live_trades.extend(_batch)
            # Rolling window — prevent unbounded memory growth
            if len(st.session_state.live_trades) > 500:
                st.session_state.live_trades = st.session_state.live_trades[-500:]

bor, nc, reserve, margin, focus, fails, clearing = run_all()

# Merge live feed trades + simulator trades and recompute if anything present.
# The cached baseline is untouched; we shadow the top-level variables.
_all_incoming = (
    st.session_state.get("live_trades", []) +
    st.session_state.get("sim_trades",  [])
)
if _all_incoming:
    bor      = apply_scenario(bor, _all_incoming)
    nc       = NetCapitalCalculator(bor, config.CALCULATION_DATE).calculate()
    reserve  = CustomerReserveCalculator(bor, config.CALCULATION_DATE).calculate()
    margin   = MarginCalculator(bor, config.CALCULATION_DATE).calculate()
    focus    = FOCUSReportAssembler(
                   bor, nc, reserve, margin, config.CALCULATION_DATE
               ).assemble()
    clearing = ClearingMarginCalculator(bor, nc.net_capital,
                                         nc.required_net_capital,
                                         config.CALCULATION_DATE).calculate()

acct_name_map  = {a.account_id: (a.client_name or a.account_id) for a in bor.accounts.values()}
sec_desc_map   = {s.cusip: s.description for s in bor.securities.values()}
cushion        = nc.cushion_pct * 100 if nc.cushion_pct != float("inf") else 0.0

# ── Metrics history (within-session trending) ─────────────────────────────────
from datetime import datetime as _dt
_snap = {
    "time":         _dt.now().strftime("%H:%M:%S"),
    "net_capital":  nc.net_capital,
    "required_nc":  nc.required_net_capital,
    "excess_nc":    nc.excess_net_capital,
    "cushion_pct":  cushion,
    "reserve_req":  reserve.total_reserve_required,
    "margin_calls": margin.total_margin_call_amount,
    "n_calls":      margin.accounts_with_margin_calls,
    "live_trades":  len(st.session_state.get("live_trades", [])),
}
_hist = list(st.session_state.get("metrics_history", []))  # copy; never mutate session state in-place
_last = _hist[-1] if _hist else {}
if _last.get("net_capital") != nc.net_capital or _last.get("live_trades") != _snap["live_trades"]:
    _hist.append(_snap)
    if len(_hist) > 500:
        _hist = _hist[-500:]
    st.session_state.metrics_history = _hist

# ── Session state ─────────────────────────────────────────────────────────────
if "scenario_trades" not in st.session_state:
    st.session_state.scenario_trades = []
if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0
if "sim_running" not in st.session_state:
    st.session_state.sim_running = False
if "sim_trades" not in st.session_state:
    st.session_state.sim_trades = []
if "sim_history" not in st.session_state:
    st.session_state.sim_history = []
if "sim_tick" not in st.session_state:
    st.session_state.sim_tick = 0
if "live_trades" not in st.session_state:
    st.session_state.live_trades = []
if "live_mode" not in st.session_state:
    st.session_state.live_mode = False
if "live_upload_key" not in st.session_state:
    st.session_state.live_upload_key = 0
if "metrics_history" not in st.session_state:
    st.session_state.metrics_history = []
if "_live_rc" not in st.session_state:
    st.session_state._live_rc = 0

# Prior-day baseline — computed once per session from seeded offsets of the cached baseline
if "prior_day" not in st.session_state:
    _rng_pd = random.Random(17)
    _pd_bor, _pd_nc, _pd_res, _pd_mg, *_ = run_all()
    st.session_state.prior_day = {
        "net_capital":    _pd_nc.net_capital     * _rng_pd.uniform(0.93, 1.07),
        "required_nc":    _pd_nc.required_net_capital * _rng_pd.uniform(0.97, 1.03),
        "excess_nc":      _pd_nc.excess_net_capital   * _rng_pd.uniform(0.88, 1.12),
        "reserve_req":    _pd_res.total_reserve_required * _rng_pd.uniform(0.95, 1.05),
        "margin_calls_n": max(0, _pd_mg.accounts_with_margin_calls + _rng_pd.randint(-4, 4)),
        "margin_calls_$": _pd_mg.total_margin_call_amount * _rng_pd.uniform(0.80, 1.20),
        "cushion_pct":    (_pd_nc.cushion_pct * _rng_pd.uniform(0.93, 1.07))
                          if _pd_nc.cushion_pct != float("inf") else 0.0,
    }

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

# ── Simulation banner (visible on every tab when sim is active) ───────────────
if st.session_state.sim_trades or st.session_state.sim_running:
    _n_sim   = len(st.session_state.sim_trades)
    _running = st.session_state.sim_running
    _banner_bg    = "#1a0e00" if _running else "#0d1220"
    _banner_border= COLORS["amber"] if _running else "#2e4460"
    _banner_color = COLORS["amber"] if _running else "#4a6585"
    _dot          = "●" if _running else "◼"
    _status_txt   = "SIMULATION ACTIVE" if _running else "SIMULATION PAUSED"
    st.markdown(
        f'<div style="background:{_banner_bg};border:1px solid {_banner_border};'
        f'border-radius:4px;padding:0.45rem 1rem;margin-bottom:0.5rem;'
        f'display:flex;align-items:center;gap:1rem;font-family:Inter,sans-serif">'
        f'<span style="color:{_banner_color};font-size:10px;font-weight:700;'
        f'letter-spacing:0.12em">{_dot} {_status_txt}</span>'
        f'<span style="color:#4a6585;font-size:10px">'
        f'Tick {st.session_state.sim_tick} &nbsp;·&nbsp; '
        f'{_n_sim:,} simulated trades applied &nbsp;·&nbsp; '
        f'All tabs reflect live state</span>'
        f'<span style="margin-left:auto;color:#ef4444;font-size:9.5px;font-weight:700;'
        f'letter-spacing:0.08em">⚠ NOT ACTUAL POSITIONS</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11 = st.tabs([
    "Dashboard",
    "Net Capital  /  15c3-1",
    "Reserve  /  15c3-3",
    "Margin",
    "Options",
    "Repo",
    "Reg SHO",
    "FOCUS  Report",
    "Scenario  Tester",
    "Reg  Reference",
    "Accounts",
])


# ── PDF report generator ──────────────────────────────────────────────────────
def _build_pdf(nc, reserve, margin, clearing, fails, cushion) -> bytes:
    from fpdf import FPDF
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 9, config.FIRM_NAME, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Regulatory Compliance Report  —  Period: {config.REPORT_PERIOD}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"As of {config.CALCULATION_DATE.strftime('%d %b %Y')}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_draw_color(40, 60, 96)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)

    # Compliance status
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Compliance Status", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for label, ok in [
        ("Rule 15c3-1  Net Capital",   nc.is_compliant),
        ("Rule 15c3-1  Early Warning", not nc.is_early_warning),
        ("Rule 15c3-3  Reserve",       reserve.is_compliant),
        ("Reg T / Margin",             margin.accounts_with_margin_calls == 0),
        ("Regulation SHO  Fails",      fails.is_compliant),
    ]:
        pdf.set_text_color(16, 185, 129) if ok else pdf.set_text_color(239, 68, 68)
        pdf.cell(0, 5, f"  {'PASS' if ok else 'FAIL'}  {label}",
                 new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # Key metrics
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Key Metrics", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for label, value in [
        ("Net Capital",                  f"${nc.net_capital/1e6:,.2f}M"),
        ("Required Net Capital (2% ADI)", f"${nc.required_net_capital/1e6:,.2f}M"),
        ("Excess / (Deficiency)",         f"${nc.excess_net_capital/1e6:,.2f}M"),
        ("NC Cushion % of ADI",           f"{cushion:.1f}%"),
        ("Aggregate Debit Items",         f"${nc.aggregate_debit_items/1e6:,.1f}M"),
        ("Total Haircuts",                f"${nc.total_haircuts/1e6:,.2f}M"),
        ("Customer Reserve Required",     f"${reserve.total_reserve_required/1e6:,.2f}M"),
        ("Margin Calls — Count",          str(margin.accounts_with_margin_calls)),
        ("Margin Calls — Amount",         f"${margin.total_margin_call_amount/1e6:,.2f}M"),
        ("Clearing Org Margin",           f"${clearing.total_clearing_margin/1e6:,.2f}M"),
    ]:
        pdf.cell(110, 5, f"  {label}", border=0)
        pdf.cell(0, 5, value, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Generated {_dt.now().strftime('%d %b %Y %H:%M:%S')}  —  For internal use only",
             new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

with t1:
    nc_ok   = nc.is_compliant
    ew_ok   = not nc.is_early_warning
    res_ok  = reserve.is_compliant
    mg_ok   = margin.accounts_with_margin_calls == 0
    sho_ok  = fails.is_compliant
    prior   = st.session_state.prior_day   # prior-day snapshot

    # Stress signal (cached — no extra compute cost if already run on t9)
    _dash_stress = run_stress(bor, nc, reserve, margin)
    _worst = min(_dash_stress, key=lambda s: s.shocked_net_capital)

    def _d(cur, prev, higher_better=True, fmt="$", decimals=1):
        """Format a prior-day delta with sign, color hint, and arrow."""
        delta = cur - prev
        good  = (delta >= 0) == higher_better
        arrow = "▲" if delta >= 0 else "▼"
        if fmt == "$":
            s = f"${abs(delta)/1e6:.{decimals}f}M"
        else:
            s = f"{abs(delta):.{decimals}f}%"
        return f"{arrow} {s} vs prior", good

    nc_d,  nc_dg  = _d(nc.net_capital,                  prior["net_capital"])
    req_d, req_dg = _d(nc.required_net_capital,          prior["required_nc"], higher_better=False)
    exc_d, exc_dg = _d(nc.excess_net_capital,            prior["excess_nc"])
    res_d, res_dg = _d(reserve.total_reserve_required,   prior["reserve_req"], higher_better=False)
    mg_d,  mg_dg  = _d(margin.total_margin_call_amount,  prior["margin_calls_$"], higher_better=False)
    cs_d,  cs_dg  = _d(cushion, prior["cushion_pct"], fmt="%")

    # Capital runway: days until minimum NC breach at current daily burn rate
    _nc_daily_change = nc.net_capital - prior["net_capital"]
    if _nc_daily_change < 0:
        _days_to_min = (nc.net_capital - nc.required_net_capital) / abs(_nc_daily_change)
        _days_to_ew  = (nc.net_capital - nc.early_warning_level)  / abs(_nc_daily_change)
        _runway_val  = max(_days_to_min, 0)
        _runway_sub  = (f"EW breach in {max(_days_to_ew,0):.0f}d"
                        if _days_to_ew > 0 else "Already below EW")
        _runway_color = COLORS["red"] if _runway_val < 10 else (
                        COLORS["amber"] if _runway_val < 30 else COLORS["green"])
    else:
        _runway_val   = float("inf")
        _runway_sub   = f"+${_nc_daily_change/1e6:.1f}M/day — improving"
        _runway_color = COLORS["green"]
    _runway_str = f"{_runway_val:.0f} days" if _runway_val != float("inf") else "∞"

    _dash_kpi_items = [
        (_kpi("Net Capital",
              f"${nc.net_capital/1e6:,.1f}M",
              _badge("COMPLIANT" if nc_ok else "NON-COMPLIANT", nc_ok),
              COLORS["green"] if nc_ok else COLORS["red"],
              nc_d, nc_dg), 1),
        (_kpi("Required Net Capital",
              f"${nc.required_net_capital/1e6:,.2f}M",
              f"2% × ${nc.aggregate_debit_items/1e6:,.0f}M ADI",
              COLORS["blue"],
              req_d, req_dg), 1),
        (_kpi("Excess / (Deficiency)",
              f"${nc.excess_net_capital/1e6:,.1f}M",
              f"NC {cushion:.1f}% of ADI",
              COLORS["green"] if nc_ok else COLORS["red"],
              exc_d, exc_dg), 1),
        (_kpi("Capital Runway",
              _runway_str,
              _runway_sub,
              _runway_color), 1),
        (_kpi("Customer Reserve",
              f"${reserve.total_reserve_required/1e6:,.1f}M",
              _badge("FUNDED" if res_ok else "DEFICIENT", res_ok),
              COLORS["green"] if res_ok else COLORS["red"],
              res_d, res_dg), 2),
        (_kpi("Margin Calls",
              str(margin.accounts_with_margin_calls),
              f"${margin.total_margin_call_amount/1e6:,.2f}M total" if margin.accounts_with_margin_calls else "All accounts in compliance",
              COLORS["green"] if mg_ok else COLORS["red"],
              mg_d, mg_dg), 3),
        (_kpi("Clearing Org Margin",
              f"${clearing.total_clearing_margin/1e6:,.1f}M",
              _badge("ECP ACTIVE", False) if clearing.has_ecp_charge else f"{len(clearing.calls)} components",
              COLORS["red"] if clearing.has_ecp_charge else COLORS["amber"]), 3),
        (_kpi("Worst-Case NC  (Stressed)",
              f"${_worst.shocked_net_capital/1e6:,.1f}M",
              _badge("COMPLIANT" if _worst.shocked_is_compliant else "BREACHED", _worst.shocked_is_compliant)
              + f'<span style="font-size:9.5px;color:#4a6585;margin-left:0.4rem">{_worst.name}</span>',
              COLORS["green"] if _worst.shocked_is_compliant else COLORS["red"]), 8),
    ]
    _kpi_font  = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    _kpi_css   = ("* {margin:0;padding:0;box-sizing:border-box}"
                  "html,body {background:#070c18;margin:0;padding:0}")
    _kpi_cards = "".join(
        f'<div style="flex:1;min-width:0;cursor:pointer;transition:filter 0.15s"'
        f' onclick="window.parent.document.querySelectorAll(\'[data-baseweb=tab]\')[{_tab_idx}].click()"'
        f' onmouseover="this.style.filter=\'brightness(1.25)\'"'
        f' onmouseout="this.style.filter=\'brightness(1)\'"'
        f' title="Click to view details">{_kpi_html}</div>'
        for _kpi_html, _tab_idx in _dash_kpi_items
    )
    st.components.v1.html(
        f'<html><head><link href="{_kpi_font}" rel="stylesheet">'
        f'<style>{_kpi_css}</style></head><body>'
        f'<div style="display:flex;gap:0.75rem;width:100%;padding-bottom:4px">{_kpi_cards}</div>'
        f'</body></html>',
        height=140,
        scrolling=False,
    )

    checks = [
        ("15c3-1  Net Capital",    nc_ok),
        ("15c3-1  Early Warning",  ew_ok),
        ("15c3-3  Reserve Funded", res_ok),
        ("Margin  No Open Calls",  mg_ok),
        ("Reg SHO  No Hard Fails", sho_ok),
    ]
    badges = "  ".join(_badge(label, ok) for label, ok in checks)
    all_ok = all(ok for _, ok in checks)
    overall_color = COLORS["green"] if all_ok else COLORS["red"]
    overall_text  = "ALL CHECKS PASSED" if all_ok else f"{sum(1 for _,ok in checks if not ok)} CHECK(S) FAILED"

    st.markdown(
        f'<div style="background:#0c1525;border:1px solid #182035;border-radius:5px;'
        f'padding:0.8rem 1.2rem;margin:1rem 0;display:flex;align-items:center;gap:1.5rem">'
        f'<span style="font-size:10px;font-weight:700;letter-spacing:0.1em;color:{overall_color};'
        f'text-transform:uppercase;flex-shrink:0">{overall_text}</span>'
        f'<div style="display:flex;gap:0.6rem;flex-wrap:wrap">{badges}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Stress Scenario Strip ─────────────────────────────────────────────────
    _section("Stress Scenarios — Post-Shock Net Capital")
    _scols = st.columns(5)
    for _scol, _s in zip(_scols, _dash_stress):
        _s_ok  = _s.shocked_is_compliant
        _s_ew  = _s.shocked_is_early_warning
        _top   = COLORS["red"] if not _s_ok else (COLORS["amber"] if _s_ew else COLORS["green"])
        _bdg   = (_badge("BREACHED", False) if not _s_ok
                  else _badge("EARLY WARN", False) if _s_ew
                  else _badge("OK", True))
        _sign  = "+" if _s.delta_net_capital >= 0 else "−"
        _dcol  = COLORS["green"] if _s.delta_net_capital >= 0 else COLORS["red"]
        _scol.markdown(
            f'<div style="background:#0c1525;border:1px solid #182035;border-top:2px solid {_top};'
            f'border-radius:5px;padding:0.75rem 1rem;min-height:108px">'
            f'<div style="font-size:9px;font-weight:700;letter-spacing:0.1em;color:#3d5878;'
            f'text-transform:uppercase;margin-bottom:0.4rem">{_s.name}</div>'
            f'<div style="font-size:1.25rem;font-weight:600;color:#deeeff;'
            f'font-variant-numeric:tabular-nums">${_s.shocked_net_capital/1e6:,.0f}M</div>'
            f'<div style="font-size:10px;color:{_dcol};font-weight:600;margin-top:0.2rem">'
            f'{_sign}${abs(_s.delta_net_capital)/1e6:.1f}M vs baseline</div>'
            f'<div style="margin-top:0.5rem">{_bdg}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

    # ── Live Feed ─────────────────────────────────────────────────────────────
    _section("Live Trade Feed")
    _lf_col, _lf_info = st.columns([3, 5])

    with _lf_col:
        _live_file = st.file_uploader(
            "Drop a trade CSV to update calculations instantly",
            type=["csv"],
            label_visibility="collapsed",
            key=f"live_upload_{st.session_state.live_upload_key}",
        )
        if _live_file is not None:
            try:
                import pandas as _pd_lf
                _df_lf = _pd_lf.read_csv(_live_file)
                _df_lf.columns = [c.strip().lower() for c in _df_lf.columns]
                _req = {"cusip", "direction", "quantity"}
                if _req - set(_df_lf.columns):
                    st.error(f"Missing columns: {', '.join(sorted(_req - set(_df_lf.columns)))}")
                else:
                    _default_acct = list(bor.accounts.keys())[0] if bor.accounts else ""
                    _parsed_lf = []
                    for _idx, _row in _df_lf.iterrows():
                        try:
                            _cu = str(_row["cusip"]).strip()
                            _di = str(_row["direction"]).strip().upper()
                            if _di not in ("BUY", "SELL"):
                                continue
                            _qt = float(_row["quantity"])
                            _se = bor.securities.get(_cu)
                            try:
                                _pr = float(_row.get("price", ""))
                            except (ValueError, TypeError):
                                _pr = _se.price if _se else 0.0
                            _ac = str(_row.get("account_id", "")).strip()
                            _ac = _ac if _ac and _ac != "nan" else _default_acct
                            _de = str(_row.get("description", "")).strip()
                            _de = (_de if _de and _de != "nan"
                                   else (_se.description if _se else _cu))
                            _mg = str(_row.get("is_margin", "TRUE")).strip().upper() not in ("FALSE","0","NO")
                            _parsed_lf.append(ScenarioTrade(
                                trade_id=new_trade_id(),
                                account_id=_ac,
                                client_name=(bor.accounts[_ac].client_name if _ac in bor.accounts else _ac),
                                cusip=_cu, description=_de, direction=_di,
                                quantity=_qt, price=_pr,
                                security_type=(_se.security_type.value if _se else "EQUITY_LISTED"),
                                asset_class=(_se.asset_class if _se else "equity"),
                                is_margin=_mg,
                            ))
                        except Exception:
                            continue
                    if _parsed_lf:
                        st.session_state.live_trades.extend(_parsed_lf)
                        st.session_state.live_upload_key += 1
                        st.rerun()
            except Exception as _e:
                st.error(f"Could not parse file: {_e}")

    with _lf_info:
        _n_live = len(st.session_state.live_trades)
        _live_mv = sum(t.market_value for t in st.session_state.live_trades)
        _lf_c1, _lf_c2, _lf_c3 = st.columns(3)
        _lf_c1.markdown(
            _kpi("Live Trades Loaded", str(_n_live),
                 "From file upload or simulation",
                 COLORS["green"] if _n_live > 0 else COLORS["blue"]),
            unsafe_allow_html=True,
        )
        _lf_c2.markdown(
            _kpi("Live Trade MV", f"${_live_mv/1e6:,.1f}M",
                 "Aggregate market value", COLORS["blue"]),
            unsafe_allow_html=True,
        )
        _lf_mode_color = COLORS["green"] if st.session_state.live_mode else "#4a6585"
        _lf_c3.markdown(
            _kpi("Feed Mode",
                 "AUTO-REFRESH" if st.session_state.live_mode else "MANUAL",
                 "8s refresh when Live Mode on" if st.session_state.live_mode else "Toggle Live Mode in header",
                 _lf_mode_color),
            unsafe_allow_html=True,
        )
        if _n_live > 0:
            if st.button("✕  Clear Live Trades", use_container_width=True):
                st.session_state.live_trades = []
                st.session_state.metrics_history = []
                st.rerun()

    # ── Metrics Trends ────────────────────────────────────────────────────────
    _hist_data = st.session_state.get("metrics_history", [])
    if len(_hist_data) >= 2:
        _section("Metrics Trends")
        _hist_key = tuple(
            (r["time"], r["net_capital"], r["required_nc"],
             r["cushion_pct"], r["reserve_req"], r["margin_calls"])
            for r in _hist_data
        )
        _fig_nc, _fig_cs, _fig_res, _fig_mg = _build_trend_figs(_hist_key)

        _tr1, _tr2 = st.columns(2)
        with _tr1:
            _chart(_fig_nc, height=260)
        with _tr2:
            _chart(_fig_cs, height=260)

        _tr3, _tr4 = st.columns(2)
        with _tr3:
            _chart(_fig_res, height=260)
        with _tr4:
            _chart(_fig_mg, height=260)

    # ── Exports ───────────────────────────────────────────────────────────────
    _section("Export")
    _ex1, _ex2, _ex3, _ex4 = st.columns(4)

    with _ex1:
        try:
            _pdf_bytes = _build_pdf(nc, reserve, margin, clearing, fails, cushion)
            st.download_button(
                label="⬇  PDF Report",
                data=_pdf_bytes,
                file_name=f"regulatory_report_{config.CALCULATION_DATE}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as _pdf_err:
            st.caption(f"PDF unavailable: {_pdf_err}")

    with _ex2:
        _pos_df = bor.positions_df()
        st.download_button(
            label="⬇  Positions CSV",
            data=_pos_df.to_csv(index=False),
            file_name=f"positions_{config.CALCULATION_DATE}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with _ex3:
        _acct_rows = [
            {
                "account_id":        a.account_id,
                "client_name":       a.client_name,
                "account_type":      a.account_type.value,
                "cash_balance":      a.cash_balance,
                "long_market_value": a.long_market_value,
                "short_market_value":a.short_market_value,
                "margin_debit":      a.margin_debit,
                "net_equity":        a.equity,
            }
            for a in bor.accounts.values()
        ]
        import pandas as _pd_ex
        st.download_button(
            label="⬇  Accounts CSV",
            data=_pd_ex.DataFrame(_acct_rows).to_csv(index=False),
            file_name=f"accounts_{config.CALCULATION_DATE}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with _ex4:
        if _hist_data:
            import pandas as _pd_h
            st.download_button(
                label="⬇  Metrics History CSV",
                data=_pd_h.DataFrame(_hist_data).to_csv(index=False),
                file_name=f"metrics_history_{config.CALCULATION_DATE}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.caption("No history yet — metrics are recorded as the dashboard refreshes.")

    # ── Gauge + Funding Requirements + Concentration ──────────────────────────
    g1, g2, g3, g4 = st.columns([2, 3, 2, 2])

    with g1:
        _section("NC % of ADI — Compliance Gauge")
        _gauge_max = max(20.0, cushion * 1.4)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=cushion,
            delta={"reference": prior["cushion_pct"], "valueformat": ".2f",
                   "suffix": "%", "font": {"size": 11}},
            number={"suffix": "%", "valueformat": ".2f",
                    "font": {"size": 26, "color": "#deeeff"}},
            gauge={
                "axis": {"range": [0, _gauge_max], "ticksuffix": "%",
                         "tickfont": {"size": 9, "color": "#4a6585"},
                         "tickcolor": "#182035"},
                "steps": [
                    {"range": [0, 2],          "color": "#200808"},   # non-compliant
                    {"range": [2, 5],          "color": "#1f1200"},   # early warning
                    {"range": [5, _gauge_max], "color": "#051a0f"},   # compliant
                ],
                "threshold": {"line": {"color": COLORS["amber"], "width": 2},
                               "thickness": 0.8, "value": 5},
                "bar": {"color": COLORS["blue"] if cushion >= 5
                        else COLORS["amber"] if cushion >= 2
                        else COLORS["red"],
                        "thickness": 0.25},
            },
            title={"text": "Required: 2% &nbsp;·&nbsp; Warning: 5%",
                   "font": {"size": 9, "color": "#2e4460"}},
        ))
        fig_gauge.update_layout(
            height=220, margin=dict(l=20, r=20, t=10, b=10),
            paper_bgcolor="#0c1525", font_color="#8ba3c0",
        )
        st.plotly_chart(fig_gauge, use_container_width=True,
                        config={"displayModeBar": False})

    with g2:
        _section("Cash Funding Requirements")
        # Next business day for margin calls (T+1)
        from datetime import timedelta
        _calc = config.CALCULATION_DATE
        _t1 = _calc + timedelta(days=1)
        while _t1.weekday() >= 5:
            _t1 += timedelta(days=1)
        # Next Friday for reserve deposit
        _days_to_fri = (4 - _calc.weekday()) % 7 or 7
        _fri = _calc + timedelta(days=_days_to_fri)

        _mc_cash   = margin.total_margin_call_amount
        _res_cash  = max(0, reserve.total_reserve_required - reserve.current_reserve_deposit)
        _repo_cash = sum(r.variation_margin_call for r in margin.repo_details
                         if not r.is_compliant)
        _total_cash = _mc_cash + _res_cash + _repo_cash

        funding_rows = [
            ("Margin Calls (T+1)",      _mc_cash,   _t1.strftime("%d %b"),  COLORS["red"]),
            ("Reserve Deposit",         _res_cash,  _fri.strftime("%d %b"), COLORS["amber"]),
            ("Repo Variation Margin",   _repo_cash, "Same day",             COLORS["amber"]),
        ]
        rows_html = ""
        for lbl, amt, due, col in funding_rows:
            rows_html += (
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:0.45rem 0.8rem;border-bottom:1px solid #0f1d32">'
                f'<div style="font-size:11.5px;color:#8ba3c0">{lbl}'
                f'<span style="font-size:9.5px;color:#2e4460;margin-left:0.5rem">Due {due}</span></div>'
                f'<div style="font-size:12px;font-weight:600;color:{col};'
                f'font-variant-numeric:tabular-nums">${amt:,.0f}</div></div>'
            )
        rows_html += (
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:0.55rem 0.8rem;border-top:1px solid #182035;margin-top:2px">'
            f'<div style="font-size:11.5px;font-weight:700;color:#deeeff">Total Cash Required</div>'
            f'<div style="font-size:14px;font-weight:700;color:#ef4444;'
            f'font-variant-numeric:tabular-nums">${_total_cash:,.0f}</div></div>'
        )
        st.markdown(
            f'<div style="background:#0c1525;border:1px solid #182035;border-radius:5px;'
            f'overflow:hidden">{rows_html}</div>',
            unsafe_allow_html=True,
        )

    with g3:
        _section("Concentration Risk")
        _total_lmv = sum(a.long_market_value for a in bor.accounts.values()
                         if a.long_market_value > 0)
        _conc_threshold = 0.20   # 20% of total book
        _conc_rows = []
        for acct in sorted(bor.get_customer_accounts() + bor.get_pab_accounts(),
                           key=lambda a: -a.long_market_value):
            if acct.long_market_value <= 0:
                continue
            pct = acct.long_market_value / _total_lmv if _total_lmv else 0
            _conc_rows.append({
                "name": acct.client_name or acct.account_id,
                "lmv":  acct.long_market_value,
                "pct":  pct,
                "breach": pct >= _conc_threshold,
            })
        _conc_rows = _conc_rows[:7]

        conc_html = ""
        for r in _conc_rows:
            bar_w  = min(100, r["pct"] * 100 / _conc_threshold)
            b_col  = COLORS["red"] if r["breach"] else COLORS["blue"]
            flag   = ' <span style="color:#ef4444;font-size:9px;font-weight:700">⚠ CONC</span>' if r["breach"] else ""
            conc_html += (
                f'<div style="padding:0.35rem 0.8rem;border-bottom:1px solid #0f1d32">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:3px">'
                f'<span style="font-size:11px;color:#8ba3c0">{r["name"]}{flag}</span>'
                f'<span style="font-size:11px;color:{b_col};font-weight:600;'
                f'font-variant-numeric:tabular-nums">{r["pct"]*100:.1f}%</span></div>'
                f'<div style="background:#182035;border-radius:2px;height:3px">'
                f'<div style="background:{b_col};width:{bar_w:.0f}%;height:3px;border-radius:2px"></div>'
                f'</div></div>'
            )
        st.markdown(
            f'<div style="background:#0c1525;border:1px solid #182035;border-radius:5px;'
            f'overflow:hidden"><div style="padding:0.4rem 0.8rem;font-size:9.5px;color:#2e4460;'
            f'border-bottom:1px solid #182035;letter-spacing:0.08em">Client LMV &nbsp;·&nbsp; '
            f'bar = % of 20% threshold &nbsp;·&nbsp; ⚠ = breach</div>{conc_html}</div>',
            unsafe_allow_html=True,
        )

    with g4:
        _section("Repo Counterparty Conc.")
        _rcp: dict = {}
        for _rp in bor.repo_positions:
            _rcp[_rp.counterparty] = _rcp.get(_rp.counterparty, 0.0) + _rp.cash_amount
        _rcp_total = sum(_rcp.values()) or 1.0
        _rcp_nc    = nc.net_capital or 1.0
        _rcp_sorted = sorted(_rcp.items(), key=lambda x: -x[1])[:7]
        _conc_nc_threshold = 0.25  # 25% of NC flag

        rcp_html = ""
        for _cp, _cash in _rcp_sorted:
            _pct_nc  = _cash / _rcp_nc
            _pct_bk  = _cash / _rcp_total
            _breach  = _pct_nc >= _conc_nc_threshold
            _rc_col  = COLORS["red"] if _breach else COLORS["teal"]
            _rflag   = ' <span style="color:#ef4444;font-size:9px;font-weight:700">⚠ CONC</span>' if _breach else ""
            _bar_w   = min(100, _pct_nc / _conc_nc_threshold * 100)
            rcp_html += (
                f'<div style="padding:0.35rem 0.8rem;border-bottom:1px solid #0f1d32">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:3px">'
                f'<span style="font-size:10.5px;color:#8ba3c0;overflow:hidden;text-overflow:ellipsis;'
                f'white-space:nowrap;max-width:65%">{_cp.split()[0]}{_rflag}</span>'
                f'<span style="font-size:11px;color:{_rc_col};font-weight:600;'
                f'font-variant-numeric:tabular-nums">{_pct_nc*100:.0f}% NC</span></div>'
                f'<div style="background:#182035;border-radius:2px;height:3px">'
                f'<div style="background:{_rc_col};width:{_bar_w:.0f}%;height:3px;border-radius:2px"></div>'
                f'</div></div>'
            )
        st.markdown(
            f'<div style="background:#0c1525;border:1px solid #182035;border-radius:5px;'
            f'overflow:hidden"><div style="padding:0.4rem 0.8rem;font-size:9.5px;color:#2e4460;'
            f'border-bottom:1px solid #182035;letter-spacing:0.08em">Repo counterparties &nbsp;·&nbsp; '
            f'bar = % of 25% NC limit &nbsp;·&nbsp; ⚠ = breach</div>{rcp_html}</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        _section("Net Capital Waterfall")
        steps = [
            ("Equity",            nc.stockholders_equity,  "absolute"),
            ("+ Sub Debt",        nc.allowable_sub_debt,   "relative"),
            ("− Non-Allowable",  -nc.total_non_allowable,  "relative"),
            ("− Haircuts",       -nc.total_haircuts,        "relative"),
            ("Net Capital",       nc.net_capital,          "total"),
        ]
        fig = go.Figure(go.Waterfall(
            measure=[s[2] for s in steps],
            x=[s[0] for s in steps],
            y=[s[1] for s in steps],
            text=[f"${abs(s[1])/1e6:.1f}M" for s in steps],
            textposition="outside",
            textfont=dict(size=11, color="#8ba3c0"),
            connector={"line": {"color": "#182035", "width": 1}},
            decreasing={"marker": {"color": COLORS["red"], "line": {"width": 0}}},
            increasing={"marker": {"color": COLORS["green"], "line": {"width": 0}}},
            totals={"marker": {"color": COLORS["blue"], "line": {"width": 0}}},
        ))
        fig.add_hline(y=nc.required_net_capital, line_dash="dot",
                      line_color=COLORS["amber"], line_width=1,
                      annotation_text=f"Required {nc.required_net_capital/1e6:.0f}M",
                      annotation_font_size=10, annotation_font_color=COLORS["amber"])
        fig.update_layout(showlegend=False, yaxis=dict(tickprefix="$", tickformat=",.0f"))
        _chart(fig, 340)

    with c2:
        _section("Client Exposure — Long Market Value")
        client_rows = []
        for acct in bor.get_customer_accounts() + bor.get_pab_accounts():
            if acct.long_market_value > 0:
                call_rec = next((r for r in margin.account_details
                                 if r.account_id == acct.account_id), None)
                client_rows.append({
                    "Client":  acct.client_name or acct.account_id,
                    "Type":    acct.account_type.value,
                    "LMV":     acct.long_market_value,
                    "Status":  "Call" if (call_rec and call_rec.has_margin_call) else "OK",
                })
        df_tree = pd.DataFrame(client_rows)
        fig2 = px.treemap(df_tree, path=["Type", "Client"], values="LMV",
                          color="Status",
                          color_discrete_map={"OK": "#0d3326", "Call": "#3d0f0f"})
        fig2.update_traces(
            texttemplate="<b>%{label}</b><br>%{value:$,.0f}",
            textfont_size=11,
            hovertemplate="<b>%{label}</b><br>LMV: %{value:$,.0f}<extra></extra>",
            marker_line_width=0.5, marker_line_color="#182035",
        )
        fig2.update_layout(margin=dict(l=0, r=0, t=24, b=0), paper_bgcolor="#0c1525")
        _chart(fig2, 340)

    c3, c4 = st.columns(2)

    with c3:
        _section("Haircut by Security Type")
        hc_agg = {}
        for h in nc.haircut_details:
            hc_agg.setdefault(h.security_type, [0.0, 0.0])
            hc_agg[h.security_type][0] += h.market_value
            hc_agg[h.security_type][1] += h.haircut_amount
        hc_df = pd.DataFrame([
            {"Type": t, "MV": v[0], "HC": v[1], "Rate": v[1]/v[0]*100 if v[0] else 0}
            for t, v in hc_agg.items()
        ]).sort_values("HC", ascending=True)
        fig3 = go.Figure(go.Bar(
            x=hc_df["HC"], y=hc_df["Type"], orientation="h",
            marker=dict(
                color=hc_df["Rate"],
                colorscale=[[0, "#0c2a4a"], [0.5, "#1d5a9c"], [1, "#ef4444"]],
                showscale=True,
                colorbar=dict(title=dict(text="HC%", font=dict(size=9)),
                              thickness=10, tickfont=dict(size=9), tickcolor="#4a6585"),
            ),
            hovertemplate="<b>%{y}</b><br>Haircut: %{x:$,.0f}<br>Rate: %{marker.color:.1f}%<extra></extra>",
        ))
        fig3.update_layout(xaxis=dict(tickprefix="$", tickformat=",.0f"))
        _chart(fig3, 340)

    with c4:
        _section("Margin Calls by Client")
        calls_list = sorted([r for r in margin.account_details if r.has_margin_call],
                            key=lambda x: -x.margin_call_amount)
        if calls_list:
            df_calls = pd.DataFrame([{
                "Client":   acct_name_map.get(r.account_id, r.account_id),
                "Call ($)": r.margin_call_amount,
                "Type":     r.margin_call_type,
                "LMV":      r.long_market_value,
                "Equity":   r.equity,
            } for r in calls_list])
            fig4 = go.Figure()
            for ctype, color in [("HOUSE", COLORS["red"]), ("MAINTENANCE", COLORS["amber"])]:
                sub = df_calls[df_calls["Type"] == ctype]
                if not sub.empty:
                    fig4.add_trace(go.Bar(
                        x=sub["Call ($)"], y=sub["Client"], orientation="h",
                        name=ctype, marker_color=color, marker_line_width=0,
                        hovertemplate="<b>%{y}</b><br>Call: %{x:$,.0f}<extra></extra>",
                    ))
            fig4.update_layout(barmode="stack",
                               xaxis=dict(tickprefix="$", tickformat=",.0f"),
                               legend=dict(orientation="h", y=1.08, font_size=10))
            _chart(fig4, 340)
        else:
            st.markdown(
                '<div style="height:340px;display:flex;align-items:center;justify-content:center;'
                'background:#0c1525;border:1px solid #182035;border-radius:5px">'
                '<span style="color:#10b981;font-size:13px;font-weight:500;letter-spacing:0.06em">'
                'NO MARGIN CALLS</span></div>', unsafe_allow_html=True)

    st.divider()
    _section("Client Position Summary")
    summary = []
    for acct in sorted(bor.get_customer_accounts() + bor.get_pab_accounts(),
                       key=lambda a: -a.long_market_value):
        c = next((r for r in margin.account_details if r.account_id == acct.account_id), None)
        summary.append({
            "Client":        acct.client_name or acct.account_id,
            "Type":          acct.account_type.value,
            "Long MV":       f"${acct.long_market_value:>14,.0f}",
            "Short MV":      f"${acct.short_market_value:>14,.0f}",
            "Net Exposure":  f"${acct.long_market_value - acct.short_market_value:>14,.0f}",
            "Margin Debit":  f"${acct.margin_debit:>14,.0f}",
            "Equity":        f"${acct.equity:>14,.0f}",
            "House Req.":    f"${c.house_required:>14,.0f}" if c else "—",
            "Excess Equity": f"${c.excess_equity:>14,.0f}" if c else "—",
            "Margin Call":   f"${c.margin_call_amount:>10,.0f}" if (c and c.margin_call_amount) else "—",
            "Call Type":     c.margin_call_type if c else "",
        })
    df_s = pd.DataFrame(summary)

    def _row_style(row):
        if row.get("Call Type", "") in ("HOUSE", "MAINTENANCE"):
            return ["background-color:#160808; color:#ef4444"] * len(row)
        return [""] * len(row)

    st.dataframe(df_s.style.apply(_row_style, axis=1),
                 use_container_width=True, hide_index=True, height=460)


# ══════════════════════════════════════════════════════════════════════════════
# NET CAPITAL
# ══════════════════════════════════════════════════════════════════════════════

with t2:
    _kpi_row([
        ("Net Capital",           f"${nc.net_capital/1e6:,.1f}M",
         _badge("COMPLIANT" if nc.is_compliant else "NON-COMPLIANT", nc.is_compliant),
         COLORS["green"] if nc.is_compliant else COLORS["red"]),
        ("Required  (2% ADI)",    f"${nc.required_net_capital/1e6:,.2f}M", "Alternative Method", COLORS["blue"]),
        ("Excess Net Capital",    f"${nc.excess_net_capital/1e6:,.1f}M",
         _badge("EARLY WARNING", False) if nc.is_early_warning else "Within limits",
         COLORS["green"] if not nc.is_early_warning else COLORS["amber"]),
        ("Aggregate Debit Items", f"${nc.aggregate_debit_items/1e6:,.1f}M", "Customer debit balances", COLORS["teal"]),
        ("NC % of ADI",           f"{cushion:.2f}%", "Min required: 2.00%",
         COLORS["green"] if cushion >= 2 else COLORS["red"]),
        ("Total Haircuts",        f"${nc.total_haircuts/1e6:,.1f}M",
         f"{len(nc.haircut_details):,} positions", COLORS["amber"]),
    ])

    # ── Headroom ──────────────────────────────────────────────────────────────
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    _section("Capital Headroom")
    _hw1, _hw2, _hw3, _hw4 = st.columns(4)
    _to_ew    = nc.net_capital - nc.early_warning_level
    _to_min   = nc.excess_net_capital
    _nc_ratio = (nc.net_capital / nc.required_net_capital
                 if nc.required_net_capital else float("inf"))
    _hc_drag  = (nc.total_haircuts / nc.tentative_net_capital * 100
                 if nc.tentative_net_capital else 0.0)
    _hw1.markdown(_kpi(
        "To Early Warning",
        f"${abs(_to_ew)/1e6:,.1f}M",
        "Above 5% ADI threshold" if _to_ew >= 0 else "BREACH — Below early warning",
        COLORS["green"] if _to_ew >= 0 else COLORS["red"],
    ), unsafe_allow_html=True)
    _hw2.markdown(_kpi(
        "To Non-Compliant",
        f"${abs(_to_min)/1e6:,.1f}M",
        "Above 2% ADI threshold" if _to_min >= 0 else "BREACH — Non-compliant",
        COLORS["green"] if _to_min >= 0 else COLORS["red"],
    ), unsafe_allow_html=True)
    _hw3.markdown(_kpi(
        "NC / Minimum Ratio",
        f"{_nc_ratio:.1f}×" if _nc_ratio != float("inf") else "∞",
        "PAIB distributions suspended above 15×" if _nc_ratio > 15 else "Within distribution limit",
        COLORS["amber"] if _nc_ratio > 15 else COLORS["green"],
    ), unsafe_allow_html=True)
    _hw4.markdown(_kpi(
        "Haircut Drag",
        f"{_hc_drag:.1f}%",
        f"${nc.total_haircuts/1e6:,.1f}M consumed of ${nc.tentative_net_capital/1e6:,.1f}M tentative NC",
        COLORS["amber"] if _hc_drag > 25 else COLORS["blue"],
    ), unsafe_allow_html=True)

    # ── Capital Waterfall ─────────────────────────────────────────────────────
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    _section("Net Capital Waterfall  —  Rule 15c3-1 Computation")
    _na_total = sum(nc.non_allowable_assets.values())
    fig_wf = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "total", "relative", "total", "relative", "total"],
        x=[
            "Stockholders'<br>Equity",
            "+ Sub Debt",
            "= Total Capital",
            "− Non-Allowable<br>Assets",
            "= Tentative NC",
            "− Haircuts",
            "= Net Capital",
        ],
        y=[
            nc.stockholders_equity  / 1e6,
            nc.allowable_sub_debt   / 1e6,
            nc.total_capital        / 1e6,
            -_na_total              / 1e6,
            nc.tentative_net_capital / 1e6,
            -nc.total_haircuts      / 1e6,
            nc.net_capital          / 1e6,
        ],
        text=[
            f"${nc.stockholders_equity/1e6:,.1f}M",
            f"+${nc.allowable_sub_debt/1e6:,.1f}M",
            f"${nc.total_capital/1e6:,.1f}M",
            f"−${_na_total/1e6:,.1f}M",
            f"${nc.tentative_net_capital/1e6:,.1f}M",
            f"−${nc.total_haircuts/1e6:,.1f}M",
            f"${nc.net_capital/1e6:,.1f}M",
        ],
        textposition="outside",
        textfont=dict(size=10, color="#c4d8ee"),
        connector=dict(line=dict(color="#182035", width=1, dash="dot")),
        increasing=dict(marker=dict(color=COLORS["green"], line=dict(width=0))),
        decreasing=dict(marker=dict(color=COLORS["red"],   line=dict(width=0))),
        totals=dict(   marker=dict(color=COLORS["blue"],   line=dict(width=0))),
    ))
    fig_wf.add_hline(
        y=nc.early_warning_level / 1e6,
        line_color=COLORS["amber"], line_dash="dash", line_width=1.5,
        annotation_text=f"Early Warning  ${nc.early_warning_level/1e6:,.1f}M",
        annotation_font_size=9, annotation_font_color=COLORS["amber"],
        annotation_position="bottom right",
    )
    fig_wf.add_hline(
        y=nc.required_net_capital / 1e6,
        line_color=COLORS["red"], line_dash="dash", line_width=1.5,
        annotation_text=f"Required NC  ${nc.required_net_capital/1e6:,.1f}M",
        annotation_font_size=9, annotation_font_color=COLORS["red"],
        annotation_position="top right",
    )
    fig_wf.update_layout(
        yaxis=dict(tickprefix="$", ticksuffix="M", tickformat=",.0f"),
        showlegend=False,
    )
    _chart(fig_wf, height=380)

    st.divider()
    c1, c2 = st.columns([1, 1])

    with c1:
        _section("Capital Computation")
        comp = [
            ("Stockholders' Equity",           nc.stockholders_equity),
            ("+ Allowable Subordinated Debt",  nc.allowable_sub_debt),
            ("= Total Capital",                nc.total_capital),
        ]
        for k, v in nc.non_allowable_assets.items():
            comp.append((f"  − {k.replace('_',' ').title()}", -v))
        comp += [
            ("= Tentative Net Capital",        nc.tentative_net_capital),
            ("− Haircuts on Positions",        -nc.total_haircuts),
            ("= Net Capital",                  nc.net_capital),
            ("Required Net Capital (2%)",      -nc.required_net_capital),
            ("Early Warning Level (5%)",       -nc.early_warning_level),
            ("Excess Net Capital",             nc.excess_net_capital),
        ]
        bold_rows = {"= Total Capital", "= Tentative Net Capital", "= Net Capital", "Excess Net Capital"}
        rows_html = ""
        for label, val in comp:
            is_bold = label in bold_rows
            color = "#ef4444" if val < 0 and label not in bold_rows else ("#deeeff" if is_bold else "#8ba3c0")
            weight = "600" if is_bold else "400"
            border_top = "border-top:1px solid #182035;" if is_bold else ""
            rows_html += (
                f'<tr><td style="padding:6px 12px;color:{color};font-weight:{weight};'
                f'font-size:12.5px;{border_top}">{label}</td>'
                f'<td style="padding:6px 12px;text-align:right;color:{color};font-weight:{weight};'
                f'font-size:12.5px;font-variant-numeric:tabular-nums;{border_top}">'
                f'${val:>,.0f}</td></tr>'
            )
        st.markdown(
            f'<div style="border:1px solid #182035;border-radius:5px;overflow:hidden">'
            f'<table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif">'
            f'<thead><tr>'
            f'<th style="background:#080e1c;color:#2e4460;font-size:9.5px;font-weight:700;'
            f'letter-spacing:0.12em;text-transform:uppercase;padding:8px 12px;'
            f'border-bottom:1px solid #182035">Item</th>'
            f'<th style="background:#080e1c;color:#2e4460;font-size:9.5px;font-weight:700;'
            f'letter-spacing:0.12em;text-transform:uppercase;padding:8px 12px;'
            f'border-bottom:1px solid #182035;text-align:right">Amount (USD)</th>'
            f'</tr></thead><tbody>{rows_html}</tbody></table></div>',
            unsafe_allow_html=True,
        )

        # ── Within-tab NC Trend ────────────────────────────────────────────
        _nc_hist = st.session_state.get("metrics_history", [])
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        _section("Net Capital  ·  Session Trend")
        if len(_nc_hist) >= 2:
            _df_trend = pd.DataFrame(_nc_hist)
            fig_nc_trend = go.Figure()
            fig_nc_trend.add_trace(go.Scatter(
                x=_df_trend["time"], y=_df_trend["net_capital"],
                mode="lines+markers", name="Net Capital",
                line=dict(color=COLORS["blue"], width=2),
                marker=dict(size=4),
                hovertemplate="<b>%{x}</b><br>NC: %{y:$,.0f}<extra></extra>",
            ))
            fig_nc_trend.add_trace(go.Scatter(
                x=_df_trend["time"], y=_df_trend["required_nc"],
                mode="lines", name="Required NC",
                line=dict(color=COLORS["red"], width=1.5, dash="dot"),
                hovertemplate="<b>%{x}</b><br>Required: %{y:$,.0f}<extra></extra>",
            ))
            fig_nc_trend.update_layout(
                yaxis=dict(tickprefix="$", tickformat=",.0f"),
                legend=dict(orientation="h", y=1.1, font_size=10),
                margin=dict(t=24, b=8),
            )
            _chart(fig_nc_trend, 200)

            fig_cush_trend = go.Figure(go.Scatter(
                x=_df_trend["time"], y=_df_trend["cushion_pct"],
                mode="lines+markers",
                line=dict(color=COLORS["green"], width=2),
                marker=dict(size=4),
                fill="tozeroy", fillcolor=COLORS["green"] + "22",
                hovertemplate="<b>%{x}</b><br>Cushion: %{y:.1f}%<extra></extra>",
            ))
            fig_cush_trend.add_hline(
                y=5, line_dash="dot", line_color=COLORS["amber"],
                annotation_text="Early Warning (5%)", annotation_font_size=9,
                annotation_position="bottom right",
            )
            fig_cush_trend.update_layout(
                yaxis=dict(ticksuffix="%", title=dict(text="Cushion %", font_size=10)),
                margin=dict(t=8, b=8),
            )
            _chart(fig_cush_trend, 160)
        else:
            st.markdown(
                '<div style="padding:10px 14px;border:1px solid #182035;border-radius:5px;'
                'color:#2e4460;font-size:11px;font-family:Inter,sans-serif;text-align:center">'
                'Trend builds after 2+ snapshots — toggle Live Mode or regenerate to accumulate history.</div>',
                unsafe_allow_html=True,
            )

    with c2:
        _section("Haircut by Security Type")
        by_type = {}
        for h in nc.haircut_details:
            by_type.setdefault(h.security_type, [0.0, 0.0])
            by_type[h.security_type][0] += h.market_value
            by_type[h.security_type][1] += h.haircut_amount
        df_ht = pd.DataFrame([
            {"Security Type": t, "Market Value": v[0],
             "Haircut ($)": v[1], "Eff. Rate %": v[1]/v[0]*100 if v[0] else 0}
            for t, v in by_type.items()
        ]).sort_values("Haircut ($)", ascending=False)
        _html_table(df_ht, {
            "Market Value": "${:,.0f}", "Haircut ($)": "${:,.0f}", "Eff. Rate %": "{:.2f}%",
        })

        # ── Concentration Flag ─────────────────────────────────────────────
        if not df_ht.empty:
            _total_hc_c2 = df_ht["Haircut ($)"].sum()
            _top_type = df_ht.iloc[0]
            _top_share = _top_type["Haircut ($)"] / _total_hc_c2 * 100 if _total_hc_c2 else 0
            if _top_share >= 60:
                _flag_color, _flag_bg, _flag_label = COLORS["red"], "#1a0a0a", "HIGH CONCENTRATION"
            elif _top_share >= 40:
                _flag_color, _flag_bg, _flag_label = COLORS["amber"], "#1a1000", "ELEVATED CONCENTRATION"
            else:
                _flag_color, _flag_bg, _flag_label = COLORS["green"], "#091a0e", "DIVERSIFIED"
            st.markdown(
                f'<div style="margin-top:0.75rem;border:1px solid {_flag_color}55;border-radius:5px;'
                f'background:{_flag_bg};padding:10px 14px;display:flex;align-items:center;gap:12px">'
                f'<div style="width:8px;height:8px;border-radius:50%;background:{_flag_color};'
                f'flex-shrink:0;box-shadow:0 0 6px {_flag_color}"></div>'
                f'<div><span style="color:{_flag_color};font-size:9.5px;font-weight:700;'
                f'letter-spacing:0.12em;font-family:Inter,sans-serif">{_flag_label}</span>'
                f'<span style="color:#8ba3c0;font-size:11px;font-family:Inter,sans-serif"> — '
                f'<b style="color:#deeeff">{_top_type["Security Type"]}</b> accounts for '
                f'<b style="color:{_flag_color}">{_top_share:.1f}%</b> of total haircuts</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        _section("MV vs Haircut by Type")
        fig_sc = px.scatter(
            df_ht, x="Market Value", y="Haircut ($)",
            size="Eff. Rate %", color="Security Type",
            color_discrete_sequence=PALETTE,
            hover_name="Security Type",
            hover_data={"Eff. Rate %": ":.2f%", "Market Value": ":$,.0f",
                        "Haircut ($)": ":$,.0f", "Security Type": False},
        )
        fig_sc.update_traces(marker_line_width=0)
        fig_sc.update_layout(
            showlegend=True, legend=dict(font_size=10, orientation="h", y=-0.25),
            xaxis=dict(tickprefix="$", tickformat=",.0f"),
            yaxis=dict(tickprefix="$", tickformat=",.0f"),
        )
        _chart(fig_sc, 260)

        # ── Business Line Capital Consumption ─────────────────────────────
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        _section("Business Line Capital Consumption  ·  15c3-1 Haircuts")
        _pos_bline = {p.position_id: p.business_line.value for p in bor.positions}
        _bl_hc: dict = {}
        for h in nc.haircut_details:
            # repo collateral position_ids match repo_id, not position_id
            bl = _pos_bline.get(h.position_id, "REPO")
            _bl_hc[bl] = _bl_hc.get(bl, 0.0) + h.haircut_amount
        _total_hc = sum(_bl_hc.values()) or 1.0
        _bl_sorted = sorted(_bl_hc.items(), key=lambda x: -x[1])

        fig_bl_hc = go.Figure(go.Bar(
            y=[b for b, _ in _bl_sorted],
            x=[v for _, v in _bl_sorted],
            orientation="h",
            marker_color=COLORS["amber"], marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>Haircut: %{x:$,.0f}<extra></extra>",
        ))
        fig_bl_hc.update_layout(
            xaxis=dict(tickprefix="$", tickformat=",.0f"),
            yaxis=dict(autorange="reversed"),
        )
        _chart(fig_bl_hc, 220)

        _bl_rows = [{"Business Line": bl, "Haircut ($)": hc,
                     "% of Haircuts": hc / _total_hc * 100,
                     "% of Net Capital": hc / nc.net_capital * 100 if nc.net_capital else 0}
                    for bl, hc in _bl_sorted]
        _html_table(pd.DataFrame(_bl_rows), {
            "Haircut ($)":      "${:,.0f}",
            "% of Haircuts":    "{:.1f}%",
            "% of Net Capital": "{:.2f}%",
        })

    st.divider()
    _section("Top 25 Positions by Haircut Amount")
    top25 = sorted(nc.haircut_details, key=lambda x: -x.haircut_amount)[:25]
    df_top = pd.DataFrame([{
        "Description": sec_desc_map.get(h.cusip, h.cusip),
        "Type": h.security_type, "MV": h.market_value,
        "HC Rate": h.haircut_pct * 100, "HC ($)": h.haircut_amount,
    } for h in top25])

    fig_bar = go.Figure()
    for i, stype in enumerate(df_top["Type"].unique()):
        sub = df_top[df_top["Type"] == stype]
        fig_bar.add_trace(go.Bar(
            x=sub["HC ($)"], y=sub["Description"], orientation="h",
            name=stype, marker_color=PALETTE[i % len(PALETTE)], marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>Haircut: %{x:$,.0f}<extra></extra>",
        ))
    fig_bar.update_layout(
        barmode="stack",
        xaxis=dict(tickprefix="$", tickformat=",.0f"),
        legend=dict(orientation="h", y=1.04, font_size=10),
        yaxis=dict(tickfont_size=10, autorange="reversed"),
    )
    _chart(fig_bar, 580)

    with st.expander(f"Full Haircut Detail  —  {len(nc.haircut_details):,} positions"):
        all_hc = pd.DataFrame([{
            "Position ID": h.position_id, "CUSIP": h.cusip,
            "Description": sec_desc_map.get(h.cusip, ""),
            "Type": h.security_type, "Market Value": h.market_value,
            "HC Rate (%)": h.haircut_pct * 100, "Haircut ($)": h.haircut_amount,
        } for h in nc.haircut_details])
        st.dataframe(
            all_hc.style
                .format({"Market Value": "${:,.2f}", "HC Rate (%)": "{:.1f}%", "Haircut ($)": "${:,.2f}"})
                .background_gradient(subset=["Haircut ($)"], cmap="Reds"),
            use_container_width=True, hide_index=True, height=480,
        )


# ══════════════════════════════════════════════════════════════════════════════
# RESERVE
# ══════════════════════════════════════════════════════════════════════════════

with t3:
    _kpi_row([
        ("Customer Reserve Req.", f"${reserve.customer.reserve_required/1e6:,.2f}M",
         "15c3-3 Weekly Computation", COLORS["blue"]),
        ("PAB Reserve Req.",      f"${reserve.pab.reserve_required/1e6:,.2f}M",
         "Proprietary Accts of BDs", COLORS["purple"]),
        ("Total Reserve Req.",    f"${reserve.total_reserve_required/1e6:,.2f}M",
         _badge("FUNDED" if reserve.is_compliant else "DEFICIENT", reserve.is_compliant),
         COLORS["green"] if reserve.is_compliant else COLORS["red"]),
        ("Current Deposit",       f"${reserve.current_reserve_deposit/1e6:,.2f}M",
         f"Surplus: ${reserve.reserve_surplus/1e6:,.2f}M" if reserve.is_compliant
         else f"Deficiency: ${reserve.reserve_deficiency/1e6:,.2f}M",
         COLORS["green"] if reserve.is_compliant else COLORS["red"]),
        ("Next Deposit Deadline",
         (lambda d: d.strftime("%d %b %Y"))(
             config.CALCULATION_DATE + __import__("datetime").timedelta(
                 days=(4 - config.CALCULATION_DATE.weekday()) % 7 or 7)),
         "15c3-3: close of next business Friday",
         COLORS["amber"]),
    ])

    st.divider()

    def _fmt_cell(val) -> str:
        """Auto-format a detail cell value."""
        if isinstance(val, float):
            if 0 < abs(val) < 200:   # likely a percentage (Leverage %)
                return f"{val:.1f}%"
            return f"${val:,.0f}"
        return _html.escape(str(val))

    def _accordion_table(side: str, line_items: list, total: float) -> None:
        """
        Render a reserve formula table using native HTML <details>/<summary>
        elements — no JavaScript needed. Each row is a <details> block that
        expands inline when clicked to show the per-account breakdown.
        """
        accent     = "#10b981" if side == "credit" else "#ef4444"
        accent_bg  = "#071a12" if side == "credit" else "#1a0808"
        accent_bdr = "#0d3326" if side == "credit" else "#3d0f0f"
        title      = "Credits" if side == "credit" else "Debits"

        # Inject CSS once (Streamlit deduplicates identical <style> blocks)
        st.markdown("""
        <style>
        .res-details summary { list-style: none; }
        .res-details summary::-webkit-details-marker { display: none; }
        .res-details[open] summary .res-arrow { color: #3b82f6; }
        .res-details[open] summary .res-arrow::before { content: "▼"; }
        .res-details:not([open]) summary .res-arrow::before { content: "▶"; }
        .res-details summary:hover { background: #111d30 !important; }
        </style>""", unsafe_allow_html=True)

        rows_html = ""
        for label, amount, detail in line_items:
            has_det = bool(detail)

            if has_det:
                # Build inner breakdown table
                cols    = list(detail[0].keys())
                th_html = "".join(
                    f'<th style="background:#060d1a;color:#2e4460;font-size:9px;font-weight:700;'
                    f'letter-spacing:0.1em;text-transform:uppercase;padding:5px 10px;'
                    f'white-space:nowrap;border-bottom:1px solid #182035;'
                    f'text-align:{"left" if i==0 else "right"}">{c}</th>'
                    for i, c in enumerate(cols)
                )
                td_rows = ""
                for row in detail:
                    tds = "".join(
                        f'<td style="padding:5px 10px;color:#8ba3c0;font-size:11.5px;'
                        f'font-variant-numeric:tabular-nums;white-space:nowrap;'
                        f'border-bottom:1px solid #0a1525;'
                        f'text-align:{"left" if i==0 else "right"}">'
                        f'{_fmt_cell(row[c])}</td>'
                        for i, c in enumerate(cols)
                    )
                    td_rows += f"<tr>{tds}</tr>"

                inner = (
                    f'<div style="background:#060d1a;border-top:1px solid #0f1d32;'
                    f'max-height:280px;overflow-y:auto">'
                    f'<table style="width:100%;border-collapse:collapse;'
                    f'font-family:Inter,sans-serif">'
                    f'<thead><tr>{th_html}</tr></thead>'
                    f'<tbody>{td_rows}</tbody>'
                    f'</table></div>'
                )

                rows_html += (
                    f'<details class="res-details" style="border-bottom:1px solid #0f1d32">'
                    f'<summary style="display:flex;justify-content:space-between;'
                    f'align-items:center;padding:8px 14px;cursor:pointer;'
                    f'font-family:Inter,sans-serif;user-select:none">'
                    f'<span style="font-size:12.5px;color:#c4d8ee">'
                    f'<span class="res-arrow" style="font-size:9px;margin-right:7px"></span>'
                    f'{label}'
                    f'<span style="color:#2e4460;font-size:10px;margin-left:7px">'
                    f'{len(detail)} rows</span></span>'
                    f'<span style="font-size:12.5px;color:#deeeff;'
                    f'font-variant-numeric:tabular-nums">${amount:,.0f}</span>'
                    f'</summary>'
                    f'{inner}'
                    f'</details>'
                )
            else:
                # Non-expandable row (no detail data)
                rows_html += (
                    f'<div style="display:flex;justify-content:space-between;'
                    f'align-items:center;padding:8px 14px;border-bottom:1px solid #0f1d32;'
                    f'font-family:Inter,sans-serif">'
                    f'<span style="font-size:12.5px;color:#c4d8ee;padding-left:16px">{label}</span>'
                    f'<span style="font-size:12.5px;color:#deeeff;'
                    f'font-variant-numeric:tabular-nums">${amount:,.0f}</span>'
                    f'</div>'
                )

        # Total row
        total_row = (
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:9px 14px;background:{accent_bg};border-top:1px solid {accent_bdr};'
            f'font-family:Inter,sans-serif">'
            f'<span style="font-size:12.5px;font-weight:700;color:{accent}">Total {title}</span>'
            f'<span style="font-size:13px;font-weight:700;color:{accent};'
            f'font-variant-numeric:tabular-nums">${total:,.0f}</span>'
            f'</div>'
        )

        # Column header bar
        header = (
            f'<div style="display:flex;justify-content:space-between;background:#080e1c;'
            f'padding:8px 14px;border-bottom:1px solid #182035;font-family:Inter,sans-serif">'
            f'<span style="color:#2e4460;font-size:9.5px;font-weight:700;'
            f'letter-spacing:0.12em;text-transform:uppercase">Item</span>'
            f'<span style="color:#2e4460;font-size:9.5px;font-weight:700;'
            f'letter-spacing:0.12em;text-transform:uppercase">Amount (USD)</span>'
            f'</div>'
        )

        st.markdown(
            f'<div style="margin-bottom:0.4rem">'
            f'<div style="font-size:10px;font-weight:700;letter-spacing:0.1em;color:{accent};'
            f'text-transform:uppercase;padding-bottom:0.5rem">{title}'
            f'<span style="color:#2e4460;font-weight:400;text-transform:none;font-size:10px;'
            f'margin-left:0.5rem">— click any row to expand</span></div>'
            f'<div style="border:1px solid #182035;border-radius:5px;overflow:hidden">'
            f'{header}{rows_html}{total_row}'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    for label, items in [("Customer Accounts", reserve.customer), ("PAB Accounts", reserve.pab)]:
        _section(label)
        cl, cr = st.columns(2)

        with cl:
            _accordion_table("credit", [
                ("Free Credit Balances",          items.free_credit_balances,          items.detail_free_credits),
                ("Net Credit — Margin Accounts",  items.net_credit_margin_accounts,    items.detail_net_credit_margin),
                ("Amounts Payable — Short Sales", items.amounts_payable_short_sales,   items.detail_short_sales),
                ("Stock Borrowed from Customers", items.stock_borrowed_from_customers, items.detail_stock_borrowed),
                ("Fails to Receive",              items.customer_fails_to_receive,     items.detail_fails_receive),
                ("Accrued Interest Payable",      items.accrued_interest_payable,      items.detail_accrued_interest),
            ], items.total_credits)

        with cr:
            _accordion_table("debit", [
                ("Customer Debit Balances",        items.customer_debit_balances,           items.detail_debit_balances),
                ("Sec. Borrowed — Cover Shorts",   items.securities_borrowed_cover_shorts,  items.detail_sec_borrowed_short),
                ("Cash at Clearing Organizations", items.cash_at_clearing_orgs,             items.detail_cash_clearing),
                ("Securities Loaned to Customers", items.securities_loaned_to_customers,    items.detail_sec_loaned),
                ("Fails to Deliver",               items.customer_fails_to_deliver,         items.detail_fails_deliver),
            ], items.total_debits)

        net = items.total_credits - items.total_debits
        col = COLORS["green"] if items.reserve_required == 0 else COLORS["amber"]
        st.markdown(
            f'<div style="background:#0c1525;border:1px solid #182035;border-radius:4px;'
            f'padding:0.6rem 1rem;font-size:12px;color:#8ba3c0;margin-bottom:1.2rem">'
            f'Net (Credits − Debits): <b style="color:#deeeff;font-variant-numeric:tabular-nums">'
            f'${net:,.2f}</b>&nbsp;&nbsp;→&nbsp;&nbsp;Reserve Required: '
            f'<b style="color:{col};font-variant-numeric:tabular-nums">'
            f'${items.reserve_required:,.2f}</b></div>', unsafe_allow_html=True)

    st.divider()
    _section("Credits vs Debits — Component Breakdown")
    comp_labels = ["Free Credits", "Net Credit (Margin)", "Short Sale Payable",
                   "Stock Borrowed", "Fails to Receive", "Accrued Interest"]
    debit_labels = ["Debit Balances", "Sec. Borrowed (Shorts)", "Clearing Org Cash",
                    "Sec. Loaned", "Fails to Deliver"]
    c_vals  = [reserve.customer.free_credit_balances, reserve.customer.net_credit_margin_accounts,
               reserve.customer.amounts_payable_short_sales, reserve.customer.stock_borrowed_from_customers,
               reserve.customer.customer_fails_to_receive, reserve.customer.accrued_interest_payable]
    d_vals  = [reserve.customer.customer_debit_balances, reserve.customer.securities_borrowed_cover_shorts,
               reserve.customer.cash_at_clearing_orgs, reserve.customer.securities_loaned_to_customers,
               reserve.customer.customer_fails_to_deliver]
    pc_vals = [reserve.pab.free_credit_balances, reserve.pab.net_credit_margin_accounts,
               reserve.pab.amounts_payable_short_sales, reserve.pab.stock_borrowed_from_customers,
               reserve.pab.customer_fails_to_receive, reserve.pab.accrued_interest_payable]
    pd_vals = [reserve.pab.customer_debit_balances, reserve.pab.securities_borrowed_cover_shorts,
               reserve.pab.cash_at_clearing_orgs, reserve.pab.securities_loaned_to_customers,
               reserve.pab.customer_fails_to_deliver]

    fig_res = go.Figure()
    for i, (lbl, c, pc) in enumerate(zip(comp_labels, c_vals, pc_vals)):
        fig_res.add_trace(go.Bar(name=lbl, x=["Customer Credits", "PAB Credits"],
                                  y=[c, pc], marker_color=PALETTE[i], marker_line_width=0))
    for i, (lbl, d, pd_) in enumerate(zip(debit_labels, d_vals, pd_vals)):
        fig_res.add_trace(go.Bar(name=lbl, x=["Customer Debits", "PAB Debits"],
                                  y=[d, pd_], marker_color=PALETTE[(i+6) % len(PALETTE)], marker_line_width=0))
    fig_res.update_layout(barmode="stack", yaxis=dict(tickprefix="$", tickformat=",.0f"),
                          legend=dict(orientation="v", x=1.01, font_size=10, y=1))
    _chart(fig_res, 400)

    st.divider()
    _section("Rule 15c3-3(b)(3) — Rehypothecation Limit")

    rh = reserve.rehypothecation
    _kpi_row([
        ("Customer Debit Balances", f"${rh.customer_debit_balances/1e6:,.1f}M",
         "Aggregate margin loan balances", COLORS["blue"]),
        ("140% Pledging Limit",     f"${rh.limit/1e6:,.1f}M",
         "Max customer securities pledgeable", COLORS["amber"]),
        ("Currently Pledged",       f"${rh.pledged_amount/1e6:,.1f}M",
         f"{rh.utilization_pct:.1f}% of limit utilized",
         COLORS["green"] if rh.is_compliant else COLORS["red"]),
        ("Headroom",                f"${rh.headroom/1e6:,.1f}M",
         _badge("COMPLIANT", True) if rh.is_compliant else _badge("BREACH", False),
         COLORS["green"] if rh.is_compliant else COLORS["red"]),
    ])

    _rh_c1, _rh_c2 = st.columns([3, 2])

    with _rh_c1:
        _section("Pledged Securities Breakdown vs. 140% Limit")
        _rh_labels = ["To Clearing Orgs", "To Repo Desk", "To Stock Loan"]
        _rh_vals   = [rh.pledged_to_clearing_orgs, rh.pledged_as_repo_collateral,
                      rh.pledged_to_stock_loan]
        _rh_colors = [COLORS["blue"], COLORS["teal"], COLORS["purple"]]
        fig_rh = go.Figure(go.Bar(
            x=_rh_labels, y=_rh_vals,
            marker_color=_rh_colors, marker_line_width=0,
            text=[f"${v/1e6:,.1f}M" for v in _rh_vals], textposition="auto",
        ))
        fig_rh.add_hline(y=rh.limit, line_dash="dot", line_color=COLORS["amber"], line_width=1.5,
                         annotation_text=f"140% Limit  ${rh.limit/1e6:,.1f}M",
                         annotation_font_size=10, annotation_font_color=COLORS["amber"],
                         annotation_position="top right")
        fig_rh.update_layout(yaxis=dict(tickprefix="$", tickformat=",.0f"),
                             xaxis_title=None, yaxis_title="Pledged Value ($)")
        _chart(fig_rh, 280)

    with _rh_c2:
        _section("Utilization Detail")
        _rh_rows = [
            {"Usage":              "Pledged to Clearing Orgs",
             "Amount":             rh.pledged_to_clearing_orgs,
             "% of Limit":         rh.pledged_to_clearing_orgs / rh.limit * 100},
            {"Usage":              "Pledged as Repo Collateral",
             "Amount":             rh.pledged_as_repo_collateral,
             "% of Limit":         rh.pledged_as_repo_collateral / rh.limit * 100},
            {"Usage":              "Pledged to Stock Loan",
             "Amount":             rh.pledged_to_stock_loan,
             "% of Limit":         rh.pledged_to_stock_loan / rh.limit * 100},
            {"Usage":              "━━ Total Pledged",
             "Amount":             rh.pledged_amount,
             "% of Limit":         rh.utilization_pct},
            {"Usage":              "140% Limit",
             "Amount":             rh.limit,
             "% of Limit":         100.0},
            {"Usage":              "Headroom",
             "Amount":             rh.headroom,
             "% of Limit":         rh.headroom / rh.limit * 100},
        ]
        df_rh = pd.DataFrame(_rh_rows)
        st.dataframe(df_rh.style.format({"Amount": "${:,.0f}", "% of Limit": "{:.1f}%"}),
                     use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# MARGIN
# ══════════════════════════════════════════════════════════════════════════════

with t4:
    _kpi_row([
        ("Total Accounts",       str(margin.total_accounts), "Margin accounts reviewed", COLORS["blue"]),
        ("Total Long MV",        f"${margin.total_long_mv/1e6:,.0f}M", "All clients", COLORS["teal"]),
        ("Total Equity",         f"${margin.total_equity/1e6:,.0f}M", "LMV − SMV − Debit", COLORS["teal"]),
        ("Margin Calls",         str(margin.accounts_with_margin_calls),
         f"${margin.total_margin_call_amount/1e6:,.2f}M total",
         COLORS["red"] if margin.accounts_with_margin_calls else COLORS["green"]),
    ])

    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        _section("LMV vs Equity — All Clients")
        sc_rows = [{"Client": acct_name_map.get(r.account_id, r.account_id),
                    "Long MV": r.long_market_value, "Equity": r.equity,
                    "Maint.": r.maintenance_required, "Call": r.margin_call_amount,
                    "Status": "Margin Call" if r.has_margin_call else "OK"}
                   for r in margin.account_details]
        df_sc2 = pd.DataFrame(sc_rows)
        fig_sc2 = px.scatter(df_sc2, x="Long MV", y="Equity", color="Status",
                             color_discrete_map={"OK": COLORS["green"], "Margin Call": COLORS["red"]},
                             size="Maint.", size_max=20, hover_name="Client",
                             hover_data={"Long MV": ":$,.0f", "Equity": ":$,.0f",
                                         "Call": ":$,.0f", "Status": True})
        fig_sc2.add_hline(y=0, line_dash="dot", line_color=COLORS["red"], line_width=1,
                          annotation_text="Zero equity", annotation_font_size=10,
                          annotation_font_color=COLORS["red"])
        fig_sc2.update_traces(marker_line_width=0)
        fig_sc2.update_layout(xaxis=dict(tickprefix="$", tickformat=",.0f"),
                              yaxis=dict(tickprefix="$", tickformat=",.0f"),
                              legend=dict(orientation="h", y=1.08, font_size=10))
        _chart(fig_sc2, 360)

    with c2:
        _section("Equity Distribution")
        eq_vals = [r.equity for r in margin.account_details if r.equity > -50e6]
        fig_hist = go.Figure(go.Histogram(
            x=eq_vals, nbinsx=30, marker_color=COLORS["blue"],
            marker_line_width=0, opacity=0.85,
            hovertemplate="Equity range: %{x:$,.0f}<br>Count: %{y}<extra></extra>",
        ))
        fig_hist.add_vline(x=0, line_dash="dot", line_color=COLORS["red"], line_width=1.5,
                           annotation_text="Zero equity", annotation_font_size=10,
                           annotation_font_color=COLORS["red"])
        fig_hist.update_layout(xaxis=dict(tickprefix="$", tickformat=",.0f"), yaxis_title="# Accounts")
        _chart(fig_hist, 360)

    st.divider()
    _section("Account Margin Detail  ·  Click row to expand position-level Reg T")

    # Pre-build position lookup by account
    _pos_by_acct: dict = {}
    for _p in bor.positions:
        _pos_by_acct.setdefault(_p.account_id, []).append(_p)

    show_calls_only = st.checkbox("Show margin call accounts only", value=False)

    def _margin_accordion(results: list, pos_by_acct: dict) -> None:
        GRID = "20px 160px 55px 85px 80px 85px 90px 90px 90px 90px 85px 85px 95px"
        TH   = ("font-size:9px;font-weight:700;letter-spacing:0.09em;color:#2e4460;"
                "text-transform:uppercase;padding:6px 6px;white-space:nowrap")
        TD   = "font-size:11px;padding:6px 6px;white-space:nowrap;overflow:hidden"
        PTH  = ("font-size:9px;font-weight:700;letter-spacing:0.08em;color:#2e4460;"
                "text-transform:uppercase;padding:5px 8px;white-space:nowrap")

        st.markdown(
            '<style>'
            '.mg-det summary{list-style:none;cursor:pointer;}'
            '.mg-det summary::-webkit-details-marker{display:none;}'
            '.mg-det[open] .mg-arr::before{content:"▼";color:#3b82f6;}'
            '.mg-det:not([open]) .mg-arr::before{content:"▶";color:#4a6585;}'
            '.mg-det summary:hover{background:#111d30!important;}'
            '</style>',
            unsafe_allow_html=True,
        )

        # Column header row (plain div — not a <summary>)
        header_html = (
            f'<div style="display:grid;grid-template-columns:{GRID};'
            f'background:#080e1c;border-bottom:2px solid #182035">'
            f'<span style="{TH}"></span>'
            f'<span style="{TH}">Client</span>'
            f'<span style="{TH}">Type</span>'
            f'<span style="{TH};text-align:right">Long MV</span>'
            f'<span style="{TH};text-align:right">Short MV</span>'
            f'<span style="{TH};text-align:right">Debit Bal.</span>'
            f'<span style="{TH};text-align:right">Equity</span>'
            f'<span style="{TH};text-align:right">Reg T Init.</span>'
            f'<span style="{TH};text-align:right">FINRA Maint.</span>'
            f'<span style="{TH};text-align:right">House Req.</span>'
            f'<span style="{TH};text-align:right">Excess Eq.</span>'
            f'<span style="{TH};text-align:right">Buying Pwr</span>'
            f'<span style="{TH};text-align:right">Call</span>'
            f'</div>'
        )

        rows_html = ""
        for r in results:
            client    = _html.escape(acct_name_map.get(r.account_id, r.account_id))
            has_call  = r.has_margin_call
            row_bg    = "background:#1a0808" if has_call else "background:#0c1525"
            eq_color  = "#ef4444" if r.equity < 0 else ("#10b981" if r.equity > r.house_required else "#f59e0b")
            exc_color = "#ef4444" if r.excess_equity <= 0 else "#10b981"
            call_txt  = (
                f'<span style="color:#ef4444;font-weight:700">${r.margin_call_amount:,.0f}'
                f'<br><span style="font-size:9px">{r.margin_call_type}</span></span>'
                if has_call else '<span style="color:#10b981">&#8212;</span>'
            )

            # ── Per-position Reg T detail table (top 20 by MV) ───────────
            positions = sorted(pos_by_acct.get(r.account_id, []),
                               key=lambda p: -p.market_value)[:20]
            pos_th = (
                f'<th style="{PTH};text-align:left">Security</th>'
                f'<th style="{PTH}">CUSIP</th>'
                f'<th style="{PTH};text-align:center">Side</th>'
                f'<th style="{PTH};text-align:right">Qty</th>'
                f'<th style="{PTH};text-align:right">Price</th>'
                f'<th style="{PTH};text-align:right">Mkt Value</th>'
                f'<th style="{PTH};text-align:right;color:#f59e0b">Reg T Init.</th>'
                f'<th style="{PTH};text-align:right">FINRA Maint.</th>'
                f'<th style="{PTH};text-align:right">House Req.</th>'
                f'<th style="{PTH};text-align:right">Margin Equity</th>'
            )
            pos_rows = ""
            for pos in positions:
                sec   = bor.securities.get(pos.cusip)
                desc  = _html.escape(sec.description if sec else pos.cusip)
                price = sec.price if sec else 0.0
                side  = pos.side.value
                mv    = pos.market_value
                if side == "LONG":
                    rt_i, fn_m, hs_r, mg_eq, sc = mv*.50, mv*.25, mv*.30, mv*.50, "#10b981"
                else:
                    rt_i, fn_m, hs_r, mg_eq, sc = mv*1.50, mv*.30, mv*.35, -(mv*.50), "#ef4444"
                eq_c = "#10b981" if mg_eq >= 0 else "#ef4444"
                pos_rows += (
                    f'<tr style="border-bottom:1px solid #070f1c">'
                    f'<td style="padding:4px 8px;color:#8ab4d4;font-size:11px">{desc}</td>'
                    f'<td style="padding:4px 8px;color:#4a6585;font-size:10px;font-family:monospace">{pos.cusip}</td>'
                    f'<td style="padding:4px 8px;text-align:center;color:{sc};font-size:10px;font-weight:700">{side}</td>'
                    f'<td style="padding:4px 8px;text-align:right;color:#8ab4d4;font-size:11px">{pos.quantity:,.0f}</td>'
                    f'<td style="padding:4px 8px;text-align:right;color:#8ab4d4;font-size:11px">${price:,.2f}</td>'
                    f'<td style="padding:4px 8px;text-align:right;color:#c9d8ed;font-size:11px">${mv:,.0f}</td>'
                    f'<td style="padding:4px 8px;text-align:right;color:#f59e0b;font-size:11px">${rt_i:,.0f}</td>'
                    f'<td style="padding:4px 8px;text-align:right;color:#8ab4d4;font-size:11px">${fn_m:,.0f}</td>'
                    f'<td style="padding:4px 8px;text-align:right;color:#6b7fa3;font-size:11px">${hs_r:,.0f}</td>'
                    f'<td style="padding:4px 8px;text-align:right;color:{eq_c};font-size:11px">${mg_eq:,.0f}</td>'
                    f'</tr>'
                )

            legend = ('Reg T&#160;&#8212;&#160;Long:&#160;50%&#160;initial&#160;/&#160;'
                      '25%&#160;FINRA&#160;maint.&#160;/&#160;30%&#160;house&#160;&#160;'
                      '|&#160;&#160;Short:&#160;150%&#160;initial&#160;/&#160;'
                      '30%&#160;FINRA&#160;maint.&#160;/&#160;35%&#160;house')
            pos_section = (
                f'<div style="background:#060d1a;border-top:1px solid #0f1d32;overflow-x:auto">'
                f'<div style="padding:5px 12px;font-size:9px;color:#2e4460;letter-spacing:0.08em;text-transform:uppercase">{legend}</div>'
                f'<table style="width:100%;border-collapse:collapse;min-width:760px">'
                f'<thead><tr style="background:#040810">{pos_th}</tr></thead>'
                f'<tbody>{pos_rows}</tbody>'
                f'</table></div>'
            )

            # display:grid goes directly on <summary> — no <div> wrapper inside
            rows_html += (
                f'<details class="mg-det" style="border-bottom:1px solid #0f1d32">'
                f'<summary style="display:grid;grid-template-columns:{GRID};'
                f'align-items:center;{row_bg};padding:4px 0;list-style:none;outline:none;user-select:none">'
                f'<span class="mg-arr" style="{TD};padding-left:6px"></span>'
                f'<span style="{TD};color:#c9d8ed;font-weight:500">{client}</span>'
                f'<span style="{TD};color:#4a6585;font-size:10px">{r.account_type}</span>'
                f'<span style="{TD};text-align:right;color:#8ab4d4">${r.long_market_value/1e6:,.2f}M</span>'
                f'<span style="{TD};text-align:right;color:#8ab4d4">${r.short_market_value/1e6:,.2f}M</span>'
                f'<span style="{TD};text-align:right;color:#8ab4d4">${r.debit_balance/1e6:,.2f}M</span>'
                f'<span style="{TD};text-align:right;color:{eq_color}">${r.equity/1e6:,.2f}M</span>'
                f'<span style="{TD};text-align:right;color:#f59e0b">${r.reg_t_initial_required/1e6:,.2f}M</span>'
                f'<span style="{TD};text-align:right;color:#8ab4d4">${r.maintenance_required/1e6:,.2f}M</span>'
                f'<span style="{TD};text-align:right;color:#8ab4d4">${r.house_required/1e6:,.2f}M</span>'
                f'<span style="{TD};text-align:right;color:{exc_color}">${r.excess_equity/1e6:,.2f}M</span>'
                f'<span style="{TD};text-align:right;color:#8ab4d4">${r.buying_power/1e6:,.2f}M</span>'
                f'<span style="{TD};text-align:right">{call_txt}</span>'
                f'</summary>'
                f'{pos_section}'
                f'</details>'
            )

        st.markdown(
            f'<div style="border:1px solid #182035;border-radius:5px;overflow:hidden;font-family:Inter,monospace">'
            f'{header_html}{rows_html}</div>',
            unsafe_allow_html=True,
        )

    _mg_results = sorted(margin.account_details, key=lambda x: -x.long_market_value)
    if show_calls_only:
        _mg_results = [r for r in _mg_results if r.has_margin_call]
    _margin_accordion(_mg_results, _pos_by_acct)


# ══════════════════════════════════════════════════════════════════════════════
# OPTIONS
# ══════════════════════════════════════════════════════════════════════════════

with t5:

    # ── Options Book — Greeks Exposure ────────────────────────────────────────
    _section("Options Book — Greeks Exposure")

    _opt_positions = [
        p for p in bor.positions
        if bor.securities.get(p.cusip) and
           bor.securities[p.cusip].security_type.value == "OPTION"
    ]
    if _opt_positions:
        # Aggregate net Greeks (long = +1, short = −1 sign)
        _net_delta = _net_gamma = _net_vega = _net_theta = 0.0
        _opt_rows = []
        for _p in _opt_positions:
            _sec = bor.securities[_p.cusip]
            _sign = 1.0 if _p.side.value == "LONG" else -1.0
            _contracts = _p.quantity
            _d  = (_sec.delta  or 0.0) * _sign * _contracts * 100
            _g  = (_sec.gamma  or 0.0) * _sign * _contracts * 100
            _v  = (_sec.vega   or 0.0) * _sign * _contracts * 100
            _th = (_sec.theta  or 0.0) * _sign * _contracts * 100
            _net_delta += _d
            _net_gamma += _g
            _net_vega  += _v
            _net_theta += _th
            _opt_rows.append({
                "Security":        _sec.description,
                "CUSIP":           _p.cusip,
                "Side":            _p.side.value,
                "Contracts":       int(_contracts),
                "Delta/contract":  round(_sec.delta or 0.0, 4),
                "Net Delta ($eq)": round(_d, 2),
                "Net Gamma":       round(_g, 4),
                "Net Vega":        round(_v, 2),
            })

        _kpi_row([
            ("Net Delta ($-eq)",       f"${_net_delta:,.0f}", "Sum across all options", COLORS["blue"]),
            ("Net Gamma",              f"{_net_gamma:.2f}",   "Δ per 1pt move", COLORS["teal"]),
            ("Net Vega (per 1% IV)",   f"${_net_vega:,.0f}", "IV sensitivity", COLORS["purple"]),
            ("Net Theta (daily)",      f"${_net_theta:,.0f}", "Time decay per day", COLORS["amber"]),
        ])
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        _html_table(pd.DataFrame(_opt_rows), {
            "Net Delta ($eq)": "${:,.0f}",
            "Net Gamma":       "{:.4f}",
            "Net Vega":        "${:,.0f}",
        })
    else:
        st.caption("No options positions in current book.")


# ══════════════════════════════════════════════════════════════════════════════
# REPO
# ══════════════════════════════════════════════════════════════════════════════

with t6:

    repo_calls = [r for r in margin.repo_details if not r.is_compliant]
    _kpi_row([
        ("Total Repo Trades",     str(len(bor.repo_positions)), "Active positions", COLORS["blue"]),
        ("Variation Calls",       str(len(repo_calls)),
         f"${sum(r.variation_margin_call for r in repo_calls)/1e6:,.2f}M",
         COLORS["amber"] if repo_calls else COLORS["green"]),
        ("Total Repo Book",       f"${sum(r.cash_amount for r in bor.repo_positions if r.direction=='REPO')/1e6:,.0f}M",
         "Gross cash lent", COLORS["teal"]),
        ("Total Reverse Book",    f"${sum(r.cash_amount for r in bor.repo_positions if r.direction=='REVERSE')/1e6:,.0f}M",
         "Gross cash borrowed", COLORS["purple"]),
    ])

    st.divider()
    _section("Repo & Reverse Repo — Variation Margin")
    repo_id_to_cusip = {r.repo_id: r.collateral_cusip for r in bor.repo_positions}
    repo_tbl = [{"Repo ID": r.repo_id, "Direction": r.direction,
                 "Collateral": sec_desc_map.get(repo_id_to_cusip.get(r.repo_id, ""), r.repo_id),
                 "Coll. MV": r.collateral_mv, "Cash Amount": r.cash_amount,
                 "Haircut %": r.haircut_applied * 100, "Req. Coll.": r.required_collateral,
                 "Var. Call": r.variation_margin_call,
                 "Status": "Call Required" if not r.is_compliant else "OK"}
                for r in margin.repo_details]
    df_repo = pd.DataFrame(repo_tbl)

    def _style_repo(row):
        if row.get("Status") == "Call Required":
            return ["background-color:#160808; color:#ef4444"] * len(row)
        return [""] * len(row)

    st.dataframe(df_repo.style.apply(_style_repo, axis=1)
                 .format({c: "${:,.0f}" for c in ["Coll. MV", "Cash Amount", "Req. Coll.", "Var. Call"]}
                         | {"Haircut %": "{:.1f}%"}),
                 use_container_width=True, hide_index=True, height=380)

    # ── Repo Counterparty Concentration ───────────────────────────────────────
    st.divider()
    _section("Repo Counterparty Concentration")

    _cp_exposure: dict = {}  # counterparty → signed net cash (REPO pos, REVERSE neg)
    _cp_trades:   dict = {}
    _cp_gross:    dict = {}
    for _r in bor.repo_positions:
        _cp = _r.counterparty
        _signed = _r.cash_amount if _r.direction == "REPO" else -_r.cash_amount
        _cp_exposure[_cp] = _cp_exposure.get(_cp, 0.0) + _signed
        _cp_gross[_cp]    = _cp_gross.get(_cp, 0.0) + _r.cash_amount
        _cp_trades[_cp]   = _cp_trades.get(_cp, 0) + 1

    _total_book = sum(_cp_gross.values()) or 1.0
    _nc_val     = nc.net_capital or 1.0
    _largest_cp = max(_cp_gross, key=_cp_gross.get) if _cp_gross else "—"
    _largest_exp = _cp_gross.get(_largest_cp, 0.0)
    _largest_pct_nc = _largest_exp / _nc_val * 100

    _kpi_row([
        ("# Counterparties",          str(len(_cp_exposure)),         "Active repo counterparties", COLORS["blue"]),
        ("Largest Cash Exposure",     f"${_largest_exp/1e6:,.1f}M",  _largest_cp, COLORS["amber"]),
        ("Largest % of Net Capital",  f"{_largest_pct_nc:.1f}%",
         _badge("CONCENTRATION RISK", False) if _largest_pct_nc > 25 else "Within 25% limit",
         COLORS["red"] if _largest_pct_nc > 25 else COLORS["green"]),
        ("Total Book (Gross Cash)",   f"${_total_book/1e6:,.0f}M",   f"{len(bor.repo_positions)} trades", COLORS["teal"]),
    ])

    _cp_sorted = sorted(_cp_exposure.items(), key=lambda x: -abs(x[1]))
    fig_cp = go.Figure(go.Bar(
        x=[cp for cp, _ in _cp_sorted],
        y=[v for _, v in _cp_sorted],
        marker_color=[COLORS["red"] if v > 0 else COLORS["teal"] for _, v in _cp_sorted],
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Net Cash: %{y:$,.0f}<extra></extra>",
    ))
    fig_cp.update_layout(
        xaxis=dict(tickangle=-30),
        yaxis=dict(tickprefix="$", tickformat=",.0f"),
    )
    _chart(fig_cp, 280)

    _cp_rows = [{
        "Counterparty":    cp,
        "# Trades":        _cp_trades[cp],
        "Gross Cash":      _cp_gross[cp],
        "% of Book":       _cp_gross[cp] / _total_book * 100,
        "% of NC":         _cp_gross[cp] / _nc_val * 100,
    } for cp in [cp for cp, _ in _cp_sorted]]
    _html_table(pd.DataFrame(_cp_rows), {
        "Gross Cash": "${:,.0f}",
        "% of Book":  "{:.1f}%",
        "% of NC":    "{:.1f}%",
    }, flag_col="% of NC", flag_threshold=20.0)

    st.divider()
    _section("Clearing Organization Margin  ·  NSCC / DTC / OCC / FICC")

    _kpi_row([
        ("Total Clearing Margin", f"${clearing.total_clearing_margin/1e6:,.1f}M",
         f"{len(clearing.calls)} components",
         COLORS["red"] if clearing.has_ecp_charge else COLORS["amber"]),
        ("NSCC Total",            f"${clearing.nscc_total/1e6:,.1f}M",
         "MTM + VaR" + (" + ECP ⚠" if clearing.has_ecp_charge else ""),
         COLORS["red"] if clearing.has_ecp_charge else COLORS["blue"]),
        ("DTC",                   f"${(clearing.dtc_net_debit_cap + clearing.dtc_collateral_monitor)/1e6:,.1f}M",
         "Net Debit Cap + Coll. Monitor", COLORS["teal"]),
        ("OCC",                   f"${(clearing.occ_span_margin + clearing.occ_net_options_value)/1e6:,.1f}M",
         "SPAN Margin + Net Options Value", COLORS["purple"]),
        ("FICC",                  f"${clearing.ficc_margin/1e6:,.1f}M",
         "GSD Clearing Fund", COLORS["amber"]),
    ])

    _cm_rows = [
        {"Org": c.org, "Component": c.component, "Description": c.description,
         "Amount ($)": c.amount, "Due By": c.due_by,
         "Required": "Yes" if c.is_required else "Advisory"}
        for c in sorted(clearing.calls, key=lambda x: (-x.amount, x.org))
    ]
    df_cm = pd.DataFrame(_cm_rows)

    def _style_cm(row):
        if "ECP" in str(row.get("Component", "")):
            return ["background-color:#1a1008;color:#f59e0b"] * len(row)
        if row.get("Required") == "Yes":
            return ["background-color:#080f1c"] * len(row)
        return ["color:#6b7fa3"] * len(row)

    st.dataframe(df_cm.style.apply(_style_cm, axis=1)
                 .format({"Amount ($)": "${:,.0f}"}),
                 use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# REG SHO
# ══════════════════════════════════════════════════════════════════════════════

with t7:

    _section("Reg SHO — Settlement Fails Aging  ·  Rule 203 / 204")

    _kpi_row([
        ("Total Open Fails",          str(fails.total_fails),
         f"FTD: {fails.total_ftd}  |  FTR: {fails.total_ftr}", COLORS["blue"]),
        ("Close-Out Required (T+3+)", str(len(fails.close_out_required)),
         f"${fails.open_close_out_mv/1e6:,.1f}M  Rule 204 buy-in",
         COLORS["amber"] if fails.close_out_required else COLORS["green"]),
        ("Hard Close-Out (T+13+)",    str(len(fails.hard_close_out)),
         f"${fails.open_hard_close_out_mv/1e6:,.1f}M  Threshold securities",
         COLORS["red"] if fails.hard_close_out else COLORS["green"]),
        ("Reg SHO Status",
         _badge("BREACH", False) if not fails.is_compliant else _badge("COMPLIANT", True),
         "Hard close-outs present" if not fails.is_compliant else "No T+13+ items",
         COLORS["red"] if not fails.is_compliant else COLORS["green"]),
    ])

    _fs_c1, _fs_c2 = st.columns(2)

    with _fs_c1:
        _section("Aging Buckets — FTD vs FTR")
        _buck_labels = [b.label for b in fails.aging_buckets if b.count > 0]
        _ftr_mvs     = [b.ftr_mv for b in fails.aging_buckets if b.count > 0]
        _ftd_mvs     = [b.ftd_mv for b in fails.aging_buckets if b.count > 0]
        fig_fails = go.Figure()
        fig_fails.add_trace(go.Bar(name="FTR (Fails to Receive)", x=_buck_labels, y=_ftr_mvs,
                                   marker_color=COLORS["teal"], marker_line_width=0))
        fig_fails.add_trace(go.Bar(name="FTD (Fails to Deliver)", x=_buck_labels, y=_ftd_mvs,
                                   marker_color=COLORS["red"], marker_line_width=0))
        fig_fails.update_layout(barmode="group",
                                yaxis=dict(tickprefix="$", tickformat=",.0f"),
                                legend=dict(orientation="h", y=1.1, font_size=10))
        _chart(fig_fails, 280)

    with _fs_c2:
        _section("Fails by Business Line")
        _bl_items = sorted(fails.by_business_line.items(), key=lambda x: -x[1])
        _bl_labels = [k for k, _ in _bl_items]
        _bl_vals   = [v for _, v in _bl_items]
        fig_bl = go.Figure(go.Bar(x=_bl_labels, y=_bl_vals,
                                  marker_color=COLORS["blue"], marker_line_width=0,
                                  text=[f"${v/1e6:,.1f}M" for v in _bl_vals],
                                  textposition="auto"))
        fig_bl.update_layout(yaxis=dict(tickprefix="$", tickformat=",.0f"), xaxis_title=None)
        _chart(fig_bl, 280)

    _section("Individual Fail Records")
    _fail_rows = []
    for _f in sorted(fails.fail_records, key=lambda x: -x.days_outstanding):
        _sec  = bor.securities.get(_f.cusip)
        _desc = _sec.description if _sec else _f.cusip
        _flag = ("HARD CLOSE-OUT" if _f.hard_close_out
                 else ("CLOSE-OUT REQ." if _f.close_out_required else ""))
        _fail_rows.append({
            "Fail ID":    _f.fail_id,
            "Security":   _desc,
            "Dir.":       _f.direction,
            "Age (days)": _f.days_outstanding,
            "Bucket":     _f.aging_bucket,
            "Mkt Value":  _f.market_value,
            "Contra":     _f.contra_party,
            "Reason":     _f.reason,
            "BizLine":    _f.business_line,
            "Flag":       _flag,
        })
    df_fails = pd.DataFrame(_fail_rows)

    def _style_fails(row):
        if row.get("Flag") == "HARD CLOSE-OUT":
            return ["background-color:#1a0808;color:#ef4444"] * len(row)
        if row.get("Flag") == "CLOSE-OUT REQ.":
            return ["background-color:#1a1008;color:#f59e0b"] * len(row)
        return [""] * len(row)

    st.dataframe(df_fails.style.apply(_style_fails, axis=1)
                 .format({"Mkt Value": "${:,.0f}"}),
                 use_container_width=True, hide_index=True, height=420)


# ══════════════════════════════════════════════════════════════════════════════
# FOCUS REPORT
# ══════════════════════════════════════════════════════════════════════════════

with t8:
    st.markdown(
        f'<div style="background:#0c1525;border:1px solid #182035;border-radius:5px;'
        f'padding:1rem 1.5rem;margin-bottom:1.5rem;display:flex;justify-content:space-between">'
        f'<div><div style="font-size:10px;font-weight:700;letter-spacing:0.1em;color:#2e4460;'
        f'text-transform:uppercase;margin-bottom:0.3rem">FOCUS Report Part II</div>'
        f'<div style="font-size:14px;font-weight:600;color:#deeeff">{focus.firm_name}</div></div>'
        f'<div style="text-align:right">'
        f'<div style="font-size:10px;color:#2e4460;margin-bottom:0.2rem">BD ID: {focus.broker_dealer_id}</div>'
        f'<div style="font-size:10px;color:#2e4460">Period: {focus.report_period}</div>'
        f'<div style="font-size:10px;color:#2e4460">As of: {focus.as_of_date}</div>'
        f'</div></div>', unsafe_allow_html=True)

    sections = {
        "Balance Sheet":             ["1","2","3","4","5","8","9","10","16"],
        "Net Capital (15c3-1)":      ["3210","3215","3220","3221","3225","3226",
                                       "3230","3240","3250","3260","3400","3410"],
        "Customer Reserve (15c3-3)": ["2010","2015","2016","2017","2020","2030",
                                       "2035","2040","2041","2042","2060","2061","2062"],
        "Margin":                    ["4010","4020","4030","4040"],
        "Revenue / P&L":             ["4800","4810","4820"],
    }
    for sec_name, lines in sections.items():
        with st.expander(sec_name, expanded=(sec_name == "Net Capital (15c3-1)")):
            rows_f = []
            for line in lines:
                item = focus.get(line)
                if item:
                    if item.note == "Percentage":   display = f"{item.amount:.2f}%"
                    elif item.note == "Count":      display = f"{item.amount:.0f}"
                    else:                           display = f"${item.amount:,.2f}"
                    rows_f.append({"Line": item.line, "Description": item.description,
                                   "Amount": display, "Note": item.note})
            _html_table(pd.DataFrame(rows_f))

    st.divider()
    focus_path = "data/csv/focus_report.csv"
    if not os.path.exists(focus_path):
        FOCUSReportAssembler(bor, nc, reserve, margin,
                             config.CALCULATION_DATE).export_csv(focus, focus_path)
    if os.path.exists(focus_path):
        with open(focus_path, "rb") as f:
            st.download_button(label="↓  Export FOCUS Report  (CSV)", data=f,
                               file_name=f"focus_report_{config.REPORT_PERIOD}.csv",
                               mime="text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO TESTER
# ══════════════════════════════════════════════════════════════════════════════

with t9:

    # ── Pre-Defined Stress Scenarios ───────────────────────────────────────────
    _section("Pre-Defined Stress Scenarios")
    _stress_results = run_stress(bor, nc, reserve, margin)

    # Build heatmap-style table
    _sc_names  = [s.name for s in _stress_results]
    _sc_dnc    = [s.delta_net_capital      for s in _stress_results]
    _sc_dres   = [s.delta_reserve_required for s in _stress_results]
    _sc_dmg    = [s.delta_margin_call_amount for s in _stress_results]

    def _stress_cell(val: float, invert: bool = False) -> str:
        """Render a stress delta cell with red/amber/green colouring."""
        bad = val < 0 if not invert else val > 0
        if bad:
            if abs(val) > 50e6:
                bg, fg = "#2d0a0a", "#ef4444"
            else:
                bg, fg = "#1a1008", "#f59e0b"
        else:
            bg, fg = "#052e16", "#10b981"
        sign = "+" if val >= 0 else "−"
        return (f'<td style="padding:8px 14px;text-align:right;background:{bg};color:{fg};'
                f'font-weight:600;font-variant-numeric:tabular-nums;font-size:12.5px;'
                f'border:1px solid #182035">'
                f'{sign}${abs(val)/1e6:.1f}M</td>')

    _hdr = (
        '<th style="padding:8px 14px;background:#080e1c;color:#2e4460;font-size:9.5px;'
        'font-weight:700;letter-spacing:0.1em;text-transform:uppercase;border:1px solid #182035">'
    )
    _th_scenario = f'{_hdr}Scenario</th>'
    _th_nc       = f'{_hdr}Δ Net Capital</th>'
    _th_res      = f'{_hdr}Δ Reserve Required</th>'
    _th_mg       = f'{_hdr}Δ Margin Calls $</th>'
    _th_status   = f'{_hdr}NC Post-Shock</th>'

    _stress_rows = ""
    for s in _stress_results:
        _nc_ok   = s.shocked_is_compliant
        _ew_flag = s.shocked_is_early_warning
        _status  = (_badge("NON-COMPLIANT", False) if not _nc_ok
                    else _badge("EARLY WARNING", False) if _ew_flag
                    else _badge("COMPLIANT", True))
        _name_bg = "#0c1525"
        _stress_rows += (
            f'<tr>'
            f'<td style="padding:8px 14px;color:#c9d8ed;font-weight:500;font-size:12.5px;'
            f'background:{_name_bg};border:1px solid #182035">{s.name}</td>'
            + _stress_cell(s.delta_net_capital, invert=False)
            + _stress_cell(s.delta_reserve_required, invert=True)
            + _stress_cell(s.delta_margin_call_amount, invert=True)
            + f'<td style="padding:8px 14px;text-align:center;background:#0c1525;'
              f'border:1px solid #182035">{_status}&nbsp; '
              f'<span style="font-size:11px;color:#4a6585">${s.shocked_net_capital/1e6:,.0f}M</span></td>'
            f'</tr>'
        )

    st.markdown(
        f'<div style="overflow-x:auto;border:1px solid #182035;border-radius:5px;margin-bottom:1.5rem">'
        f'<table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif">'
        f'<thead><tr>{_th_scenario}{_th_nc}{_th_res}{_th_mg}{_th_status}</tr></thead>'
        f'<tbody>{_stress_rows}</tbody>'
        f'</table></div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Green = improvement vs baseline · Amber = moderate adverse impact (< $50M) · "
        "Red = severe adverse impact (> $50M). "
        "NC status reflects post-shock compliance vs 2% ADI threshold."
    )

    st.divider()

    # ── Security universe grouped by asset class ───────────────────────────────
    eq_secs = {s.cusip: s.description for s in bor.securities.values()
               if s.security_type.value in ("EQUITY_LISTED", "ETF")}
    fi_secs = {s.cusip: s.description for s in bor.securities.values()
               if s.security_type.value in ("US_TREASURY", "AGENCY", "MUNICIPAL",
                                              "CORP_IG", "CORP_HY", "MBS")}
    opt_secs = {s.cusip: s.description for s in bor.securities.values()
                if s.security_type.value == "OPTION"}

    client_accts = {
        a.account_id: f"{a.client_name or a.account_id}  [{a.account_type.value}]"
        for a in sorted(bor.get_customer_accounts() + bor.get_pab_accounts(),
                        key=lambda a: a.client_name or a.account_id)
    }

    # ── Trade entry + positions panel ─────────────────────────────────────────
    col_form, col_trades = st.columns([5, 7])

    with col_form:
        _section("Add Hypothetical Trade")

        with st.form("scenario_form", clear_on_submit=True):
            asset_class = st.selectbox(
                "Asset Class",
                ["Equity / ETF", "Fixed Income", "Option"],
            )

            if asset_class == "Equity / ETF":
                sec_pool, qty_label, default_qty, qty_step = eq_secs,  "Quantity (shares)",   10_000.0, 1_000.0
            elif asset_class == "Fixed Income":
                sec_pool, qty_label, default_qty, qty_step = fi_secs,  "Face Value ($)",    5_000_000.0, 500_000.0
            else:
                sec_pool, qty_label, default_qty, qty_step = opt_secs, "Contracts",               100.0, 10.0

            cusip = st.selectbox("Security", options=list(sec_pool.keys()),
                                 format_func=lambda x: sec_pool.get(x, x))

            account_id = st.selectbox("Client Account", options=list(client_accts.keys()),
                                      format_func=lambda x: client_accts.get(x, x))

            direction = st.radio("Direction", ["BUY  (Long)", "SELL  (Short)"], horizontal=True)

            col_q, col_p = st.columns(2)
            with col_q:
                quantity = st.number_input(qty_label, min_value=1.0,
                                           value=default_qty, step=qty_step, format="%.0f")
            with col_p:
                ref_price = bor.securities[cusip].price if cusip in bor.securities else 100.0
                price = st.number_input("Price", min_value=0.0001,
                                        value=ref_price, step=0.01, format="%.4f")

            is_margin = st.checkbox("Finance with margin  (50% Reg T initial)", value=True)

            submitted = st.form_submit_button("＋  Add to Scenario", use_container_width=True)

        if submitted and cusip:
            sec = bor.securities.get(cusip)
            trade = ScenarioTrade(
                trade_id=new_trade_id(),
                account_id=account_id,
                client_name=(bor.accounts[account_id].client_name
                             if account_id in bor.accounts else account_id),
                cusip=cusip,
                description=sec_pool.get(cusip, cusip),
                direction="BUY" if "BUY" in direction else "SELL",
                quantity=quantity,
                price=price,
                security_type=sec.security_type.value if sec else "EQUITY_LISTED",
                asset_class=sec.asset_class if sec else "equity",
                is_margin=is_margin,
            )
            st.session_state.scenario_trades.append(trade)
            st.rerun()

        # ── Upload Portfolio CSV ───────────────────────────────────────────────
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        _section("Upload Portfolio CSV")

        template_csv = (
            "cusip,direction,quantity,price,account_id,description,is_margin\n"
            "037833100,BUY,10000,,,,TRUE\n"
            "594918104,SELL,5000,185.00,,Apple Inc,TRUE\n"
        )
        st.download_button(
            label="⬇  Download Template",
            data=template_csv,
            file_name="portfolio_template.csv",
            mime="text/csv",
            use_container_width=True,
        )

        uploaded_file = st.file_uploader(
            "Upload positions CSV",
            type=["csv"],
            label_visibility="collapsed",
            key=f"portfolio_upload_{st.session_state.upload_key}",
        )

        if uploaded_file is not None:
            try:
                df_up = pd.read_csv(uploaded_file)
                df_up.columns = [c.strip().lower() for c in df_up.columns]
                required_cols = {"cusip", "direction", "quantity"}
                missing_cols = required_cols - set(df_up.columns)
                if missing_cols:
                    st.error(f"Missing required columns: {', '.join(sorted(missing_cols))}")
                else:
                    default_acct = list(client_accts.keys())[0] if client_accts else ""
                    parsed, errs = [], []
                    for idx, row in df_up.iterrows():
                        try:
                            cusip_u = str(row["cusip"]).strip()
                            dir_u = str(row["direction"]).strip().upper()
                            if dir_u not in ("BUY", "SELL"):
                                errs.append(f"Row {idx+2}: direction must be BUY or SELL")
                                continue
                            qty_u = float(row["quantity"])

                            sec_u = bor.securities.get(cusip_u)

                            try:
                                price_u = float(row.get("price", ""))
                            except (ValueError, TypeError):
                                price_u = sec_u.price if sec_u else 0.0

                            acct_raw = str(row.get("account_id", "")).strip()
                            acct_u = acct_raw if acct_raw and acct_raw != "nan" else default_acct

                            desc_raw = str(row.get("description", "")).strip()
                            desc_u = (desc_raw if desc_raw and desc_raw != "nan"
                                      else (sec_u.description if sec_u else cusip_u))

                            margin_raw = str(row.get("is_margin", "TRUE")).strip().upper()
                            is_margin_u = margin_raw not in ("FALSE", "0", "NO")

                            parsed.append(ScenarioTrade(
                                trade_id=new_trade_id(),
                                account_id=acct_u,
                                client_name=(bor.accounts[acct_u].client_name
                                             if acct_u in bor.accounts else acct_u),
                                cusip=cusip_u,
                                description=desc_u,
                                direction=dir_u,
                                quantity=qty_u,
                                price=price_u,
                                security_type=(sec_u.security_type.value if sec_u else "EQUITY_LISTED"),
                                asset_class=(sec_u.asset_class if sec_u else "equity"),
                                is_margin=is_margin_u,
                            ))
                        except Exception as row_exc:
                            errs.append(f"Row {idx+2}: {row_exc}")

                    for e in errs[:5]:
                        st.warning(e)

                    if parsed:
                        st.caption(f"{len(parsed)} trade{'s' if len(parsed) != 1 else ''} ready to import")
                        if st.button(
                            f"＋  Add {len(parsed)} Trade{'s' if len(parsed) != 1 else ''}",
                            use_container_width=True,
                            key="add_uploaded",
                        ):
                            st.session_state.scenario_trades.extend(parsed)
                            st.session_state.upload_key += 1
                            st.rerun()
            except Exception as exc:
                st.error(f"Could not parse CSV: {exc}")

        # ── Random Batch Generator ─────────────────────────────────────────────
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        _section("Random Batch Generator")

        all_acct_ids = list(client_accts.keys())
        all_secs_by_class = {
            "equity":       list(eq_secs.keys()),
            "fixed_income": list(fi_secs.keys()),
            "option":       list(opt_secs.keys()),
        }
        # Weight asset class selection: equities most common, options least
        _AC_WEIGHTS = {"equity": 0.55, "fixed_income": 0.30, "option": 0.15}

        with st.form("batch_form", clear_on_submit=False):
            col_n, col_seed = st.columns([3, 1])
            with col_n:
                batch_n = st.slider("Number of trades", min_value=1, max_value=5000,
                                    value=100, step=1)
            with col_seed:
                use_seed = st.checkbox("Fixed seed", value=False,
                                       help="Reproducible randomness")

            col_eq, col_fi, col_opt = st.columns(3)
            with col_eq:   w_eq  = st.number_input("Equity weight",  0.0, 1.0, 0.55, 0.05)
            with col_fi:   w_fi  = st.number_input("Fixed Inc weight", 0.0, 1.0, 0.30, 0.05)
            with col_opt:  w_opt = st.number_input("Option weight",  0.0, 1.0, 0.15, 0.05)

            gen_submitted = st.form_submit_button(
                "⚡  Generate Random Trades", use_container_width=True)

        if gen_submitted and all_acct_ids:
            rng = random.Random(42 if use_seed else None)

            # Normalise weights; fall back to even split if all zero
            raw_w = [w_eq, w_fi, w_opt]
            total_w = sum(raw_w)
            if total_w == 0:
                raw_w = [1.0, 1.0, 1.0]; total_w = 3.0
            norm_w = [w / total_w for w in raw_w]

            ac_keys   = ["equity", "fixed_income", "option"]
            ac_labels = ["Equity / ETF", "Fixed Income", "Option"]

            new_batch: list = []
            for _ in range(batch_n):
                # Pick asset class
                ac = rng.choices(ac_keys, weights=norm_w, k=1)[0]
                pool_keys = all_secs_by_class[ac]
                if not pool_keys:
                    continue

                cusip_r = rng.choice(pool_keys)
                sec_r   = bor.securities.get(cusip_r)
                if sec_r is None:
                    continue

                ref_p   = sec_r.price
                # ± 3% price noise
                price_r = ref_p * rng.uniform(0.97, 1.03)

                # Realistic quantity distributions (log-uniform)
                if ac == "equity":
                    qty_r = math.floor(math.exp(rng.uniform(math.log(100),
                                                             math.log(500_000))) / 100) * 100
                elif ac == "fixed_income":
                    qty_r = math.floor(math.exp(rng.uniform(math.log(100_000),
                                                             math.log(50_000_000))) / 100_000) * 100_000
                else:  # option
                    qty_r = math.floor(math.exp(rng.uniform(math.log(1),
                                                             math.log(2_000))) / 1) * 1

                # Direction: weighted slightly long (60/40)
                dir_r = rng.choices(["BUY", "SELL"], weights=[0.60, 0.40])[0]

                # Intent label (cosmetic — captured in description prefix)
                if dir_r == "BUY":
                    intent = rng.choice(["Buy to Open", "Buy to Cover"])
                else:
                    intent = rng.choice(["Sell to Close", "Sell Short"])

                acct_id_r = rng.choice(all_acct_ids)
                client_r  = (bor.accounts[acct_id_r].client_name
                             if acct_id_r in bor.accounts else acct_id_r)

                # Options and FI are less likely to be margined
                margin_r = rng.random() < (0.85 if ac == "equity"
                                           else 0.40 if ac == "fixed_income"
                                           else 0.20)

                sec_pool_r = (eq_secs if ac == "equity"
                              else fi_secs if ac == "fixed_income"
                              else opt_secs)

                new_batch.append(ScenarioTrade(
                    trade_id=new_trade_id(),
                    account_id=acct_id_r,
                    client_name=client_r,
                    cusip=cusip_r,
                    description=f"[{intent}] {sec_pool_r.get(cusip_r, cusip_r)}",
                    direction=dir_r,
                    quantity=float(qty_r),
                    price=price_r,
                    security_type=sec_r.security_type.value,
                    asset_class=sec_r.asset_class,
                    is_margin=margin_r,
                ))

            st.session_state.scenario_trades.extend(new_batch)
            st.rerun()

    with col_trades:
        trades = st.session_state.scenario_trades
        n = len(trades)
        header_right = ""
        if n > 0:
            header_right = (f'<span style="font-size:10px;color:#4a6585">'
                            f'{n} trade{"s" if n != 1 else ""} &nbsp;·&nbsp; '
                            f'Total MV: ${sum(t.market_value for t in trades):,.0f}</span>')

        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'font-size:10px;font-weight:700;letter-spacing:0.13em;color:#2e4460;'
            f'text-transform:uppercase;padding:1.5rem 0 0.6rem;border-bottom:1px solid #182035;'
            f'margin-bottom:0.8rem">SCENARIO POSITIONS{header_right}</div>',
            unsafe_allow_html=True,
        )

        if not trades:
            st.markdown(
                '<div style="text-align:center;color:#2e4460;padding:3rem 1rem;'
                'border:1px dashed #182035;border-radius:5px;font-size:11px;'
                'letter-spacing:0.08em;text-transform:uppercase">No trades added yet</div>',
                unsafe_allow_html=True,
            )
        else:
            for i, trade in enumerate(trades):
                dir_color = COLORS["green"] if trade.direction == "BUY" else COLORS["red"]
                hc_pct, hc_amt = 0.0, 0.0
                if trade.cusip in bor.securities:
                    from calculators.haircuts import compute_haircut
                    sec = bor.securities[trade.cusip]
                    hc_pct, hc_amt = compute_haircut(
                        sec.security_type, trade.market_value,
                        sec.years_to_maturity(config.CALCULATION_DATE), sec.price)

                col_desc, col_btn = st.columns([9, 1])
                with col_desc:
                    st.markdown(
                        f'<div style="background:#0c1525;border:1px solid #182035;border-left:3px solid {dir_color};'
                        f'border-radius:4px;padding:0.55rem 0.9rem;margin-bottom:0.35rem;'
                        f'font-family:Inter,sans-serif;display:flex;justify-content:space-between;'
                        f'align-items:center">'
                        f'<div>'
                        f'<span style="color:{dir_color};font-size:9.5px;font-weight:700;'
                        f'letter-spacing:0.12em;text-transform:uppercase;margin-right:0.6rem">'
                        f'{trade.direction}</span>'
                        f'<span style="color:#deeeff;font-size:12px">{trade.description[:45]}</span>'
                        f'<br>'
                        f'<span style="color:#4a6585;font-size:10.5px">'
                        f'{trade.client_name}&nbsp;&nbsp;·&nbsp;&nbsp;{trade.notional_label}</span>'
                        f'</div>'
                        f'<div style="text-align:right">'
                        f'<div style="color:#deeeff;font-size:12px;font-variant-numeric:tabular-nums">'
                        f'${trade.market_value:,.0f}</div>'
                        f'<div style="color:#f59e0b;font-size:10px;font-variant-numeric:tabular-nums">'
                        f'HC: ${hc_amt:,.0f} ({hc_pct*100:.0f}%)</div>'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                with col_btn:
                    if st.button("✕", key=f"rm_{trade.trade_id}", use_container_width=True):
                        st.session_state.scenario_trades.pop(i)
                        st.rerun()

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Clear Random Trades", use_container_width=True):
                    st.session_state.scenario_trades = [
                        t for t in st.session_state.scenario_trades
                        if not t.description.startswith("[")
                    ]
                    st.rerun()
            with btn_col2:
                if st.button("Clear All Trades", use_container_width=True):
                    st.session_state.scenario_trades = []
                    st.rerun()

    # ── Regulatory Impact ──────────────────────────────────────────────────────

    st.divider()

    if not trades:
        st.markdown(
            '<div style="text-align:center;padding:3rem;color:#2e4460;font-size:12px;'
            'letter-spacing:0.06em;text-transform:uppercase">'
            'Add trades above to see regulatory impact</div>',
            unsafe_allow_html=True,
        )
    else:
        _section("Regulatory Impact Analysis")

        # Run scenario calculations
        with st.spinner("Computing scenario…"):
            s_bor = apply_scenario(bor, trades)
            s_nc     = NetCapitalCalculator(s_bor, config.CALCULATION_DATE).calculate()
            s_res    = CustomerReserveCalculator(s_bor, config.CALCULATION_DATE).calculate()
            s_margin = MarginCalculator(s_bor, config.CALCULATION_DATE).calculate()

        s_cushion = s_nc.cushion_pct * 100 if s_nc.cushion_pct != float("inf") else 0.0

        # ── Before / After KPI row ─────────────────────────────────────────────
        def _delta_html(base: float, scen: float, prefix: str = "$", suffix: str = "",
                        higher_is_better: bool = True) -> str:
            delta = scen - base
            better = (delta >= 0) == higher_is_better
            color  = COLORS["green"] if better else COLORS["red"]
            sign   = "+" if delta >= 0 else ""
            if prefix == "$":
                d_str = f"{sign}${abs(delta)/1e6:.2f}M" if abs(delta) >= 1e4 else f"{sign}${delta:,.0f}"
            else:
                d_str = f"{sign}{delta:.2f}{suffix}"
            return f'<span style="color:{color};font-size:11px;font-weight:600">{d_str}</span>'

        metrics = [
            ("Net Capital",      nc.net_capital,      s_nc.net_capital,      True),
            ("Required NC",      nc.required_net_capital, s_nc.required_net_capital, False),
            ("Excess NC",        nc.excess_net_capital, s_nc.excess_net_capital, True),
            ("Total Haircuts",   nc.total_haircuts,   s_nc.total_haircuts,   False),
            ("Reserve Req.",     reserve.total_reserve_required, s_res.total_reserve_required, False),
            ("Margin Calls ($)", margin.total_margin_call_amount, s_margin.total_margin_call_amount, False),
        ]

        cols = st.columns(len(metrics))
        for col, (label, base_v, scen_v, hib) in zip(cols, metrics):
            better = (scen_v >= base_v) == hib
            accent = COLORS["green"] if better else COLORS["red"]
            delta  = scen_v - base_v
            sign   = "+" if delta >= 0 else ""
            d_str  = f"{sign}${delta/1e6:.2f}M" if abs(delta) >= 1e4 else f"{sign}${delta:,.0f}"
            col.markdown(
                f'<div style="background:#0c1525;border:1px solid #182035;border-top:2px solid {accent};'
                f'border-radius:5px;padding:0.8rem 1rem;text-align:center">'
                f'<div style="font-size:9.5px;font-weight:700;letter-spacing:0.1em;color:#3d5878;'
                f'text-transform:uppercase;margin-bottom:0.3rem">{label}</div>'
                f'<div style="font-size:11px;color:#4a6585;font-variant-numeric:tabular-nums">'
                f'${base_v/1e6:.2f}M</div>'
                f'<div style="font-size:1.1rem;font-weight:600;color:#deeeff;'
                f'font-variant-numeric:tabular-nums;letter-spacing:-0.02em">${scen_v/1e6:.2f}M</div>'
                f'<div style="font-size:11px;color:{accent};font-weight:600;'
                f'font-variant-numeric:tabular-nums">{d_str}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # ── Impact detail table ────────────────────────────────────────────────
        impact_rows = []
        for label, base_v, scen_v, hib in metrics:
            delta = scen_v - base_v
            better = (delta >= 0) == hib
            impact_rows.append({
                "Metric":    label,
                "Baseline":  f"${base_v:,.2f}",
                "Scenario":  f"${scen_v:,.2f}",
                "Delta":     f"{'+'if delta>=0 else ''}${delta:,.2f}",
                "Status":    "▲ Better" if better else "▼ Worse",
            })

        nc_status_row = {
            "Metric":   "Compliance Status",
            "Baseline": "✓ Compliant" if nc.is_compliant else "✗ Non-Compliant",
            "Scenario": "✓ Compliant" if s_nc.is_compliant else "✗ Non-Compliant",
            "Delta":    "—",
            "Status":   ("▲ Better" if s_nc.is_compliant and not nc.is_compliant
                         else "▼ Worse" if not s_nc.is_compliant and nc.is_compliant
                         else "→ Unchanged"),
        }
        impact_rows.append(nc_status_row)
        _html_table(pd.DataFrame(impact_rows))

        # ── Scenario haircut waterfall ─────────────────────────────────────────
        _section("Scenario Trade Haircut Contributions")

        scn_hc_rows = []
        for trade in trades:
            if trade.cusip in s_bor.securities:
                from calculators.haircuts import compute_haircut
                sec = s_bor.securities[trade.cusip]
                pct, amt = compute_haircut(
                    sec.security_type, trade.market_value,
                    sec.years_to_maturity(config.CALCULATION_DATE), sec.price)
                scn_hc_rows.append({
                    "Trade":       f"{trade.direction} {trade.description[:35]}",
                    "Client":      trade.client_name,
                    "MV":          trade.market_value,
                    "HC Rate %":   pct * 100,
                    "HC ($)":      amt,
                    "Direction":   trade.direction,
                })

        if scn_hc_rows:
            df_scn_hc = pd.DataFrame(scn_hc_rows).sort_values("HC ($)", ascending=True)
            fig_scn = go.Figure()
            for direction, color in [("BUY", COLORS["green"]), ("SELL", COLORS["red"])]:
                sub = df_scn_hc[df_scn_hc["Direction"] == direction]
                if not sub.empty:
                    fig_scn.add_trace(go.Bar(
                        x=sub["HC ($)"], y=sub["Trade"], orientation="h",
                        name=direction, marker_color=color, marker_line_width=0,
                        hovertemplate=(
                            "<b>%{y}</b><br>"
                            "Haircut: %{x:$,.0f}<br>"
                            "Rate: %{customdata[0]:.1f}%<extra></extra>"
                        ),
                        customdata=sub[["HC Rate %"]].values,
                    ))
            total_scn_hc = sum(r["HC ($)"] for r in scn_hc_rows)
            fig_scn.update_layout(
                barmode="group",
                title=dict(
                    text=f"Total scenario haircut: ${total_scn_hc:,.0f}  "
                         f"| Net Capital impact: ${(s_nc.net_capital - nc.net_capital):+,.0f}",
                    font=dict(size=11, color="#8ba3c0"), x=0,
                ),
                xaxis=dict(tickprefix="$", tickformat=",.0f"),
                legend=dict(orientation="h", y=1.12, font_size=10),
                yaxis=dict(tickfont_size=10),
            )
            _chart(fig_scn, max(260, len(scn_hc_rows) * 36 + 80))

        # ── Before/After waterfall comparison ─────────────────────────────────
        _section("Before vs After — Net Capital Bridge")
        bridge_steps = [
            ("Baseline NC",        nc.net_capital,                                     "absolute"),
            ("Scenario Haircuts", -(s_nc.total_haircuts - nc.total_haircuts),           "relative"),
            ("Reserve Δ",          -(s_res.total_reserve_required - reserve.total_reserve_required), "relative"),
            ("Scenario NC",        s_nc.net_capital,                                   "total"),
        ]
        fig_bridge = go.Figure(go.Waterfall(
            measure=[s[2] for s in bridge_steps],
            x=[s[0] for s in bridge_steps],
            y=[s[1] for s in bridge_steps],
            text=[f"${abs(s[1])/1e6:.2f}M" for s in bridge_steps],
            textposition="outside",
            textfont=dict(size=11, color="#8ba3c0"),
            connector={"line": {"color": "#182035", "width": 1}},
            decreasing={"marker": {"color": COLORS["red"], "line": {"width": 0}}},
            increasing={"marker": {"color": COLORS["green"], "line": {"width": 0}}},
            totals={"marker": {"color": COLORS["blue"], "line": {"width": 0}}},
        ))
        fig_bridge.add_hline(y=s_nc.required_net_capital, line_dash="dot",
                             line_color=COLORS["amber"], line_width=1,
                             annotation_text=f"Required {s_nc.required_net_capital/1e6:.1f}M",
                             annotation_font_size=10, annotation_font_color=COLORS["amber"])
        fig_bridge.update_layout(showlegend=False, yaxis=dict(tickprefix="$", tickformat=",.0f"))
        _chart(fig_bridge, 320)

    # ══════════════════════════════════════════════════════════════════════════
    # LIVE SIMULATION MODE
    # ══════════════════════════════════════════════════════════════════════════

    st.divider()
    _section("Live Simulation Mode")

    # ── Controls ──────────────────────────────────────────────────────────────
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2, 2, 2, 2])

    with ctrl_col1:
        sim_btn_label = "⏹  Stop Simulation" if st.session_state.sim_running else "▶  Start Simulation"
        if st.button(sim_btn_label, use_container_width=True):
            st.session_state.sim_running = not st.session_state.sim_running
            if not st.session_state.sim_running:
                pass  # keep history/trades visible after stop
            st.rerun()

    with ctrl_col2:
        trades_per_tick = st.select_slider(
            "Trades per tick",
            options=[1, 2, 5, 10, 20, 50],
            value=5,
        )

    with ctrl_col3:
        tick_interval = st.select_slider(
            "Tick interval (s)",
            options=[0.2, 0.5, 1.0, 2.0, 5.0],
            value=1.0,
        )

    with ctrl_col4:
        max_sim_trades = st.select_slider(
            "Rolling window (trades)",
            options=[100, 250, 500, 1000, 2000, 5000],
            value=500,
        )

    # Status bar
    n_sim = len(st.session_state.sim_trades)
    n_hist = len(st.session_state.sim_history)
    status_color = COLORS["green"] if st.session_state.sim_running else "#2e4460"
    pulse = "●" if st.session_state.sim_running else "○"
    st.markdown(
        f'<div style="font-size:11px;color:{status_color};letter-spacing:0.06em;'
        f'padding:0.4rem 0 0.8rem">'
        f'{pulse}&nbsp; {"LIVE — " if st.session_state.sim_running else "STOPPED — "}'
        f'Tick {st.session_state.sim_tick} &nbsp;·&nbsp; '
        f'{n_sim:,} sim trades &nbsp;·&nbsp; {n_hist} snapshots recorded'
        f'</div>',
        unsafe_allow_html=True,
    )

    if st.button("Reset Simulation", use_container_width=False):
        st.session_state.sim_running  = False
        st.session_state.sim_trades   = []
        st.session_state.sim_history  = []
        st.session_state.sim_tick     = 0
        st.rerun()

    # ── Live charts (shown once we have history) ───────────────────────────────
    if st.session_state.sim_history:
        df_hist = pd.DataFrame(st.session_state.sim_history)

        # ── Time-series: Net Capital trajectory ───────────────────────────────
        _section("Net Capital — Live Feed")
        fig_live = go.Figure()
        fig_live.add_trace(go.Scatter(
            x=df_hist["trades"], y=df_hist["net_capital"] / 1e6,
            mode="lines", name="Net Capital",
            line=dict(color=COLORS["blue"], width=2),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.07)",
        ))
        fig_live.add_trace(go.Scatter(
            x=df_hist["trades"], y=df_hist["required_nc"] / 1e6,
            mode="lines", name="Required NC (2% ADI)",
            line=dict(color=COLORS["amber"], width=1.5, dash="dot"),
        ))
        fig_live.add_trace(go.Scatter(
            x=df_hist["trades"], y=df_hist["excess_nc"] / 1e6,
            mode="lines", name="Excess NC",
            line=dict(color=COLORS["green"], width=1.5, dash="dash"),
        ))
        # Shade non-compliant regions
        non_compliant = df_hist[~df_hist["compliant"]]
        if not non_compliant.empty:
            for _, row in non_compliant.iterrows():
                fig_live.add_vrect(
                    x0=row["trades"] - trades_per_tick, x1=row["trades"],
                    fillcolor="rgba(239,68,68,0.08)", layer="below", line_width=0,
                )
        fig_live.update_layout(
            xaxis=dict(title="Cumulative sim trades", tickformat=",d"),
            yaxis=dict(title="$M", ticksuffix="M"),
            legend=dict(orientation="h", y=1.12, font_size=10),
        )
        _chart(fig_live, 340)

        # ── Time-series: Haircuts + Reserve + Margin Calls ────────────────────
        _section("Risk Metrics — Live Feed")
        fig_risk = go.Figure()
        fig_risk.add_trace(go.Scatter(
            x=df_hist["trades"], y=df_hist["haircuts"] / 1e6,
            mode="lines", name="Total Haircuts",
            line=dict(color=COLORS["red"], width=1.5),
        ))
        fig_risk.add_trace(go.Scatter(
            x=df_hist["trades"], y=df_hist["reserve_req"] / 1e6,
            mode="lines", name="Reserve Req.",
            line=dict(color=COLORS["purple"], width=1.5),
        ))
        fig_risk.add_trace(go.Scatter(
            x=df_hist["trades"], y=df_hist["margin_calls"] / 1e6,
            mode="lines", name="Margin Calls $",
            line=dict(color=COLORS["amber"], width=1.5),
        ))
        fig_risk.update_layout(
            xaxis=dict(title="Cumulative sim trades", tickformat=",d"),
            yaxis=dict(title="$M", ticksuffix="M"),
            legend=dict(orientation="h", y=1.12, font_size=10),
        )
        _chart(fig_risk, 300)

        # ── Recent trade ticker ────────────────────────────────────────────────
        _section("Recent Trade Feed")
        last_trades = st.session_state.sim_trades[-20:][::-1]
        ticker_rows = []
        for t in last_trades:
            dir_sym   = "▲" if t.direction == "BUY" else "▼"
            dir_color = COLORS["green"] if t.direction == "BUY" else COLORS["red"]
            ticker_rows.append({
                "Dir":         f'<span style="color:{dir_color};font-weight:700">{dir_sym} {t.direction}</span>',
                "Security":    t.description.split("] ", 1)[-1][:40],
                "Client":      t.client_name,
                "Notional":    t.notional_label,
                "Mkt Value":   f"${t.market_value:,.0f}",
                "Margin":      "✓" if t.is_margin else "—",
            })
        _html_table(pd.DataFrame(ticker_rows))

    # ── Simulation engine — generate tick + schedule next rerun ───────────────
    if st.session_state.sim_running:
        # Build security pool from BOR (same as batch generator)
        _sim_pools = {
            "equity":       [s for s in bor.securities.values()
                             if s.security_type.value in ("EQUITY_LISTED", "ETF")],
            "fixed_income": [s for s in bor.securities.values()
                             if s.security_type.value in ("US_TREASURY", "AGENCY", "MUNICIPAL",
                                                           "CORP_IG", "CORP_HY", "MBS")],
            "option":       [s for s in bor.securities.values()
                             if s.security_type.value == "OPTION"],
        }
        _sim_accts = list(bor.accounts.values())
        _ac_keys   = ["equity", "fixed_income", "option"]
        _ac_w      = [0.55, 0.30, 0.15]

        new_sim: list = []
        for _ in range(trades_per_tick):
            ac   = random.choices(_ac_keys, weights=_ac_w, k=1)[0]
            pool = _sim_pools[ac]
            if not pool:
                continue
            sec_r = random.choice(pool)
            acct_r = random.choice(_sim_accts)

            price_r = sec_r.price * random.uniform(0.97, 1.03)

            if ac == "equity":
                qty_r = math.floor(math.exp(random.uniform(math.log(100),
                                                            math.log(500_000))) / 100) * 100
            elif ac == "fixed_income":
                qty_r = math.floor(math.exp(random.uniform(math.log(100_000),
                                                            math.log(50_000_000))) / 100_000) * 100_000
            else:
                qty_r = max(1, math.floor(math.exp(random.uniform(math.log(1), math.log(2_000)))))

            dir_r  = random.choices(["BUY", "SELL"], weights=[0.60, 0.40])[0]
            intent = random.choice(["Buy to Open", "Buy to Cover"]) if dir_r == "BUY" \
                     else random.choice(["Sell to Close", "Sell Short"])

            sec_pool_label = (eq_secs if ac == "equity"
                              else fi_secs if ac == "fixed_income"
                              else opt_secs)

            new_sim.append(ScenarioTrade(
                trade_id=new_trade_id(),
                account_id=acct_r.account_id,
                client_name=acct_r.client_name or acct_r.account_id,
                cusip=sec_r.cusip,
                description=f"[{intent}] {sec_pool_label.get(sec_r.cusip, sec_r.cusip)}",
                direction=dir_r,
                quantity=float(qty_r),
                price=price_r,
                security_type=sec_r.security_type.value,
                asset_class=sec_r.asset_class,
                is_margin=random.random() < (0.85 if ac == "equity"
                                             else 0.40 if ac == "fixed_income" else 0.20),
            ))

        st.session_state.sim_trades.extend(new_sim)

        # Rolling window: drop oldest if over limit
        if len(st.session_state.sim_trades) > max_sim_trades:
            st.session_state.sim_trades = st.session_state.sim_trades[-max_sim_trades:]

        # Run calculations on base + sim trades combined
        _all_trades = list(st.session_state.scenario_trades) + st.session_state.sim_trades
        _s_bor    = apply_scenario(bor, _all_trades)
        _s_nc     = NetCapitalCalculator(_s_bor, config.CALCULATION_DATE).calculate()
        _s_res    = CustomerReserveCalculator(_s_bor, config.CALCULATION_DATE).calculate()
        _s_margin = MarginCalculator(_s_bor, config.CALCULATION_DATE).calculate()

        st.session_state.sim_history.append({
            "tick":        st.session_state.sim_tick,
            "trades":      len(st.session_state.sim_trades),
            "net_capital": _s_nc.net_capital,
            "required_nc": _s_nc.required_net_capital,
            "excess_nc":   _s_nc.excess_net_capital,
            "haircuts":    _s_nc.total_haircuts,
            "reserve_req": _s_res.total_reserve_required,
            "margin_calls":_s_margin.total_margin_call_amount,
            "compliant":   _s_nc.is_compliant,
        })
        st.session_state.sim_tick += 1

        time.sleep(tick_interval)
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# REG REFERENCE
# ══════════════════════════════════════════════════════════════════════════════

with t10:
    _section("Regulatory Reference — Rules Tracked by This Dashboard")

    REG_ROWS = [
        {
            "Rule / Regulation":       "SEC Rule 15c3-1\nNet Capital Rule",
            "Governing Body":          "SEC",
            "CFR Citation":            "17 CFR § 240.15c3-1",
            "Federal Register Ref":    "42 FR 33714 (Jul. 1, 1977)\nAmended 87 FR 25722 (May 2, 2022)",
            "Dashboard Tab":           "Net Capital / 15c3-1",
            "Key Threshold":           "Min $250,000 or 2% of aggregate debit items (Alternative Method); 5% early warning",
            "Description":             "Requires broker-dealers to maintain minimum net capital at all times. Haircuts are applied to proprietary securities positions and subtracted from tentative net capital.",
        },
        {
            "Rule / Regulation":       "SEC Rule 15c3-3\nCustomer Protection Rule",
            "Governing Body":          "SEC",
            "CFR Citation":            "17 CFR § 240.15c3-3",
            "Federal Register Ref":    "37 FR 25226 (Nov. 29, 1972)\nAmended 83 FR 51050 (Oct. 10, 2018)",
            "Dashboard Tab":           "Reserve / 15c3-3",
            "Key Threshold":           "Weekly reserve computation; customer funds segregated in Special Reserve Bank Account",
            "Description":             "Requires broker-dealers to maintain possession or control of customer fully-paid and excess margin securities, and to hold net customer credits in a segregated reserve account.",
        },
        {
            "Rule / Regulation":       "Regulation T\nCredit by Brokers & Dealers",
            "Governing Body":          "Federal Reserve Board",
            "CFR Citation":            "12 CFR § 220",
            "Federal Register Ref":    "29 FR 12278 (Aug. 28, 1964)\nVarious amendments",
            "Dashboard Tab":           "Margin",
            "Key Threshold":           "50% initial margin on equity purchases",
            "Description":             "Regulates the extension of credit by brokers and dealers to customers for the purchase of securities. Sets the initial margin requirement at 50% of purchase price for equity securities.",
        },
        {
            "Rule / Regulation":       "FINRA Rule 4210\nMargin Requirements",
            "Governing Body":          "FINRA",
            "CFR Citation":            "FINRA Rulebook § 4210",
            "Federal Register Ref":    "81 FR 82254 (Nov. 22, 2016)\nSR-FINRA-2015-036",
            "Dashboard Tab":           "Margin",
            "Key Threshold":           "25% maintenance margin on long positions; 30% house requirement",
            "Description":             "Establishes minimum maintenance margin requirements for customer accounts. Supplements Reg T by setting ongoing maintenance levels and concentration charge rules for large positions in a single security.",
        },
        {
            "Rule / Regulation":       "FINRA Rule 4210(e)\nRepo / Reverse Repo Margin",
            "Governing Body":          "FINRA",
            "CFR Citation":            "FINRA Rulebook § 4210(e)",
            "Federal Register Ref":    "81 FR 82254 (Nov. 22, 2016)\nSR-FINRA-2015-036",
            "Dashboard Tab":           "Repo",
            "Key Threshold":           "2% variation margin call trigger; daily mark-to-market",
            "Description":             "Governs margin requirements for covered agency transactions (repos and reverse repos). Requires daily mark-to-market and margin calls when collateral deficiency exceeds 2% of the contract value.",
        },
        {
            "Rule / Regulation":       "Regulation SHO\nShort Sale Regulation",
            "Governing Body":          "SEC",
            "CFR Citation":            "17 CFR §§ 242.200–242.204",
            "Federal Register Ref":    "69 FR 48008 (Aug. 6, 2004)\nAmended 74 FR 2578 (Jan. 15, 2009)",
            "Dashboard Tab":           "Reg SHO",
            "Key Threshold":           "Locate required before short sale; close-out of fail-to-deliver within T+2",
            "Description":             "Establishes rules governing short sales. Rule 203 requires a locate before executing a short sale. Rule 204 requires close-out of fail-to-deliver positions by the start of regular trading hours on T+2.",
        },
        {
            "Rule / Regulation":       "Options Margin Rules\nOCC / FINRA Rule 4210(f)",
            "Governing Body":          "OCC / FINRA / SEC",
            "CFR Citation":            "17 CFR § 240.9b-1; FINRA § 4210(f)",
            "Federal Register Ref":    "47 FR 12948 (Mar. 25, 1982)\nSR-FINRA-2022-020",
            "Dashboard Tab":           "Options",
            "Key Threshold":           "Margin based on underlying notional; 100-share multiplier per contract",
            "Description":             "Governs margin requirements for listed options positions. Naked short calls and puts carry higher margin requirements. Writers of options must post margin equal to the option premium plus a percentage of the underlying security value.",
        },
        {
            "Rule / Regulation":       "SEC Rule 17a-5\nFOCUS Report",
            "Governing Body":          "SEC",
            "CFR Citation":            "17 CFR § 240.17a-5",
            "Federal Register Ref":    "38 FR 26644 (Sep. 25, 1973)\nAmended 86 FR 54500 (Oct. 1, 2021)",
            "Dashboard Tab":           "FOCUS Report",
            "Key Threshold":           "Monthly (Part II/IIA) or quarterly (Part II for smaller BDs) filing",
            "Description":             "Requires broker-dealers to file the Financial and Operational Combined Uniform Single (FOCUS) Report with their designated examining authority. Part II captures net capital, reserve, and balance sheet data.",
        },
    ]

    # ── Table ─────────────────────────────────────────────────────────────────
    TH = (
        "background:#080e1c;color:#2e4460;font-size:9.5px;font-weight:700;"
        "letter-spacing:0.12em;text-transform:uppercase;padding:10px 14px;"
        "border-bottom:1px solid #182035;white-space:nowrap;text-align:left"
    )
    TD_BASE = (
        "padding:9px 14px;border-bottom:1px solid #0f1d32;"
        "font-family:Inter,sans-serif;vertical-align:top;font-size:12px"
    )
    COLS = ["Rule / Regulation", "Governing Body", "CFR Citation",
            "Federal Register Ref", "Dashboard Tab", "Key Threshold"]

    headers_html = "".join(f'<th style="{TH}">{c}</th>' for c in COLS)

    body_html = ""
    for i, r in enumerate(REG_ROWS):
        bg = "#0a1120" if i % 2 == 0 else "#070c18"
        rule_cell = (
            f'<td style="{TD_BASE};color:#deeeff;font-weight:600;white-space:nowrap">'
            + r["Rule / Regulation"].replace("\n", "<br>") + "</td>"
        )
        body_cell = f'<td style="{TD_BASE};color:#7a9fc0">' + r["Governing Body"] + "</td>"
        cfr_cell  = f'<td style="{TD_BASE};color:#c4d8ee;white-space:nowrap">' + r["CFR Citation"] + "</td>"
        fr_cell   = (
            f'<td style="{TD_BASE};color:#4a6585;white-space:nowrap;font-size:11px">'
            + r["Federal Register Ref"].replace("\n", "<br>") + "</td>"
        )
        tab_cell  = (
            f'<td style="{TD_BASE};color:#3b82f6;white-space:nowrap;font-size:11.5px">'
            + r["Dashboard Tab"] + "</td>"
        )
        key_cell  = f'<td style="{TD_BASE};color:#c4d8ee">' + r["Key Threshold"] + "</td>"
        body_html += (
            f'<tr style="background:{bg}">'
            + rule_cell + body_cell + cfr_cell + fr_cell + tab_cell + key_cell
            + "</tr>"
        )

    st.markdown(
        f'<div style="overflow-x:auto;border:1px solid #182035;border-radius:6px;margin-bottom:2rem">'
        f'<table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif">'
        f'<thead><tr>{headers_html}</tr></thead>'
        f'<tbody>{body_html}</tbody>'
        f'</table></div>',
        unsafe_allow_html=True,
    )

    # ── Detail cards ──────────────────────────────────────────────────────────
    _section("Rule Summaries")
    col_a, col_b = st.columns(2)
    for idx, r in enumerate(REG_ROWS):
        col = col_a if idx % 2 == 0 else col_b
        with col:
            st.markdown(
                f'<div style="background:#0c1525;border:1px solid #182035;border-left:3px solid #3b82f6;'
                f'border-radius:5px;padding:1rem 1.2rem;margin-bottom:1rem">'
                f'<div style="color:#deeeff;font-size:13px;font-weight:600;margin-bottom:0.25rem">'
                + r["Rule / Regulation"].replace("\n", " — ") +
                f'</div>'
                f'<div style="color:#4a6585;font-size:10px;letter-spacing:0.08em;'
                f'text-transform:uppercase;margin-bottom:0.6rem">'
                + r["Governing Body"] + "&nbsp;·&nbsp;" + r["CFR Citation"] +
                f'</div>'
                f'<div style="color:#7a9fc0;font-size:12px;line-height:1.5">'
                + r["Description"] +
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

# ══════════════════════════════════════════════════════════════════════════════
# ACCOUNTS
# ══════════════════════════════════════════════════════════════════════════════

with t11:
    _section("Client Accounts")

    all_accts = sorted(
        bor.get_customer_accounts() + bor.get_pab_accounts(),
        key=lambda a: a.client_name or a.account_id,
    )

    sel_col, _ = st.columns([3, 5])
    acct_labels = ["— All Accounts —"] + [
        f"{a.client_name}  [{a.account_id}]" if a.client_name else a.account_id
        for a in all_accts
    ]
    acct_map = {lbl: a for lbl, a in zip(acct_labels[1:], all_accts)}
    sel = sel_col.selectbox("Account", acct_labels, label_visibility="collapsed")

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    _ACCT_TH = (
        "background:#080e1c;color:#2e4460;font-size:9.5px;font-weight:700;"
        "letter-spacing:0.12em;text-transform:uppercase;padding:10px 14px;"
        "border-bottom:1px solid #182035;white-space:nowrap"
    )

    def _acct_td(val, align="left", color="#c4d8ee", bold=False):
        fw = "font-weight:600;" if bold else ""
        return (
            f'<td style="padding:8px 14px;border-bottom:1px solid #0f1d32;'
            f'font-family:Inter,sans-serif;font-size:12px;color:{color};'
            f'text-align:{align};white-space:nowrap;{fw}">{val}</td>'
        )

    def _acct_money(v):
        return f"${v:,.0f}" if v >= 0 else f"(${abs(v):,.0f})"

    def _acct_table(headers_html, body_html):
        st.markdown(
            f'<div style="overflow-x:auto;border:1px solid #182035;border-radius:6px;margin-bottom:2rem">'
            f'<table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif">'
            f'<thead><tr>{headers_html}</tr></thead>'
            f'<tbody>{body_html}</tbody>'
            f'</table></div>',
            unsafe_allow_html=True,
        )

    if sel == "— All Accounts —":
        # ── Summary table: one row per account ────────────────────────────────
        _section("Account Summary")

        col_defs = [
            ("Client",         "left"),
            ("Account ID",     "left"),
            ("Type",           "left"),
            ("Cash Balance",   "right"),
            ("Long MV",        "right"),
            ("Short MV",       "right"),
            ("Margin Debit",   "right"),
            ("Net Equity",     "right"),
            ("# Positions",    "right"),
        ]
        headers_html = "".join(
            f'<th style="{_ACCT_TH};text-align:{align}">{col}</th>'
            for col, align in col_defs
        )

        pos_count = {}
        for p in bor.positions:
            pos_count[p.account_id] = pos_count.get(p.account_id, 0) + 1

        body_html = ""
        for i, a in enumerate(all_accts):
            bg = "#0a1120" if i % 2 == 0 else "#070c18"
            eq = a.equity
            type_badge = (
                f'<span style="background:#0f1d32;color:#7a9fc0;padding:1px 7px;'
                f'border-radius:3px;font-size:10px;letter-spacing:0.06em">'
                f'{a.account_type.value}</span>'
            )
            body_html += (
                f'<tr style="background:{bg}">'
                + _acct_td(a.client_name or "—", bold=True)
                + _acct_td(a.account_id, color="#4a6585")
                + _acct_td(type_badge)
                + _acct_td(_acct_money(a.cash_balance), "right",
                           COLORS["green"] if a.cash_balance >= 0 else COLORS["red"])
                + _acct_td(f"${a.long_market_value:,.0f}", "right")
                + _acct_td(f"${a.short_market_value:,.0f}", "right",
                           COLORS["red"] if a.short_market_value > 0 else "#c4d8ee")
                + _acct_td(f"${a.margin_debit:,.0f}", "right",
                           COLORS["amber"] if a.margin_debit > 0 else "#c4d8ee")
                + _acct_td(_acct_money(eq), "right",
                           COLORS["green"] if eq >= 0 else COLORS["red"], bold=True)
                + _acct_td(str(pos_count.get(a.account_id, 0)), "right", "#7a9fc0")
                + "</tr>"
            )
        _acct_table(headers_html, body_html)

    else:
        acct = acct_map[sel]

        # ── KPI cards ─────────────────────────────────────────────────────────
        kpi_cols = st.columns(5)
        kpi_data = [
            ("Cash Balance",       acct.cash_balance,
             COLORS["green"] if acct.cash_balance >= 0 else COLORS["red"],
             "Credit" if acct.cash_balance >= 0 else "Debit balance"),
            ("Long Market Value",  acct.long_market_value,  COLORS["blue"],  "Gross long exposure"),
            ("Short Market Value", acct.short_market_value, COLORS["red"],   "Gross short exposure"),
            ("Margin Debit",       acct.margin_debit,       COLORS["amber"], "Reg T financed"),
            ("Net Equity",         acct.equity,
             COLORS["green"] if acct.equity >= 0 else COLORS["red"],
             "Long \u2212 Short \u2212 Debit"),
        ]
        for col, (label, val, accent, sub) in zip(kpi_cols, kpi_data):
            sign = "" if val >= 0 else "-"
            col.markdown(
                _kpi(label, f'{sign}${abs(val):,.0f}', sub, accent),
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        # ── Securities positions ───────────────────────────────────────────────
        _section("Securities Positions")

        acct_positions = sorted(
            [p for p in bor.positions if p.account_id == acct.account_id],
            key=lambda p: -p.market_value,
        )

        if not acct_positions:
            st.markdown(
                '<div style="text-align:center;color:#2e4460;padding:2rem 1rem;'
                'border:1px dashed #182035;border-radius:5px;font-size:11px;'
                'letter-spacing:0.08em;text-transform:uppercase">No positions in this account</div>',
                unsafe_allow_html=True,
            )
        else:
            pos_col_defs = [
                ("Description",    "left"),
                ("CUSIP",          "left"),
                ("Security Type",  "left"),
                ("Side",           "left"),
                ("Quantity",       "right"),
                ("Price",          "right"),
                ("Market Value",   "right"),
                ("Cost Basis",     "right"),
                ("Unrealized P&L", "right"),
            ]
            headers_html = "".join(
                f'<th style="{_ACCT_TH};text-align:{align}">{col}</th>'
                for col, align in pos_col_defs
            )
            body_html = ""
            for i, p in enumerate(acct_positions):
                bg = "#0a1120" if i % 2 == 0 else "#070c18"
                sec        = bor.securities.get(p.cusip)
                desc       = (sec.description if sec else p.cusip)[:50]
                sec_type   = sec.security_type.value.replace("_", " ").title() if sec else "—"
                price      = sec.price if sec else 0.0
                pnl        = (p.market_value - p.cost_basis if p.side.value == "LONG"
                              else p.cost_basis - p.market_value)
                pnl_color  = COLORS["green"] if pnl >= 0 else COLORS["red"]
                side_color = COLORS["green"] if p.side.value == "LONG" else COLORS["red"]
                side_badge = (
                    f'<span style="color:{side_color};font-weight:700;'
                    f'font-size:10px;letter-spacing:0.1em">{p.side.value}</span>'
                )
                type_badge = (
                    f'<span style="background:#0f1d32;color:#7a9fc0;padding:1px 7px;'
                    f'border-radius:3px;font-size:10px">{sec_type}</span>'
                )
                body_html += (
                    f'<tr style="background:{bg}">'
                    + _acct_td(desc, bold=True)
                    + _acct_td(p.cusip, color="#4a6585")
                    + _acct_td(type_badge)
                    + _acct_td(side_badge)
                    + _acct_td(f"{p.quantity:,.0f}", "right")
                    + _acct_td(f"${price:,.4f}", "right", "#7a9fc0")
                    + _acct_td(f"${p.market_value:,.0f}", "right")
                    + _acct_td(f"${p.cost_basis:,.0f}", "right", "#4a6585")
                    + _acct_td(
                        f'{"+" if pnl >= 0 else ""}${pnl:,.0f}',
                        "right", pnl_color, bold=True,
                    )
                    + "</tr>"
                )
            _acct_table(headers_html, body_html)
