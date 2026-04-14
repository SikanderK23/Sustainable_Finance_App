import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from textwrap import dedent

try:
    import yfinance as yf
except Exception:
    yf = None

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="QGreen — Sustainable Portfolio Advisor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS (unchanged)
# ============================================================
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(46,125,50,0.10), transparent 28%),
            radial-gradient(circle at top right, rgba(21,101,192,0.08), transparent 25%),
            linear-gradient(180deg, #f4fbf5 0%, #eef6f3 100%) !important;
        color: #132218 !important;
    }
    p, span, label, div, li, td, th, h1, h2, h3, h4, h5, h6,
    .stMarkdown, .stMarkdown p, .stMarkdown li { color: #132218 !important; }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f3fbf4 0%, #edf7f0 100%) !important;
        border-right: 1px solid rgba(46,125,50,0.10);
    }
    section[data-testid="stSidebar"] * { color: #132218 !important; }
    .stTextInput > div > div > input, .stNumberInput input,
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: rgba(255,255,255,0.88) !important;
        border: 1px solid rgba(46,125,50,0.18) !important;
        border-radius: 10px !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%) !important;
        color: white !important; border: none !important;
        border-radius: 999px !important; padding: 0.72rem 1.25rem !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 24px rgba(27,94,32,0.20) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease !important;
    }
    .stButton > button:hover { transform: translateY(-1px) scale(1.01); box-shadow: 0 14px 30px rgba(27,94,32,0.26) !important; }
    .stSlider [data-baseweb="slider"] div[role="slider"] { background: #2e7d32 !important; box-shadow: 0 0 0 4px rgba(46,125,50,0.18) !important; }
    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.78) !important; border: 1px solid rgba(46,125,50,0.12) !important;
        border-radius: 16px !important; padding: 1rem !important; box-shadow: 0 10px 28px rgba(22,34,26,0.06) !important;
    }
    div[data-testid="metric-container"] label { color: #2e7d32 !important; font-weight: 700 !important; }
    .stDataFrame, .stDataFrame * { background: rgba(255,255,255,0.85) !important; color: #132218 !important; }
    .hero {
        background: linear-gradient(135deg, rgba(27,94,32,0.97) 0%, rgba(56,142,60,0.95) 55%, rgba(38,166,154,0.92) 100%);
        color: white !important; border-radius: 24px; padding: 2.5rem 2rem 2rem 2rem;
        box-shadow: 0 18px 40px rgba(27,94,32,0.20); margin-bottom: 1.15rem; position: relative; overflow: hidden;
    }
    .hero:before {
        content: ""; position: absolute; inset: -35% auto auto 68%;
        width: 260px; height: 260px; background: rgba(255,255,255,0.10); border-radius: 50%; filter: blur(2px);
    }
    .hero h1 { font-size: 3rem; margin: 0; color: white !important; letter-spacing: 0.4px; }
    .hero p { color: rgba(255,255,255,0.95) !important; margin-top: 0.45rem; font-size: 1.05rem; max-width: 840px; }
    .glass-card {
        background: rgba(255,255,255,0.74); border: 1px solid rgba(255,255,255,0.55);
        backdrop-filter: blur(10px); border-radius: 20px; padding: 1.2rem 1.2rem 1.3rem 1.2rem;
        box-shadow: 0 12px 30px rgba(19,34,24,0.06); min-height: 225px; height: 225px;
        display: flex; flex-direction: column; justify-content: space-between;
        cursor: pointer; transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .glass-card p { flex-grow: 1; margin-bottom: 0.8rem; }
    .glass-card:hover { transform: translateY(-2px); box-shadow: 0 18px 36px rgba(19,34,24,0.12); }
    .glass-card h4 { margin: 0 0 0.4rem 0; color: #1b5e20 !important; }
    .glass-card p { color: #23412d !important; }
    .glass-card.selected {
        background: linear-gradient(145deg, #1b5e20 0%, #2e7d32 55%, #43a047 100%);
        border: 1px solid rgba(27,94,32,0.22); box-shadow: 0 16px 34px rgba(27,94,32,0.24); transform: translateY(-2px);
    }
    .glass-card.selected h4, .glass-card.selected p, .glass-card.selected .mode-badge { color: white !important; }
    .mode-badge {
        display: inline-flex; align-self: flex-start; margin-top: auto; padding: 0.28rem 0.65rem;
        border-radius: 999px; background: rgba(27,94,32,0.10); color: #1b5e20 !important;
        font-size: 0.78rem; font-weight: 800; letter-spacing: 0.2px;
    }
    .card-btn-overlay { position: relative; }
    .card-btn-overlay .stButton { position: absolute; inset: 0; opacity: 0; }
    .status-pill {
        display: inline-block; padding: 0.35rem 0.75rem; border-radius: 999px;
        background: rgba(255,255,255,0.16); color: white !important; border: 1px solid rgba(255,255,255,0.22);
        font-size: 0.88rem; font-weight: 600; margin-right: 0.45rem; margin-top: 0.55rem;
        animation: pulseGlow 3.2s ease-in-out infinite;
    }
    .soft-box {
        background: rgba(255,255,255,0.78); border: 1px solid rgba(46,125,50,0.10);
        border-radius: 18px; padding: 1rem 1.1rem; box-shadow: 0 8px 24px rgba(19,34,24,0.05); margin-bottom: 0.9rem;
    }
    .soft-box h4 { margin-top: 0; color: #1b5e20 !important; }
    .rec-box {
        background: linear-gradient(135deg, rgba(232,245,233,0.95), rgba(241,248,233,0.95));
        border-left: 6px solid #2e7d32; border-radius: 18px; padding: 1.2rem 1.35rem;
        box-shadow: 0 12px 28px rgba(46,125,50,0.10); min-height: 100%;
    }
    .rec-box h4 { color: #1b5e20 !important; margin-top: 0; }
    .note-box { background: rgba(227,242,253,0.82); border-left: 4px solid #1e88e5; border-radius: 14px; padding: 0.9rem 1rem; margin-bottom: 0.9rem; }
    .info-box { background: rgba(232,245,233,0.82); border-left: 4px solid #2e7d32; border-radius: 14px; padding: 0.9rem 1rem; margin-bottom: 0.9rem; }
    .strategy-box { background: rgba(255,255,255,0.82); border: 1px solid rgba(46,125,50,0.14); border-radius: 18px; padding: 0.95rem 1rem; margin-top: 0.75rem; box-shadow: 0 10px 24px rgba(19,34,24,0.05); }
    .strategy-title { font-weight: 800; color: #1b5e20 !important; margin-bottom: 0.2rem; }
    .hero, .glass-card, .soft-box, .rec-box, .strategy-box, .note-box { animation: fadeUp 0.65s ease both; }
    .metric-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.95rem; margin-bottom: 1rem; }
    .metric-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(239,248,241,0.92));
        border: 1px solid rgba(46,125,50,0.18); border-radius: 18px; padding: 1rem 1.05rem;
        box-shadow: 0 12px 28px rgba(19,34,24,0.08); min-height: 122px;
    }
    .metric-label { font-size: 0.90rem; font-weight: 800; color: #1b5e20 !important; margin-bottom: 0.35rem; }
    .metric-value { font-size: clamp(1.18rem, 2.2vw, 1.65rem); line-height: 1.18; font-weight: 900; color: #0f2d18 !important; white-space: normal; overflow-wrap: anywhere; word-break: break-word; }
    .metric-sub { font-size: 0.80rem; margin-top: 0.34rem; color: #355544 !important; }
    .asset-table-wrap { margin-top: 0.35rem; margin-bottom: 0.9rem; border-radius: 18px; overflow: hidden; box-shadow: 0 12px 28px rgba(19,34,24,0.09); border: 1px solid rgba(27,94,32,0.18); }
    .asset-table { width: 100%; border-collapse: collapse; background: rgba(255,255,255,0.96); color: #102516 !important; }
    .asset-table thead th { background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%); color: white !important; padding: 0.82rem 0.9rem; font-size: 0.89rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.10); }
    .asset-table tbody td { padding: 0.78rem 0.9rem; border-bottom: 1px solid rgba(27,94,50,0.10); font-size: 0.92rem; color: #102516 !important; font-weight: 600; }
    .asset-table tbody tr:nth-child(odd) { background: #f3fbf4; }
    .asset-table tbody tr:nth-child(even) { background: #e8f5e9; }
    .stTabs [data-baseweb="tab-list"] { gap: 0.45rem; background: rgba(255,255,255,0.62); padding: 0.35rem; border-radius: 999px; border: 1px solid rgba(46,125,50,0.10); box-shadow: 0 10px 24px rgba(19,34,24,0.05); width: fit-content; }
    .stTabs [data-baseweb="tab"] { background: transparent !important; border-radius: 999px !important; padding: 0.55rem 1rem !important; color: #1b5e20 !important; font-weight: 700 !important; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%) !important; color: white !important; box-shadow: 0 8px 18px rgba(27,94,32,0.18); }
    .why-box { background: linear-gradient(160deg, rgba(255,255,255,0.96), rgba(232,245,233,0.95)); border-top: 4px solid #66bb6a; border-radius: 18px; padding: 1.15rem 1.25rem; box-shadow: 0 12px 28px rgba(19,34,24,0.06); height: 100%; }
    .why-box h4 { color: #1b5e20 !important; margin-top: 0; }
    .impact-shell { background: linear-gradient(160deg, rgba(255,255,255,0.94), rgba(238,248,240,0.96)); border: 1px solid rgba(46,125,50,0.14); border-radius: 22px; padding: 1.15rem 1.2rem; box-shadow: 0 14px 30px rgba(19,34,24,0.07); margin-top: 0.9rem; margin-bottom: 1rem; }
    .impact-shell h4 { margin: 0; color: #1b5e20 !important; }
    .impact-shell p { color: #274333 !important; }
    .impact-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.9rem; margin-top: 0.85rem; margin-bottom: 0.85rem; }
    .impact-card { background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(241,248,243,0.95)); border: 1px solid rgba(46,125,50,0.14); border-radius: 18px; padding: 0.95rem 1rem; box-shadow: 0 10px 24px rgba(19,34,24,0.05); }
    .impact-kicker { font-size: 0.78rem; font-weight: 800; letter-spacing: 0.35px; text-transform: uppercase; color: #2e7d32 !important; margin-bottom: 0.35rem; }
    .impact-value { font-size: clamp(1.06rem, 2.0vw, 1.45rem); font-weight: 900; color: #10311d !important; line-height: 1.15; margin-bottom: 0.22rem; }
    .impact-detail { font-size: 0.82rem; color: #3d5f4c !important; }
    .impact-note { background: rgba(27,94,32,0.06); border-left: 4px solid #2e7d32; border-radius: 14px; padding: 0.85rem 0.95rem; margin-top: 0.25rem; }
    .impact-note ul { margin: 0.45rem 0 0.1rem 1rem; padding-left: 0.4rem; }
    .impact-topline { display: flex; flex-wrap: wrap; gap: 0.55rem; margin-top: 0.75rem; margin-bottom: 0.9rem; }
    .impact-pill { display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.45rem 0.7rem; border-radius: 999px; font-size: 0.8rem; font-weight: 800; letter-spacing: 0.2px; border: 1px solid rgba(46,125,50,0.10); background: rgba(255,255,255,0.88); color: #183b26 !important; }
    .impact-pill-positive { background: rgba(232,245,233,0.95); color: #1b5e20 !important; border-color: rgba(46,125,50,0.22); }
    .impact-pill-neutral { background: rgba(243,248,244,0.95); color: #355844 !important; border-color: rgba(85,118,97,0.18); }
    .impact-pill-caution { background: rgba(255,243,224,0.94); color: #8a4b00 !important; border-color: rgba(249,168,37,0.22); }
    .disclaimer { background: rgba(255,248,225,0.88); border-left: 4px solid #f9a825; border-radius: 12px; padding: 0.8rem 1rem; font-size: 0.88rem; color: #5f4b00 !important; margin-top: 1.3rem; }
    @keyframes fadeUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0px); } }
    @keyframes pulseGlow { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-1px); } }
    @media (max-width: 1100px) { .metric-grid { grid-template-columns: repeat(1, minmax(0, 1fr)); } .impact-grid { grid-template-columns: repeat(1, minmax(0, 1fr)); } }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"] { color-scheme: light !important; }
    div[data-baseweb="select"] * { color: #132218 !important; }
    div[data-baseweb="popover"], div[role="listbox"], ul[role="listbox"], li[role="option"] {
        background: #ffffff !important; color: #132218 !important;
    }
    div[data-baseweb="popover"] *, div[role="listbox"] *, ul[role="listbox"] *, li[role="option"] * {
        color: #132218 !important; background: transparent !important;
    }
    input, textarea, input::placeholder, textarea::placeholder {
        color: #132218 !important;
        -webkit-text-fill-color: #132218 !important;
        opacity: 1 !important;
    }
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        color: #132218 !important;
        -webkit-text-fill-color: #132218 !important;
        caret-color: #132218 !important;
        background: rgba(255,255,255,0.96) !important;
    }
    .stSelectbox label, .stTextInput label, .stNumberInput label, .stTextArea label { color: #132218 !important; }
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="popover"],
    div[role="listbox"],
    ul[role="listbox"],
    li[role="option"] {
        background: #ffffff !important;
        color: #132218 !important;
        border-color: rgba(46,125,50,0.18) !important;
    }
    div[data-baseweb="select"] [data-testid="stMarkdownContainer"],
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] svg,
    div[data-baseweb="popover"] *,
    div[role="listbox"] *,
    ul[role="listbox"] *,
    li[role="option"] * {
        color: #132218 !important;
        fill: #132218 !important;
        background: transparent !important;
        -webkit-text-fill-color: #132218 !important;
    }
    li[role="option"][aria-selected="true"],
    li[role="option"]:hover,
    div[role="option"][aria-selected="true"],
    div[role="option"]:hover {
        background: #e8f5e9 !important;
        color: #132218 !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data
def load_esg_data():
    base_dir = Path(__file__).parent
    candidates = [base_dir / "ESGMore.csv", Path("ESGMore.csv")]
    csv_path = next((p for p in candidates if p.exists()), None)
    if csv_path is None:
        return pd.DataFrame(columns=["comname", "ticker", "esg_0_100"])
    try:
        raw = pd.read_csv(csv_path)
    except Exception:
        return pd.DataFrame(columns=["comname", "ticker", "esg_0_100"])
    raw.columns = [str(c).strip().lower() for c in raw.columns]
    required_cols = {"year", "ticker", "fieldname", "valuescore"}
    if not required_cols.issubset(set(raw.columns)):
        return pd.DataFrame(columns=["comname", "ticker", "esg_0_100"])
    work = raw.copy()
    work["ticker"] = work["ticker"].astype(str).str.strip().str.upper()
    work["fieldname"] = work["fieldname"].astype(str).str.strip()
    work["year"] = pd.to_numeric(work["year"], errors="coerce")
    work["valuescore_num"] = pd.to_numeric(work["valuescore"], errors="coerce")
    score_field = "ESGScore" if "ESGScore" in set(work["fieldname"]) else "ESGCombinedScore"
    work = work[work["fieldname"] == score_field].copy()
    if work.empty:
        return pd.DataFrame(columns=["comname", "ticker", "esg_0_100"])
    grouped = (
        work.groupby(["ticker", "year"], dropna=False, as_index=False)
        .agg(esg_0_100=("valuescore_num", lambda s: float(np.nanmean(s)) * 100 if s.notna().any() else np.nan))
    )
    grouped = grouped.dropna(subset=["ticker", "esg_0_100"])
    grouped = grouped.sort_values(["ticker", "year"], ascending=[True, False]).drop_duplicates("ticker")
    grouped["comname"] = grouped["ticker"]
    grouped = grouped[["comname", "ticker", "esg_0_100"]].sort_values("ticker").reset_index(drop=True)
    return grouped


@st.cache_data
def load_impact_data():
    base_dir = Path(__file__).parent
    candidates = [base_dir / "ESGMore.csv", Path("ESGMore.csv")]
    csv_path = next((p for p in candidates if p.exists()), None)
    if csv_path is None:
        return pd.DataFrame()
    try:
        raw = pd.read_csv(csv_path)
    except Exception:
        return pd.DataFrame()
    raw.columns = [str(c).strip().lower() for c in raw.columns]
    required_cols = {"year", "ticker", "fieldname", "value", "valuescore"}
    if not required_cols.issubset(set(raw.columns)):
        return pd.DataFrame()
    score_fields = {"ESGScore", "ESGCombinedScore", "ESGCControversiesScore", "ESGEmissionsScore"}
    bool_fields = {"EmissionsTrading", "BiodiversityImpactReduction"}
    metric_fields = ["ESGScore", "ESGCombinedScore", "ESGCControversiesScore", "ESGEmissionsScore",
                     "CO2EquivalentsEmissionDirectScope1", "CO2EquivalentsEmissionIndirectScope2",
                     "CO2EquivalentsEmissionIndirectScope3", "BoardGenderDiversityPercent",
                     "BoardCulturalDiversityPercent", "EmissionsTrading", "BiodiversityImpactReduction"]
    work = raw.copy()
    work["ticker"] = work["ticker"].astype(str).str.strip().str.upper()
    work["ticker_key"] = work["ticker"].str.replace(r"[^A-Z0-9]", "", regex=True)
    work["year"] = pd.to_numeric(work["year"], errors="coerce")
    work["fieldname"] = work["fieldname"].astype(str).str.strip()
    work["value_num"] = pd.to_numeric(work["value"], errors="coerce")
    work["valuescore_num"] = pd.to_numeric(work["valuescore"], errors="coerce")
    work["bool_num"] = work["value"].astype(str).str.strip().str.lower().map({"true": 1.0, "false": 0.0})
    work["metric_value"] = np.where(work["fieldname"].isin(score_fields), work["valuescore_num"] * 100,
                                    work["value_num"])
    work.loc[work["fieldname"].isin(bool_fields), "metric_value"] = work.loc[
        work["fieldname"].isin(bool_fields), "bool_num"]
    work = work[work["fieldname"].isin(metric_fields)].copy()
    grouped = (work.groupby(["ticker", "ticker_key", "year", "fieldname"], dropna=False, as_index=False)
               .agg(metric_value=("metric_value", "mean")))
    wide = grouped.pivot_table(index=["ticker", "ticker_key", "year"], columns="fieldname", values="metric_value",
                               aggfunc="mean").reset_index()
    candidate_cols = [c for c in metric_fields if c in wide.columns]
    wide["impact_coverage"] = wide[candidate_cols].notna().sum(axis=1) if candidate_cols else 0
    wide = wide.sort_values(["ticker_key", "impact_coverage", "year"], ascending=[True, False, False])
    return wide


esg_df = load_esg_data()
company_names = esg_df["comname"].tolist()
impact_wide = load_impact_data()
impact_lookup = {}
if not impact_wide.empty:
    for rec in impact_wide.to_dict(orient="records"):
        key = str(rec.get("ticker_key", "")).strip().upper()
        if key:
            impact_lookup.setdefault(key, []).append(rec)
impact_keys = sorted(impact_lookup.keys())


# ============================================================
# PORTFOLIO MATH — CORRECT TWO-STAGE APPROACH
# ============================================================

@st.cache_data(show_spinner=False)
def fetch_returns_and_corr(ticker1: str, ticker2: str):
    """Fetch annualised return, vol, and pairwise correlation from Yahoo Finance."""
    if yf is None:
        return None
    try:
        tickers = [ticker1, ticker2]
        hist = yf.download(tickers, period="3y", interval="1d", auto_adjust=True, progress=False)
        if hist is None or hist.empty:
            return None
        if isinstance(hist.columns, pd.MultiIndex):
            close = hist["Close"]
        else:
            close = hist[["Close"]]
            close.columns = tickers
        close = close.dropna(how="all")
        if close.shape[0] < 60:
            return None
        rets = close.pct_change().dropna()
        stats = {}
        for t in tickers:
            if t not in rets.columns:
                return None
            s = rets[t].dropna()
            if len(s) < 60:
                return None
            ann_ret = float(s.mean() * 252)
            ann_vol = float(s.std() * np.sqrt(252))
            if not np.isfinite(ann_ret) or not np.isfinite(ann_vol) or ann_vol <= 0:
                return None
            stats[t] = {"return": ann_ret, "sd": ann_vol}
        aligned = rets[[ticker1, ticker2]].dropna()
        if len(aligned) < 30:
            corr_val = 0.3
        else:
            corr_val = float(aligned.corr().iloc[0, 1])
            if not np.isfinite(corr_val):
                corr_val = 0.3
        return {"stats": stats, "corr": corr_val, "source": "Yahoo Finance (3yr)"}
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def fetch_single_market_stats(ticker: str):
    if yf is None or not ticker:
        return None
    try:
        hist = yf.download(ticker, period="3y", interval="1d", auto_adjust=True, progress=False)
        if hist is None or hist.empty or "Close" not in hist.columns:
            return None
        close = hist["Close"].dropna()
        if len(close) < 60:
            return None
        rets = close.pct_change().dropna()
        ann_return = float(rets.mean() * 252)
        ann_vol = float(rets.std() * np.sqrt(252))
        if not np.isfinite(ann_return) or not np.isfinite(ann_vol) or ann_vol <= 0:
            return None
        return {"return": ann_return, "sd": ann_vol}
    except Exception:
        return None


def estimate_asset_characteristics(esg_score: float, style: str):
    """Neutral fallback estimates used only when live market data is unavailable.
    These estimates are intentionally independent of ESG score so the app does not
    mechanically reward greener assets in the financial inputs.
    """
    if style == "Conservative 🛡️":
        ret, sd = 0.06, 0.10
    elif style == "Balanced ⚖️":
        ret, sd = 0.08, 0.14
    else:
        ret, sd = 0.10, 0.18
    return round(ret, 4), round(sd, 4)


def build_asset(name, ticker, ret, sd, esg, source, mode_label):
    return {
        "name": name, "ticker": ticker,
        "ret": float(ret), "sd": float(sd), "esg": float(esg),
        "source": source, "mode": mode_label,
        "impact_profile": get_impact_profile(ticker, esg, name),
        "impact_available": bool(get_impact_profile(ticker, esg, name)),
    }


def get_asset_from_row(row, style: str, mode_label: str, market_override=None):
    if market_override:
        ret = market_override["return"]
        sd = market_override["sd"]
        source = "Yahoo Finance (3yr)"
    else:
        mkt = fetch_single_market_stats(row["ticker"])
        if mkt:
            ret, sd, source = mkt["return"], mkt["sd"], "Yahoo Finance (3yr)"
        else:
            ret, sd = estimate_asset_characteristics(row["esg_0_100"], style)
            source = "QGreen estimate"
    raw_name = str(row.get("comname", row["ticker"])).strip()
    raw_ticker = str(row["ticker"]).strip().upper()
    display_name = raw_ticker if raw_name.upper() == raw_ticker else raw_name.title()
    return build_asset(display_name, raw_ticker, ret, sd, row["esg_0_100"], source, mode_label)


def _golden_section_min(f, a, b, tol=1e-9, max_iter=300):
    gr = (np.sqrt(5) + 1) / 2
    c = b - (b - a) / gr
    d = a + (b - a) / gr
    for _ in range(max_iter):
        if abs(b - a) < tol:
            break
        if f(c) < f(d):
            b = d
        else:
            a = c
        c = b - (b - a) / gr
        d = a + (b - a) / gr
    return (a + b) / 2


def portfolio_moments(w1, r1, r2, s1, s2, corr):
    w2 = 1.0 - w1
    ret = w1 * r1 + w2 * r2
    var = w1 ** 2 * s1 ** 2 + w2 ** 2 * s2 ** 2 + 2 * corr * w1 * w2 * s1 * s2
    sd = float(np.sqrt(max(var, 1e-12)))
    return float(ret), sd


def esg_constrained_w1_bounds(esg1, esg2, min_esg):
    diff = esg1 - esg2
    rhs = min_esg - esg2
    if abs(diff) < 1e-6:
        if esg1 >= min_esg - 1e-6:
            return 0.0, 1.0
        else:
            return None
    if diff > 0:
        w1_lo = rhs / diff
        return max(0.0, w1_lo), 1.0
    else:
        w1_hi = rhs / diff
        return 0.0, min(1.0, w1_hi)


def optimise_portfolio(asset1, asset2, gamma, lambda_esg, corr, rf, esg_mode, esg_threshold, min_esg_score=0.0):
    """Benchmark implementation of the lecturer's objective.

    Maximise over risky-asset weights x >= 0 with no sum-to-one constraint:
        x'(μ-r_f 1) - (γ/2) x'Σx + λ s̄
    where s̄ = x's / x'1 is the risky-portfolio-average ESG score.

    For two risky assets, write x = α w where w = (w1, 1-w1), α >= 0.
    For any fixed risky mix w, the optimal risky scale is:
        α* = max(0, μ_p^ex / (γ σ_p^2))
    with no upper cap, so borrowing at the risk-free rate is allowed.
    """
    r1, r2 = asset1["ret"], asset2["ret"]
    s1, s2 = asset1["sd"], asset2["sd"]
    esg1, esg2 = asset1["esg"], asset2["esg"]
    lam = float(lambda_esg)
    if "Finance as Usual" in esg_mode:
        lam = 0.0

    mu1_ex = r1 - rf
    mu2_ex = r2 - rf
    e1_norm = esg1 / 100.0
    e2_norm = esg2 / 100.0

    def risky_mix_objective(w1):
        w2 = 1.0 - w1
        mu_p_ex = w1 * mu1_ex + w2 * mu2_ex
        var_p = max(w1 ** 2 * s1 ** 2 + w2 ** 2 * s2 ** 2 + 2 * corr * w1 * w2 * s1 * s2, 1e-14)
        s_bar = w1 * e1_norm + w2 * e2_norm
        alpha_star = max(0.0, mu_p_ex / (gamma * var_p)) if gamma > 0 else 0.0
        return alpha_star * mu_p_ex - 0.5 * gamma * (alpha_star ** 2) * var_p + lam * s_bar

    N = 4001
    w_grid = np.linspace(0.0, 1.0, N)
    obj_vals = np.array([risky_mix_objective(w) for w in w_grid])
    best_idx = int(np.argmax(obj_vals))
    lo = w_grid[max(0, best_idx - 1)]
    hi = w_grid[min(N - 1, best_idx + 1)]
    if hi - lo > 1e-12:
        w1_tang = float(_golden_section_min(lambda w: -risky_mix_objective(w), lo, hi))
    else:
        w1_tang = float(w_grid[best_idx])
    w1_tang = float(np.clip(w1_tang, 0.0, 1.0))
    w2_tang = 1.0 - w1_tang

    ret_tang, sd_tang = portfolio_moments(w1_tang, r1, r2, s1, s2, corr)
    mu_p_ex = ret_tang - rf
    var_tang = max(sd_tang ** 2, 1e-14)
    alpha = max(0.0, mu_p_ex / (gamma * var_tang)) if gamma > 0 else 0.0
    w_rf = 1.0 - alpha

    w1_opt = alpha * w1_tang
    w2_opt = alpha * w2_tang
    ret_opt = w_rf * rf + w1_opt * r1 + w2_opt * r2
    sd_opt = np.sqrt(max(w1_opt ** 2 * s1 ** 2 + w2_opt ** 2 * s2 ** 2 + 2 * corr * w1_opt * w2_opt * s1 * s2, 0.0))
    sharpe_tang = mu_p_ex / sd_tang if sd_tang > 1e-10 else 0.0
    sharpe_opt = (ret_opt - rf) / sd_opt if sd_opt > 1e-10 else 0.0

    tang_esg = w1_tang * esg1 + w2_tang * esg2
    esg_opt = tang_esg
    esg_opt_total = (w1_opt * esg1 + w2_opt * esg2) / max(alpha, 1e-12) if alpha > 1e-12 else np.nan

    weights = np.linspace(0.0, 1.0, 500)
    all_ret = np.array([portfolio_moments(w, r1, r2, s1, s2, corr)[0] for w in weights])
    all_std = np.array([portfolio_moments(w, r1, r2, s1, s2, corr)[1] for w in weights])
    all_esg = np.array([w * esg1 + (1 - w) * esg2 for w in weights])
    all_sharpe = np.where(all_std > 0, (all_ret - rf) / all_std, -np.inf)

    return {
        "asset1": asset1,
        "asset2": asset2,
        "w1_tang": w1_tang,
        "w2_tang": w2_tang,
        "ret_tang": ret_tang,
        "sd_tang": sd_tang,
        "sharpe_tang": sharpe_tang,
        "tang_esg": tang_esg,
        "w_rf": w_rf,
        "alpha": alpha,
        "w1": w1_opt,
        "w2": w2_opt,
        "ret_opt": ret_opt,
        "sd_opt": sd_opt,
        "esg_opt": esg_opt,
        "esg_opt_total": esg_opt_total,
        "sharpe_opt": sharpe_opt,
        "weights": weights,
        "all_ret": all_ret,
        "all_std": all_std,
        "all_esg": all_esg,
        "all_sharpe": all_sharpe,
        "rf": rf,
        "gamma": gamma,
        "lambda_esg": lam,
        "excluded": [],
        "corr": corr,
        "min_esg_score": 0.0,
        "esg_threshold": 0.0,
    }


# ============================================================
# ESG & RISK HELPERS
# ============================================================
def derive_esg_preferences(answers):
    total = int(sum(answers))
    lambda_esg = total / 21.0
    if total == 0:
        model_name = "⚪ Finance as Usual Model"
        model_short = "Finance as Usual"
        description = "λ = 0. The app solves the pure mean-variance benchmark with no ESG taste term."
    elif total <= 7:
        model_name = "🌱 Sustainable Finance Model 1.0 — Light ESG Preference"
        model_short = "Light ESG Preference"
        description = "A low positive λ adds a modest ESG taste term to the same benchmark optimisation problem."
    elif total <= 14:
        model_name = "🌿 Sustainable Finance Model 2.0 — Moderate ESG Preference"
        model_short = "Moderate ESG Preference"
        description = "A medium λ places more weight on greener risky-asset mixes while still respecting the same objective function."
    else:
        model_name = "🌍 Sustainable Finance Model 3.0 — Strong ESG Preference"
        model_short = "Strong ESG Preference"
        description = "A high λ can rationally push the solution toward a corner allocation in the greener asset."
    return {"total": total, "lambda": lambda_esg, "model_name": model_name, "model_short": model_short,
            "description": description}


def risk_profile_from_quiz(score: int):
    if score <= 4:
        return 8, "Conservative 🛡️"
    if score <= 6:
        return 4, "Balanced ⚖️"
    return 2, "Growth-Oriented 🚀"


# ============================================================
# IMPACT / DISPLAY HELPERS
# ============================================================
def ticker_key_fn(value):
    return "".join(ch for ch in str(value).upper() if ch.isalnum())


def ticker_candidates(value):
    raw = str(value).upper().strip()
    candidates = []

    def add_c(v):
        k = ticker_key_fn(v)
        if k and k not in candidates:
            candidates.append(k)

    add_c(raw)
    for sep in [".", ":", "/", " ", "-", "_"]:
        if sep in raw:
            add_c(raw.split(sep)[0])
    if raw.endswith((".OQ", ".N", ".L", ".PA", ".DE", ".HK", ".TO", ".AX", ".MI")):
        add_c(raw.split(".")[0])
    return candidates


def get_impact_profile(ticker, esg_hint=None, name_hint=None):
    def choose_best(profiles, match_type):
        if not profiles:
            return {}
        if len(profiles) == 1:
            e = dict(profiles[0]);
            e["match_type"] = match_type;
            e["match_quality"] = "single_candidate";
            return e
        scored = [(p, abs(float(p.get("ESGScore", 0)) - float(esg_hint)) if esg_hint is not None and pd.notna(
            p.get("ESGScore")) else None) for p in profiles]
        with_diff = [(p, d) for p, d in scored if d is not None]
        if with_diff:
            with_diff.sort(key=lambda x: x[1])
            best, best_diff = with_diff[0]
            e = dict(best);
            e["esg_diff"] = best_diff;
            e["match_type"] = match_type + "_esg_resolved"
            e["match_quality"] = "high_confidence" if best_diff <= 2 else (
                "medium_confidence" if best_diff <= 5 else "low_confidence")
            return e
        e = dict(profiles[0]);
        e["match_type"] = match_type;
        e["match_quality"] = "multi_no_hint";
        return e

    exact = []
    for k in ticker_candidates(ticker):
        ps = impact_lookup.get(k)
        if ps: exact.extend(ps)
    chosen = choose_best(exact, "exact")
    if chosen: return chosen
    prefix = []
    for k in ticker_candidates(ticker):
        ms = [ik for ik in impact_keys if ik.startswith(k) or k.startswith(ik)]
        ms = [ik for ik in ms if abs(len(ik) - len(k)) <= 4]
        if len(ms) == 1: prefix.extend(impact_lookup[ms[0]])
    return choose_best(prefix, "prefix")


def weighted_metric(values, weights):
    arr = np.array(values, dtype=float)
    w = np.array(weights, dtype=float)
    mask = np.isfinite(arr)
    if not mask.any(): return np.nan, 0.0
    uw = float(w[mask].sum())
    return (float(np.dot(arr[mask], w[mask]) / uw), uw) if uw > 0 else (np.nan, 0.0)


def safe_sum_numeric(values):
    vals = [float(v) for v in values if pd.notna(v)]
    return float(np.sum(vals)) if vals else np.nan


def format_tco2e(value):
    if pd.isna(value): return "Not available"
    av = abs(float(value))
    if av >= 1e9: return f"{value / 1e9:.2f}bn tCO₂e"
    if av >= 1e6: return f"{value / 1e6:.2f}m tCO₂e"
    if av >= 1e3: return f"{value / 1e3:.1f}k tCO₂e"
    return f"{value:,.0f} tCO₂e"


def format_number_or_na(value, suffix="", decimals=2):
    return "Not available" if pd.isna(value) else f"{float(value):,.{decimals}f}{suffix}"


def format_percent_or_na(value, decimals=1):
    return "Not available" if pd.isna(value) else f"{float(value):.{decimals}f}%"


def compute_impact_snapshot(asset1, asset2, w1, w2):
    p1 = get_impact_profile(asset1.get("ticker"))
    p2 = get_impact_profile(asset2.get("ticker"))
    cov = (w1 if bool(p1) else 0.0) + (w2 if bool(p2) else 0.0)
    if cov <= 0:
        return {"available": False, "message": "No LSEG impact data matched for the selected tickers."}

    def gv(p, *keys):
        return safe_sum_numeric([p.get(k) for k in keys]) if p else np.nan

    s12_1 = gv(p1, "CO2EquivalentsEmissionDirectScope1", "CO2EquivalentsEmissionIndirectScope2")
    s12_2 = gv(p2, "CO2EquivalentsEmissionDirectScope1", "CO2EquivalentsEmissionIndirectScope2")
    s123_1 = gv(p1, "CO2EquivalentsEmissionDirectScope1", "CO2EquivalentsEmissionIndirectScope2",
                "CO2EquivalentsEmissionIndirectScope3")
    s123_2 = gv(p2, "CO2EquivalentsEmissionDirectScope1", "CO2EquivalentsEmissionIndirectScope2",
                "CO2EquivalentsEmissionIndirectScope3")
    s12_p, _ = weighted_metric([s12_1, s12_2], [w1, w2])
    s123_p, _ = weighted_metric([s123_1, s123_2], [w1, w2])
    em_p, _ = weighted_metric(
        [p1.get("ESGEmissionsScore", np.nan) if p1 else np.nan, p2.get("ESGEmissionsScore", np.nan) if p2 else np.nan],
        [w1, w2])
    gd_p, _ = weighted_metric([p1.get("BoardGenderDiversityPercent", np.nan) if p1 else np.nan,
                               p2.get("BoardGenderDiversityPercent", np.nan) if p2 else np.nan], [w1, w2])
    et_p, _ = weighted_metric([100 * p1.get("EmissionsTrading", np.nan) if p1 else np.nan,
                               100 * p2.get("EmissionsTrading", np.nan) if p2 else np.nan], [w1, w2])
    bd_p, _ = weighted_metric([100 * p1.get("BiodiversityImpactReduction", np.nan) if p1 else np.nan,
                               100 * p2.get("BiodiversityImpactReduction", np.nan) if p2 else np.nan], [w1, w2])
    insights = []
    if pd.notna(s12_p): insights.append(f"Weighted Scope 1+2 emissions: {format_tco2e(s12_p)}.")
    if pd.notna(s123_p): insights.append(
        f"Weighted Scope 1+2+3 emissions: {format_tco2e(s123_p)} (where Scope 3 data is available).")
    if pd.notna(em_p): insights.append(f"Weighted LSEG emissions score: {em_p:.1f}/100.")
    if pd.notna(gd_p): insights.append(f"Weighted board gender diversity: {gd_p:.1f}%.")
    if pd.notna(et_p): insights.append(f"{et_p:.0f}% of risky portfolio weight sits in emissions-trading participants.")
    if pd.notna(bd_p): insights.append(
        f"{bd_p:.0f}% of risky portfolio weight has biodiversity-impact reduction coverage.")
    return {"available": True, "scope12_port": s12_p, "scope123_port": s123_p, "emissions_score_port": em_p,
            "gender_diversity_port": gd_p, "emissions_trading_share": et_p, "biodiversity_share": bd_p,
            "coverage_weight": cov * 100, "insights": insights}


def pick_auto_pair(df, style, lambda_esg, esg_mode, esg_threshold, min_esg_score=0.0):
    """Stable auto-pair for demo use.
    Chooses one lower-ESG and one higher-ESG asset so changing λ mainly moves weights,
    rather than constantly changing the investable pair itself.
    """
    work = df.dropna(subset=["esg_0_100"]).sort_values("esg_0_100").reset_index(drop=True)
    if len(work) < 2:
        return None, None
    low_idx = max(0, int(len(work) * 0.2))
    high_idx = min(len(work) - 1, int(len(work) * 0.8))
    anchor = work.iloc[low_idx]
    companion = work.iloc[high_idx]
    if anchor["comname"] == companion["comname"]:
        companion = work.iloc[-1]
    return anchor, companion


def build_portfolio_narrative(client_name, result, asset1, asset2, esg_mode, risk_label, esg_threshold,
                              min_esg_score=0.0):
    w_rf = result["w_rf"]
    alpha = result["alpha"]
    w1_tang = result["w1_tang"]
    w2_tang = result["w2_tang"]

    lam_display = result["lambda_esg"]
    if result["excluded"]:
        stage1 = f"The exclusion screen removed {', '.join(result['excluded'])} (ESG score below {esg_threshold:.0f}), so the risky portfolio consists of the remaining asset only."
    elif "Finance as Usual" in esg_mode or lam_display == 0.0:
        stage1 = "λ = 0: no ESG preference. The optimal risky mix maximises the Sharpe ratio (pure mean-variance tangency) with no ESG tilt."
    else:
        stage1 = (
            f"λ = {lam_display:.3f}: the ESG preference enters the objective directly as λ·s̄, "
            f"where s̄ is the portfolio-average ESG score. "
            f"The optimal risky mix was found by maximising "
            f"μ_p²/(2γσ²_p) + λ·s̄ over w₁ ∈ [0, 1]. "
            f"This tilts the portfolio toward the higher-ESG asset at the cost of a lower Sharpe ratio."
        )
        if min_esg_score > 0 and ("Best-in-Class" in esg_mode or "ESG Integration" in esg_mode):
            stage1 += f" An additional hard ESG floor of {min_esg_score:.0f} was also enforced."

    if alpha < 0.05:
        stage2 = f"Your risk profile ({risk_label}) is very conservative — nearly all capital ({w_rf * 100:.0f}%) is held in the risk-free asset."
    elif w_rf < 0.05:
        stage2 = f"Your risk profile ({risk_label}) is aggressive — almost all capital ({alpha * 100:.0f}%) is in the tangency portfolio."
    elif w_rf > 0.55:
        stage2 = f"Your risk profile ({risk_label}) is conservative: {w_rf * 100:.0f}% in the risk-free asset, {alpha * 100:.0f}% in the tangency portfolio."
    else:
        stage2 = f"Your risk profile ({risk_label}) balances: {w_rf * 100:.0f}% in the risk-free asset and {alpha * 100:.0f}% in the tangency portfolio."

    html = f"""
<div class="why-box">
    <h4>Why this portfolio?</h4>
    <p><strong>{client_name}</strong>, your recommendation follows a two-stage process rooted in Modern Portfolio Theory (Pedersen et al. 2021).</p>
    <p><strong>Stage 1 — ESG-constrained tangency portfolio:</strong> {stage1}</p>
    <p>Tangency composition: <strong>{w1_tang * 100:.1f}% {asset1['name']}</strong> · <strong>{w2_tang * 100:.1f}% {asset2['name']}</strong>.</p>
    <p><strong>Stage 2 — Risk-free allocation:</strong> {stage2}</p>
</div>"""
    return html


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
if "portfolio_built" not in st.session_state:
    st.session_state.portfolio_built = False
    st.session_state.result = None
    st.session_state.asset1 = None
    st.session_state.asset2 = None
    st.session_state.gamma = None
    st.session_state.lambda_esg = None
    st.session_state.risk_label = None
    st.session_state.esg_mode = None
    st.session_state.corr_live = None
    st.session_state.corr_source = None

mode_options = [
    "A) I enter everything manually",
    "B) I choose my assets",
    "C) Let QGreen choose for me",
]
if "mode" not in st.session_state:
    st.session_state["mode"] = mode_options[0]

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="hero">
    <h1>🌿 QGreen</h1>
    <p>QGreen turns your risk appetite and sustainability values into a rigorous, theory-grounded portfolio — combining the tangency portfolio with the risk-free asset according to your preferences.</p>
    <div>
        <span class="status-pill">Innovation</span>
        <span class="status-pill">Sustainability</span>
        <span class="status-pill">Precision</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── CLICKABLE MODE CARDS ──────────────────────────────────────────────────────
card_specs = [
    ("A) Full Manual", "Enter return, risk, ESG scores and correlation directly for complete control.", "Full control",
     mode_options[0]),
    ("B) Choose Your Assets", "You pick two assets by ticker and QGreen handles the full optimisation.",
     "Directed choice", mode_options[1]),
    ("C) Auto Portfolio", "QGreen selects two companies for you based on your risk profile and ESG preferences.",
     "Automated", mode_options[2]),
]
m1, m2, m3 = st.columns(3)
for col, (title, desc, badge, mode_value) in zip((m1, m2, m3), card_specs):
    selected_class = " selected" if st.session_state["mode"] == mode_value else ""
    col.markdown(f"""
<div class='glass-card{selected_class}'>
    <h4>{title}</h4>
    <p>{desc}</p>
    <span class='mode-badge'>{badge}</span>
</div>""", unsafe_allow_html=True)
    if col.button("Select" if st.session_state["mode"] != mode_value else "✓ Selected", key=f"mode_btn_{mode_value}",
                  use_container_width=True):
        st.session_state["mode"] = mode_value
        st.session_state.portfolio_built = False  # Reset when changing mode
        st.rerun()

mode = st.session_state["mode"]

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Portfolio Builder")
    client_name = st.text_input("Client name", value=st.session_state.get("client_name", ""),
                                placeholder="Enter client name")
    st.session_state["client_name"] = client_name

    # ── INPUT METHOD TOGGLE ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🎛️ Input Method")
    input_method = st.radio(
        "How would you like to set preferences?",
        ["Guided Quiz (Recommended)", "Advanced: Direct Parameters"],
        index=0,
        help="Quiz is best for most users. Advanced mode lets you directly set the mathematical coefficients γ (risk aversion) and λ (ESG taste)."
    )

    use_quiz = (input_method == "Guided Quiz (Recommended)")

    # Initialize variables
    gamma = 4.0
    lambda_esg = 0.0
    risk_label = "Balanced ⚖️"
    esg_mode = "⚪ Finance as Usual Model"
    esg_threshold = 0.0
    min_esg_score = 0.0

    # ── RISK & ESG INPUTS ───────────────────────────────────────────────────
    if use_quiz:
        st.markdown("---")
        st.markdown("### 📊 Step 1 — How do you feel about risk?")
        q1 = st.radio("If your portfolio drops 20%, you:",
                      ["Sell to cut losses", "Hold and wait it out", "Buy more — great opportunity"], index=1)
        q2 = st.radio("Your investment horizon is:", ["Under 2 years", "2–10 years", "Over 10 years"], index=1)
        q3 = st.radio("Your main goal is:",
                      ["Protecting what I have", "Balanced growth and stability", "Maximum long-term growth"], index=1)
        score_map = {
            "Sell to cut losses": 1, "Hold and wait it out": 2, "Buy more — great opportunity": 3,
            "Under 2 years": 1, "2–10 years": 2, "Over 10 years": 3,
            "Protecting what I have": 1, "Balanced growth and stability": 2, "Maximum long-term growth": 3,
        }
        quiz_score = score_map[q1] + score_map[q2] + score_map[q3]
        gamma, risk_label = risk_profile_from_quiz(quiz_score)
        st.success(f"Risk profile: {risk_label} (γ≈{gamma})")

        st.markdown("---")
        st.markdown("### 🌱 Step 2 — How much do you care about ESG?")
        st.caption("Slide each answer from 0 (not important) to 3 (very important).")
        q_esg = [
            st.slider("Avoiding controversial sectors entirely", 0, 3, 1, help="0 = don't care, 3 = very important"),
            st.slider("Comparing firms relative to their industry peers", 0, 3, 1),
            st.slider("Investments contributing to positive E/S outcomes", 0, 3, 1),
            st.slider("Accepting slightly lower returns for stronger ESG", 0, 3, 1),
            st.slider("Environmental factors (emissions, climate)", 0, 3, 1),
            st.slider("Social factors (labour, diversity)", 0, 3, 1),
            st.slider("Governance factors (board, transparency)", 0, 3, 1),
        ]
        esg_pref = derive_esg_preferences(q_esg)
        lambda_esg = esg_pref["lambda"]
        esg_mode = esg_pref["model_name"]

        st.markdown(f"""
<div class="strategy-box">
    <div class="strategy-title">Your ESG model</div>
    <div><strong>{esg_mode}</strong></div>
    <div style="margin-top:0.35rem;">{esg_pref['description']}</div>
</div>""", unsafe_allow_html=True)

        esg_threshold = 0.0
        min_esg_score = 0.0
        st.caption(
            "This benchmark version uses the lecturer's objective directly. ESG enters only through λ·s̄, with no extra exclusion or minimum-ESG constraints.")

    else:
        # ADVANCED MODE
        st.markdown("---")
        st.markdown("### 📊 Risk Aversion Coefficient (γ)")
        st.caption(
            "Higher γ = more risk averse. Doubling γ approximately halves your allocation to risky assets (Audit Check 1).")
        gamma = st.slider(
            "γ (gamma)",
            min_value=0.5,
            max_value=10.0,
            value=4.0,
            step=0.5,
            help="Risk aversion parameter in the utility function U = E[R] - ½γσ² + λs̄. "
                 "Typical values: 2 (aggressive), 4 (balanced), 8 (conservative)."
        )
        risk_label = f"Advanced (γ={gamma})"
        st.info(f"Risk profile: {risk_label}")

        st.markdown("---")
        st.markdown("### 🌱 ESG Taste Parameter (λ)")
        st.caption(
            "Weight on ESG in the objective function. Higher λ = stronger preference for green assets (Audit Check 2).")
        lambda_esg = st.slider(
            "λ (lambda)",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.01,
            help="ESG taste parameter. λ=0: pure finance (maximize Sharpe). "
                 "λ≈0.3: moderate ESG tilt. λ>0.5: strong ESG preference (may sacrifice returns)."
        )

        if lambda_esg == 0:
            esg_mode = "⚪ Finance as Usual Model"
        elif lambda_esg <= 0.33:
            esg_mode = "🌱 Sustainable Finance Model 1.0 — Light ESG Preference"
        elif lambda_esg <= 0.67:
            esg_mode = "🌿 Sustainable Finance Model 2.0 — Moderate ESG Preference"
        else:
            esg_mode = "🌍 Sustainable Finance Model 3.0 — Strong ESG Preference"

        st.info(f"ESG Model: {esg_mode.split('—')[-1].strip() if '—' in esg_mode else esg_mode}")
        esg_threshold = 0.0
        min_esg_score = 0.0
        st.caption("Benchmark mode: no extra ESG screens or minimum-ESG constraints are applied.")

    st.markdown("---")
    st.markdown("### 💰 Risk-free rate")
    rf = st.number_input("Risk-free rate (%)", min_value=0.0, max_value=20.0, value=4.5, step=0.1) / 100

    run = st.button("🚀 Build my portfolio", type="primary", use_container_width=True)

display_client_name = client_name.strip() if client_name and client_name.strip() else "Client"

# ============================================================
# MODE B & C INPUT FORMS (Fixed: outside needs_build gate)
# ============================================================
# These must render BEFORE the calculation block so the widgets exist
# when the user clicks "Run"

if mode.startswith("B"):
    st.subheader("Choose your two assets")
    c1, c2 = st.columns(2)
    with c1:
        name1 = st.selectbox("Asset 1", company_names, key="b_company1")
    with c2:
        available2 = [n for n in company_names if n != name1]
        name2 = st.selectbox("Asset 2", available2, key="b_company2")
    # Store for calculation
    st.session_state.mode_b_assets = (name1, name2)

elif mode.startswith("A"):
    st.subheader("Enter both assets manually")
    c1, c2 = st.columns(2)
    with c1:
        n1 = st.text_input("Asset 1 name", "Asset 1", key="c_name1")
        t1 = st.text_input("Asset 1 ticker", "A1", key="c_ticker1")
        r1 = st.number_input("Asset 1 expected return (%)", 0.0, 100.0, 10.0, 0.1, key="c_r1") / 100
        sd1 = st.number_input("Asset 1 volatility / SD (%)", 0.1, 100.0, 18.0, 0.1, key="c_sd1") / 100
        esg1_val = st.number_input("Asset 1 ESG score (0–100)", 0.0, 100.0, 65.0, 0.1, key="c_esg1")
    with c2:
        n2 = st.text_input("Asset 2 name", "Asset 2", key="c_name2")
        t2 = st.text_input("Asset 2 ticker", "A2", key="c_ticker2")
        r2 = st.number_input("Asset 2 expected return (%)", 0.0, 100.0, 7.0, 0.1, key="c_r2") / 100
        sd2 = st.number_input("Asset 2 volatility / SD (%)", 0.1, 100.0, 12.0, 0.1, key="c_sd2") / 100
        esg2_val = st.number_input("Asset 2 ESG score (0–100)", 0.0, 100.0, 85.0, 0.1, key="c_esg2")
    corr_input = st.number_input("Correlation between assets (ρ)", -1.0, 1.0, 0.30, 0.05, key="c_corr")

    # Store for calculation
    st.session_state.mode_c_assets = {
        "asset1": build_asset(n1, t1, r1, sd1, esg1_val, "Manual input", "C"),
        "asset2": build_asset(n2, t2, r2, sd2, esg2_val, "Manual input", "C"),
        "corr": corr_input
    }

# ============================================================
# BUILD ASSETS & OPTIMIZE
# ============================================================
asset1 = asset2 = None
corr_live = None
corr_source = "Manual"
mode_explainer = ""
data_message = ""

# Check if we need to build portfolio
needs_build = run or st.session_state.portfolio_built

if run:
    # Store current parameters in session state
    st.session_state.gamma = gamma
    st.session_state.lambda_esg = lambda_esg
    st.session_state.risk_label = risk_label
    st.session_state.esg_mode = esg_mode
    st.session_state.esg_threshold = esg_threshold
    st.session_state.min_esg_score = min_esg_score
    st.session_state.rf = rf
    st.session_state.use_quiz = use_quiz

if mode.startswith("C") and needs_build:
    mode_explainer = "QGreen selected two companies based on your ESG preferences and risk profile."
    if len(esg_df) >= 2:
        a1_row, a2_row = pick_auto_pair(esg_df, risk_label, lambda_esg, esg_mode, esg_threshold, min_esg_score)
        if a1_row is not None and a2_row is not None:
            with st.spinner("Fetching live market data and correlation…"):
                live = fetch_returns_and_corr(a1_row["ticker"], a2_row["ticker"])
            if live:
                asset1 = get_asset_from_row(a1_row, risk_label, "A", live["stats"].get(a1_row["ticker"]))
                asset2 = get_asset_from_row(a2_row, risk_label, "A", live["stats"].get(a2_row["ticker"]))
                corr_live = live["corr"]
                corr_source = live["source"]
                data_message = f"Return, volatility, and correlation pulled from {corr_source}."
            else:
                asset1 = get_asset_from_row(a1_row, risk_label, "A")
                asset2 = get_asset_from_row(a2_row, risk_label, "A")
                corr_live = 0.30
                corr_source = "QGreen default (0.30)"
                data_message = "Live market data unavailable — using QGreen estimates with a default correlation of 0.30."

elif mode.startswith("B") and needs_build:
    # Retrieve from session state (widgets above stored them)
    if "mode_b_assets" in st.session_state:
        name1, name2 = st.session_state.mode_b_assets
        row1 = esg_df.loc[esg_df["comname"] == name1].iloc[0]
        row2 = esg_df.loc[esg_df["comname"] == name2].iloc[0]
        with st.spinner("Fetching live market data and correlation…"):
            live = fetch_returns_and_corr(row1["ticker"], row2["ticker"])
        if live:
            asset1 = get_asset_from_row(row1, risk_label, "B", live["stats"].get(row1["ticker"]))
            asset2 = get_asset_from_row(row2, risk_label, "B", live["stats"].get(row2["ticker"]))
            corr_live = live["corr"]
            corr_source = live["source"]
            data_message = f"Return, volatility, and correlation pulled from {corr_source}."
        else:
            asset1 = get_asset_from_row(row1, risk_label, "B")
            asset2 = get_asset_from_row(row2, risk_label, "B")
            corr_live = 0.30
            corr_source = "QGreen default (0.30)"
            data_message = "Live market data unavailable — using QGreen estimates with a default correlation of 0.30."
        mode_explainer = "You picked two assets and QGreen fetched live data and computed the optimal portfolio."

elif mode.startswith("A") and needs_build:
    if "mode_c_assets" in st.session_state:
        asset1 = st.session_state.mode_c_assets["asset1"]
        asset2 = st.session_state.mode_c_assets["asset2"]
        corr_live = st.session_state.mode_c_assets["corr"]
        corr_source = "Manual input"
        mode_explainer = "You entered both assets manually."

# ── PRE-RUN ──
if not needs_build:
    st.markdown("### How to use QGreen")
    st.markdown(f"""
<div class="soft-box">
    <h4>Selected mode: {mode}</h4>
    <p><strong>Input Method:</strong> {'Guided Quiz' if use_quiz else 'Advanced (Direct Parameters)'}</p>
    <p><strong>Client:</strong> {display_client_name}</p>
    <p>{'Configure your preferences in the sidebar, then click Build my portfolio.' if mode.startswith('C') else 'Set your preferences in the sidebar, configure the assets above, then click Build my portfolio.'}</p>
    <ul>
        <li><strong>Step 1:</strong> Choose your input method (Quiz or Advanced).</li>
        <li><strong>Step 2:</strong> Select assets or let QGreen choose.</li>
        <li><strong>Step 3:</strong> Click <em>Build my portfolio</em>. QGreen uses the benchmark optimisation problem from the brief, solved in two stages.</li>
    </ul>
</div>""", unsafe_allow_html=True)
    st.stop()

# Execute optimization if we have assets and (run was clicked or we have stored results)
if asset1 is not None and asset2 is not None and run:
    # Only optimize if run was just clicked (not using stored results)
    result = optimise_portfolio(asset1, asset2, gamma, lambda_esg, corr_live, rf, esg_mode, esg_threshold,
                                min_esg_score)
    if result.get("error"):
        st.error(result["error"])
        st.stop()

    # Store everything in session state
    st.session_state.portfolio_built = True
    st.session_state.result = result
    st.session_state.asset1 = asset1
    st.session_state.asset2 = asset2
    st.session_state.corr_live = corr_live
    st.session_state.corr_source = corr_source
    st.session_state.mode_explainer = mode_explainer
    st.session_state.data_message = data_message

# Retrieve from session state if already built
if st.session_state.portfolio_built and not run:
    result = st.session_state.result
    asset1 = st.session_state.asset1
    asset2 = st.session_state.asset2
    gamma = st.session_state.gamma
    lambda_esg = st.session_state.lambda_esg
    risk_label = st.session_state.risk_label
    esg_mode = st.session_state.esg_mode
    esg_threshold = st.session_state.esg_threshold
    min_esg_score = st.session_state.min_esg_score
    rf = st.session_state.rf
    corr_live = st.session_state.corr_live
    corr_source = st.session_state.corr_source
    mode_explainer = st.session_state.mode_explainer
    data_message = st.session_state.data_message

if not st.session_state.portfolio_built:
    st.stop()

# ============================================================
# EXTRACT RESULTS
# ============================================================
w1 = result["w1"]
w2 = result["w2"]
w_rf = result["w_rf"]
alpha = result["alpha"]
ret_opt = result["ret_opt"]
sd_opt = result["sd_opt"]
esg_opt = result["esg_opt"]
esg_opt_total = result["esg_opt_total"]
sharpe_opt = result["sharpe_opt"]
ret_tang = result["ret_tang"]
sd_tang = result["sd_tang"]
sharpe_tang = result["sharpe_tang"]
w1_tang = result["w1_tang"]
w2_tang = result["w2_tang"]

# ============================================================
# RESULTS DISPLAY
# ============================================================
st.markdown(f"## 🎯 {display_client_name}'s Optimal Portfolio")
st.caption(
    f"Client: {display_client_name} · Risk profile: {risk_label} · γ={gamma}, λ={lambda_esg:.3f} · rf = {rf * 100:.1f}% · ρ = {corr_live:.2f} ({corr_source})")

st.markdown(f"""
<div class="info-box">
    <strong>{display_client_name}</strong>, {mode_explainer}<br>{data_message}<br><br>
    <strong>How the portfolio was built:</strong> First, QGreen formed the tangency portfolio from the two risky assets
    ({w1_tang * 100:.0f}% {asset1['name']} / {w2_tang * 100:.0f}% {asset2['name']}) — incorporating your ESG preferences.
    Then, based on your risk aversion (γ={gamma}), it allocated {alpha * 100:.0f}% to that tangency portfolio
    and {w_rf * 100:.0f}% to the risk-free asset (rf = {rf * 100:.1f}%).
</div>""", unsafe_allow_html=True)

impact_summary = compute_impact_snapshot(asset1, asset2, w1 / (w1 + w2) if (w1 + w2) > 0 else 0.5,
                                         w2 / (w1 + w2) if (w1 + w2) > 0 else 0.5)

summary_left, summary_right = st.columns([1.05, 0.95])

with summary_left:
    st.markdown(f"""
<div class="metric-grid">
    <div class="metric-card">
        <div class="metric-label">Expected return</div>
        <div class="metric-value">{ret_opt * 100:.2f}%</div>
        <div class="metric-sub">Annualised portfolio return</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Risk (SD)</div>
        <div class="metric-value">{sd_opt * 100:.2f}%</div>
        <div class="metric-sub">Portfolio volatility</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Risky Portfolio ESG</div>
        <div class="metric-value">{esg_opt:.2f} / 100</div>
        <div class="metric-sub">Risky-portfolio average ESG score s̄</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Sharpe ratio</div>
        <div class="metric-value">{sharpe_opt:.2f}</div>
        <div class="metric-sub">Risk-adjusted excess return</div>
    </div>
</div>""", unsafe_allow_html=True)

    alloc_rows = {"Asset": [], "Ticker": [], "Weight (total)": [], "Weight (in risky)": [], "Expected Return": [],
                  "Volatility": [], "ESG Score": []}
    alloc_rows["Asset"].append("Risk-Free Asset")
    alloc_rows["Ticker"].append("rf")
    alloc_rows["Weight (total)"].append(f"{w_rf * 100:.1f}%")
    alloc_rows["Weight (in risky)"].append("—")
    alloc_rows["Expected Return"].append(f"{rf * 100:.1f}%")
    alloc_rows["Volatility"].append("0.0%")
    alloc_rows["ESG Score"].append("—")
    for asset, w_total, w_tang in [(asset1, w1, w1_tang), (asset2, w2, w2_tang)]:
        alloc_rows["Asset"].append(asset["name"])
        alloc_rows["Ticker"].append(asset["ticker"])
        alloc_rows["Weight (total)"].append(f"{w_total * 100:.1f}%")
        alloc_rows["Weight (in risky)"].append(f"{w_tang * 100:.1f}%")
        alloc_rows["Expected Return"].append(f"{asset['ret'] * 100:.2f}%")
        alloc_rows["Volatility"].append(f"{asset['sd'] * 100:.2f}%")
        alloc_rows["ESG Score"].append(f"{asset['esg']:.1f}")
    out = pd.DataFrame(alloc_rows)
    st.markdown("<div class='asset-table-wrap'>" + out.to_html(index=False, classes="asset-table", border=0) + "</div>",
                unsafe_allow_html=True)
    st.caption(
        "'Weight (total)' reports the benchmark risky weights x. These do not need to sum to 100%; the remainder is invested in or borrowed from the risk-free asset.")

with summary_right:
    labels_pie = ["Risk-Free Asset", asset1["name"], asset2["name"]]
    sizes_pie = [max(w_rf, 0.0001), max(w1, 0.0001), max(w2, 0.0001)]
    colors_pie = ["#B0BEC5", "#2E7D32", "#66BB6A"]
    fig2, ax2 = plt.subplots(figsize=(6.0, 4.1))
    fig2.patch.set_facecolor("#f4fbf5")
    wedges, texts, autotexts = ax2.pie(sizes_pie, labels=labels_pie, autopct="%1.1f%%", colors=colors_pie,
                                       startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 2.5})
    for at in autotexts:
        at.set_color("white");
        at.set_fontweight("bold")
    ax2.set_title("Total portfolio / borrowing view", color="#123321", fontweight="bold")
    st.pyplot(fig2)
    plt.close(fig2)

    fig3, ax3 = plt.subplots(figsize=(6.0, 3.3))
    fig3.patch.set_facecolor("#f4fbf5");
    ax3.set_facecolor("#f4fbf5")
    scores = [asset1["esg"], asset2["esg"], esg_opt]
    labels3 = [asset1["name"], asset2["name"], f"Your Portfolio ({esg_opt:.1f})"]
    bars = ax3.barh(labels3, scores, color=["#145A32", "#2E8B57", "#7BC67E"])
    for bar, val in zip(bars, scores):
        ax3.text(val + 0.8, bar.get_y() + bar.get_height() / 2, f"{val:.1f}", va="center", fontweight="bold")
    ax3.set_xlim(0, 110);
    ax3.set_xlabel("ESG score")
    ax3.set_title("ESG comparison", color="#123321", fontweight="bold");
    ax3.grid(True, axis="x", alpha=0.25)
    st.pyplot(fig3)
    plt.close(fig3)

alloc_col, story_col = st.columns([1.35, 1.0], gap="large")
with alloc_col:
    st.markdown(f"""
<div class="rec-box">
    <h4>Optimal portfolio — {display_client_name}</h4>
    <p><strong>Tangency portfolio (risky assets):</strong> {w1_tang * 100:.0f}% {asset1['name']} + {w2_tang * 100:.0f}% {asset2['name']}</p>
    <p><strong>Total risky exposure:</strong> α = {alpha:.2f} · risky mix. {'Remainder held in the risk-free asset' if w_rf >= 0 else 'Negative remainder means borrowing at the risk-free rate'}.</p>
    <ul>
        <li>Expected return: <strong>{ret_opt * 100:.2f}%</strong></li>
        <li>Volatility (SD): <strong>{sd_opt * 100:.2f}%</strong></li>
        <li>Risky portfolio ESG: <strong>{esg_opt:.2f}/100</strong></li>
        <li>Total risky exposure α: <strong>{alpha:.2f}</strong></li>
        <li>Sharpe ratio: <strong>{sharpe_opt:.2f}</strong></li>
        <li>Tangency Sharpe: <strong>{sharpe_tang:.2f}</strong></li>
        <li>Correlation (ρ): <strong>{corr_live:.3f}</strong> ({corr_source})</li>
    </ul>
</div>""", unsafe_allow_html=True)

with story_col:
    story_html = build_portfolio_narrative(display_client_name, result, asset1, asset2, esg_mode, risk_label,
                                           esg_threshold, min_esg_score)
    st.markdown(story_html, unsafe_allow_html=True)

# ============================================================
# TABS (INCLUDING MONTE CARLO WITH SESSION STATE HANDLING)
# ============================================================
portfolio_tab, esg_tab, impact_tab, mc_tab, method_tab = st.tabs(
    ["📈 Portfolio Frontier", "🌱 ESG Frontier", "🌍 Impact Metrics", "🔮 Monte Carlo", "🧠 Methodology"])

with portfolio_tab:
    st.markdown("### Portfolio frontier & Capital Market Line")
    st.caption(
        "The frontier shows all risky-asset combinations. The CML connects the risk-free rate to the tangency portfolio. Your optimal portfolio lies on the CML.")
    fig_pf, ax_pf = plt.subplots(figsize=(9.5, 5.5))
    fig_pf.patch.set_facecolor("#f4fbf5");
    ax_pf.set_facecolor("#f4fbf5")
    sc = ax_pf.scatter(result["all_std"] * 100, result["all_ret"] * 100, c=result["all_esg"],
                       cmap="RdYlGn", s=18, alpha=0.86, vmin=0, vmax=100)
    cbar = plt.colorbar(sc, ax=ax_pf);
    cbar.set_label("ESG score")
    max_x = max(result["all_std"].max() * 100 * 1.4, sd_opt * 100 * 1.4)
    if sd_tang > 0:
        cml_x = np.linspace(0, max_x, 300)
        cml_y = rf * 100 + (sharpe_tang) * cml_x
        ax_pf.plot(cml_x, cml_y, color="#1b5e20", linestyle="--", lw=1.8, label="Capital Market Line")
    ax_pf.scatter(0, rf * 100, color="#1b5e20", marker="s", s=110, zorder=5, label=f"Risk-free rate ({rf * 100:.1f}%)")
    ax_pf.scatter(sd_tang * 100, ret_tang * 100, color="#D32F2F", marker="*", s=280, zorder=5,
                  label=f"Tangency portfolio (Sharpe={sharpe_tang:.2f})")
    ax_pf.scatter(sd_opt * 100, ret_opt * 100, color="#43A047", marker="*", s=310, zorder=6,
                  label=f"Your optimal portfolio (Sharpe={sharpe_opt:.2f})")
    ax_pf.scatter(asset1["sd"] * 100, asset1["ret"] * 100, color="#6A1B9A", marker="D", s=95, label=asset1["name"])
    ax_pf.scatter(asset2["sd"] * 100, asset2["ret"] * 100, color="#EF6C00", marker="D", s=95, label=asset2["name"])
    ax_pf.set_xlabel("Risk — standard deviation (%)");
    ax_pf.set_ylabel("Expected return (%)")
    ax_pf.set_title("Portfolio Frontier & CML");
    ax_pf.grid(True, alpha=0.28);
    ax_pf.legend(fontsize=8.5, loc="lower right")
    st.pyplot(fig_pf)
    plt.close(fig_pf)

with esg_tab:
    st.markdown("### ESG frontier")
    st.caption("Trade-off between risky-portfolio ESG score s̄ and Sharpe ratio across all two-asset combinations.")
    fig_esg, ax_esg = plt.subplots(figsize=(9.5, 5.0))
    fig_esg.patch.set_facecolor("#f4fbf5");
    ax_esg.set_facecolor("#f4fbf5")
    tang_esg = result["tang_esg"]
    ax_esg.plot(result["all_esg"], result["all_sharpe"], color="#2e7d32", lw=2.2, label="ESG frontier (risky assets)")
    ax_esg.scatter(tang_esg, sharpe_tang, marker="*", color="#D32F2F", s=280, zorder=6,
                   label=f"Tangency / optimal risky portfolio (ESG={tang_esg:.1f}, Sharpe={sharpe_tang:.2f})")
    ax_esg.axvline(tang_esg, color="#2e7d32", linestyle=":", lw=1.4, alpha=0.75)
    ax_esg.axhline(sharpe_tang, color="#2e7d32", linestyle=":", lw=1.4, alpha=0.75)
    ax_esg.set_xlabel("Portfolio ESG score (risky assets)");
    ax_esg.set_ylabel("Sharpe ratio")
    ax_esg.set_title("ESG Frontier");
    ax_esg.grid(True, alpha=0.28);
    ax_esg.legend(fontsize=9)
    st.pyplot(fig_esg)
    plt.close(fig_esg)

with impact_tab:
    st.markdown("### Executive impact dashboard")
    if impact_summary.get("available"):
        cov_class = "positive" if impact_summary["coverage_weight"] >= 99 else (
            "neutral" if impact_summary["coverage_weight"] >= 70 else "caution")
        cards = []
        if pd.notna(impact_summary.get("emissions_score_port")):
            cards.append(
                f'<div class="impact-card"><div class="impact-kicker">Emissions management</div><div class="impact-value">{format_number_or_na(impact_summary["emissions_score_port"], " / 100", 1)}</div><div class="impact-detail">Weighted LSEG emissions score</div></div>')
        if pd.notna(impact_summary.get("gender_diversity_port")):
            cards.append(
                f'<div class="impact-card"><div class="impact-kicker">Board diversity</div><div class="impact-value">{format_percent_or_na(impact_summary["gender_diversity_port"], 1)}</div><div class="impact-detail">Weighted board gender diversity</div></div>')
        if pd.notna(impact_summary.get("emissions_trading_share")):
            cards.append(
                f'<div class="impact-card"><div class="impact-kicker">Emissions trading</div><div class="impact-value">{format_percent_or_na(impact_summary["emissions_trading_share"], 0)}</div><div class="impact-detail">Portfolio weight in emissions-trading participants</div></div>')
        if pd.notna(impact_summary.get("biodiversity_share")):
            cards.append(
                f'<div class="impact-card"><div class="impact-kicker">Biodiversity</div><div class="impact-value">{format_percent_or_na(impact_summary["biodiversity_share"], 0)}</div><div class="impact-detail">Portfolio weight with biodiversity-impact coverage</div></div>')
        if not cards:
            cards.append(
                '<div class="impact-card"><div class="impact-kicker">Impact data</div><div class="impact-value">Available</div><div class="impact-detail">Matched but sparse impact fields.</div></div>')
        st.markdown(f"""
<div class="impact-shell">
    <h4>Sustainability view</h4>
    <div class="impact-topline"><span class="impact-pill impact-pill-{cov_class}">Data coverage · {impact_summary['coverage_weight']:.0f}% of risky portfolio weight</span></div>
    <div class="impact-grid">{''.join(cards)}</div>
    <div class="impact-note"><strong>Read-out:</strong><ul>{''.join(f"<li>{i}</li>" for i in impact_summary['insights'])}</ul>
    <p style="margin-top:0.5rem;">These are portfolio characteristics from the LSEG dataset, not avoided emissions.</p></div>
</div>""", unsafe_allow_html=True)
    else:
        st.info(impact_summary.get("message", "No LSEG impact data available for these tickers."))

with mc_tab:
    st.markdown("### 🔮 Monte Carlo Future Value Simulation")
    st.caption(
        "Simulates possible future paths using Geometric Brownian Motion: dS/S = μdt + σdW. Verified drift adjustment (μ - ½σ²) for log-normal returns.")

    col_mc1, col_mc2, col_mc3 = st.columns(3)
    with col_mc1:
        initial_investment = st.number_input("Initial Investment ($)", min_value=1000, max_value=10000000, value=10000,
                                             step=1000, key="mc_initial")
    with col_mc2:
        years_mc = st.slider("Investment Horizon (years)", min_value=1, max_value=30, value=10, key="mc_years")
    with col_mc3:
        n_sims = st.selectbox("Number of Simulations", options=[500, 1000, 2500, 5000], index=1, key="mc_sims")

    # Monte Carlo using stored portfolio parameters
    np.random.seed(42)
    mu_port = ret_opt  # annualized decimal
    sigma_port = sd_opt  # annualized decimal

    # GBM: S_t = S_0 * exp((μ - 0.5*σ²)*t + σ*W_t)
    dt = 1.0
    random_shocks = np.random.standard_normal((n_sims, years_mc))

    # Correct drift adjustment for log-normal returns (Audit verified)
    drift = (mu_port - 0.5 * sigma_port ** 2) * dt
    diffusion = sigma_port * np.sqrt(dt) * random_shocks
    log_returns = drift + diffusion

    # Cumulative product
    wealth_paths = initial_investment * np.exp(np.cumsum(log_returns, axis=1))

    ending_values = wealth_paths[:, -1]
    mean_val = np.mean(ending_values)
    median_val = np.median(ending_values)
    var_5 = np.percentile(ending_values, 5)
    var_95 = np.percentile(ending_values, 95)
    prob_loss = np.mean(ending_values < initial_investment) * 100
    rf_final = initial_investment * ((1 + rf) ** years_mc)
    prob_beat_rf = np.mean(ending_values > rf_final) * 100

    # Metrics display
    mc_cols = st.columns(4)
    mc_cols[0].metric("Median Ending Value", f"${median_val:,.0f}")
    mc_cols[1].metric("5th Percentile (VaR 95%)", f"${var_5:,.0f}",
                      delta=f"{((var_5 - initial_investment) / initial_investment) * 100:.1f}%", delta_color="normal")
    mc_cols[2].metric("95th Percentile", f"${var_95:,.0f}")
    mc_cols[3].metric("Probability of Loss", f"{prob_loss:.1f}%", delta=f"{100 - prob_loss:.1f}% chance of gain",
                      delta_color="off" if prob_loss < 50 else "inverse")

    # Histogram
    fig_mc, ax_mc = plt.subplots(figsize=(10, 5))
    fig_mc.patch.set_facecolor("#f4fbf5")
    ax_mc.set_facecolor("#f4fbf5")

    # Use log bins if range is very large
    if median_val / initial_investment > 10 or (var_5 > 0 and initial_investment / var_5 > 10):
        bins = np.logspace(np.log10(max(ending_values.min(), 100)), np.log10(ending_values.max()), 50)
        ax_mc.set_xscale('log')
    else:
        bins = 50

    ax_mc.hist(ending_values, bins=bins, alpha=0.75, color='#2E7D32', edgecolor='white', density=True)
    ax_mc.axvline(median_val, color='#D32F2F', linestyle='--', linewidth=2.5, label=f'Median: ${median_val:,.0f}')
    ax_mc.axvline(var_5, color='#F9A825', linestyle='--', linewidth=2.5, label=f'5th %ile (VaR): ${var_5:,.0f}')
    ax_mc.axvline(initial_investment, color='#1565C0', linestyle='-', linewidth=2,
                  label=f'Initial: ${initial_investment:,.0f}')
    ax_mc.set_xlabel("Portfolio Value ($)", fontsize=11)
    ax_mc.set_ylabel("Probability Density", fontsize=11)
    ax_mc.set_title(f"Distribution of Portfolio Value after {years_mc} Years ({n_sims} simulations)", fontsize=12,
                    fontweight='bold')
    ax_mc.legend()
    ax_mc.grid(True, alpha=0.3)
    st.pyplot(fig_mc)
    plt.close(fig_mc)

    # Sample paths (show only 100 for performance)
    fig_path, ax_path = plt.subplots(figsize=(10, 5))
    fig_path.patch.set_facecolor("#f4fbf5")
    ax_path.set_facecolor("#f4fbf5")
    n_display = min(100, n_sims)
    years_axis = np.arange(years_mc + 1)
    # Include starting point
    wealth_display = np.column_stack([np.full(n_display, initial_investment), wealth_paths[:n_display]])

    for i in range(n_display):
        ax_path.plot(years_axis, wealth_display[i], alpha=0.3, color='#2E7D32', linewidth=0.6)
    ax_path.axhline(initial_investment, color='#1565C0', linestyle='--', alpha=0.8, label='Initial investment')
    ax_path.set_xlabel("Years", fontsize=11)
    ax_path.set_ylabel("Portfolio Value ($)", fontsize=11)
    ax_path.set_title(f"Sample Portfolio Paths ({n_display} random simulations)", fontsize=12, fontweight='bold')
    ax_path.grid(True, alpha=0.3)
    # Format y-axis as currency
    ax_path.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: f'${x / 1000:.0f}k' if x < 1000000 else f'${x / 1000000:.1f}M'))
    st.pyplot(fig_path)
    plt.close(fig_path)

    # Explanation
    total_return_pct = ((median_val / initial_investment) ** (1 / years_mc) - 1) * 100 if years_mc > 0 else 0

    st.markdown(f"""
<div class="soft-box">
    <h4>Understanding the Simulation</h4>
    <p>Based on your optimal portfolio's expected return of <strong>{ret_opt * 100:.2f}%</strong> and volatility of <strong>{sd_opt * 100:.2f}%</strong>:</p>
    <ul>
        <li><strong>Value at Risk (5th percentile):</strong> There is a 5% chance your portfolio will be worth less than <strong>${var_5:,.0f}</strong> after {years_mc} years.</li>
        <li><strong>Implied median growth rate:</strong> <strong>{total_return_pct:.1f}%</strong> per year (geometric).</li>
        <li><strong>Probability of beating risk-free:</strong> <strong>{prob_beat_rf:.1f}%</strong> chance of doing better than just holding cash (which would grow to ${rf_final:,.0f}).</li>
        <li><strong>Probability of loss:</strong> <strong>{prob_loss:.1f}%</strong> chance of ending with less than you started.</li>
    </ul>
    <p style="font-size:0.9rem;color:#555;margin-top:0.5rem;"><em>Note: Past performance does not guarantee future results. This simulation assumes Geometric Brownian Motion with constant parameters per the Black-Scholes framework.</em></p>
</div>
""", unsafe_allow_html=True)

with method_tab:
    st.markdown("### How QGreen works")
    st.markdown("#### Two-stage portfolio construction (Pedersen et al. 2021)")
    st.markdown("QGreen maximizes the ESG-augmented mean-variance objective:")
    st.code("max  x'μ − (γ/2)x'Σx + λ·s̄", language=None)
    st.markdown("where **s̄ = (x₁s₁ + x₂s₂)/(x₁ + x₂)** is the portfolio-average ESG score (risky assets only).")
    st.markdown("**Stage 1 — ESG-constrained tangency portfolio:**")
    st.markdown("""
- Find mix w₁, w₂ across risky assets maximizing **μₚ²/(2γσₚ²) + λ·sₚ** (equivalent to max SR²/2γ + λs̄)
- This is the optimal risky composition before scaling by total risky exposure α
""")
    st.markdown("**Stage 2 — Risk-free allocation:**")
    st.markdown(f"""
- Optimal risky exposure: **α = (μₚ − r_f)/(γ·σₚ²)**
- Final risky weights are x₁ = α·w₁ and x₂ = α·w₂. The remainder 1−x'1 is invested in or borrowed from the risk-free asset.

**Your current parameters:** γ = {gamma}, λ = {lambda_esg:.3f}, r_f = {rf * 100:.1f}%
""")
    st.markdown("---")
    st.markdown("#### ESG Constraints Explained")
    st.markdown("""
- **Exclusion Threshold:** Minimum ESG score for individual assets to be considered (removes "sin stocks").
- **Portfolio Minimum (s̄):** Hard floor on the weighted-average ESG of the risky portfolio. Enforced via: w₁s₁ + w₂s₂ ≥ s̄_min.
""")
