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
# CUSTOM CSS
# ============================================================
st.markdown(
    """
<style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(46,125,50,0.10), transparent 28%),
            radial-gradient(circle at top right, rgba(21,101,192,0.08), transparent 25%),
            linear-gradient(180deg, #f4fbf5 0%, #eef6f3 100%) !important;
        color: #132218 !important;
    }

    p, span, label, div, li, td, th, h1, h2, h3, h4, h5, h6,
    .stMarkdown, .stMarkdown p, .stMarkdown li {
        color: #132218 !important;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f3fbf4 0%, #edf7f0 100%) !important;
        border-right: 1px solid rgba(46,125,50,0.10);
    }

    section[data-testid="stSidebar"] * {
        color: #132218 !important;
    }

    .stTextInput > div > div > input,
    .stNumberInput input,
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background-color: rgba(255,255,255,0.88) !important;
        border: 1px solid rgba(46,125,50,0.18) !important;
        border-radius: 10px !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 0.72rem 1.25rem !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 24px rgba(27,94,32,0.20) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) scale(1.01);
        box-shadow: 0 14px 30px rgba(27,94,32,0.26) !important;
    }

    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background: #2e7d32 !important;
        box-shadow: 0 0 0 4px rgba(46,125,50,0.18) !important;
    }

    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.78) !important;
        border: 1px solid rgba(46,125,50,0.12) !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        box-shadow: 0 10px 28px rgba(22, 34, 26, 0.06) !important;
    }

    div[data-testid="metric-container"] label {
        color: #2e7d32 !important;
        font-weight: 700 !important;
    }

    .stDataFrame, .stDataFrame * {
        background: rgba(255,255,255,0.85) !important;
        color: #132218 !important;
    }

    .hero {
        background: linear-gradient(135deg, rgba(27,94,32,0.97) 0%, rgba(56,142,60,0.95) 55%, rgba(38,166,154,0.92) 100%);
        color: white !important;
        border-radius: 24px;
        padding: 2.5rem 2rem 2rem 2rem;
        box-shadow: 0 18px 40px rgba(27,94,32,0.20);
        margin-bottom: 1.15rem;
        position: relative;
        overflow: hidden;
    }

    .hero:before {
        content: "";
        position: absolute;
        inset: -35% auto auto 68%;
        width: 260px;
        height: 260px;
        background: rgba(255,255,255,0.10);
        border-radius: 50%;
        filter: blur(2px);
    }

    .hero h1 {
        font-size: 3rem;
        margin: 0;
        color: white !important;
        letter-spacing: 0.4px;
    }

    .hero p {
        color: rgba(255,255,255,0.95) !important;
        margin-top: 0.45rem;
        font-size: 1.05rem;
        max-width: 840px;
    }

    .glass-card {
        background: rgba(255,255,255,0.74);
        border: 1px solid rgba(255,255,255,0.55);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.1rem 1.15rem;
        box-shadow: 0 12px 30px rgba(19,34,24,0.06);
        min-height: 160px;
    }

    .glass-card h4 {
        margin: 0 0 0.4rem 0;
        color: #1b5e20 !important;
    }

    .glass-card p {
        color: #23412d !important;
    }

    .glass-card.selected {
        background: linear-gradient(145deg, #1b5e20 0%, #2e7d32 55%, #43a047 100%);
        border: 1px solid rgba(27,94,32,0.22);
        box-shadow: 0 16px 34px rgba(27,94,32,0.24);
        transform: translateY(-2px);
    }

    .glass-card.selected h4,
    .glass-card.selected p,
    .glass-card.selected .mode-badge {
        color: white !important;
    }

    .mode-badge {
        display: inline-block;
        margin-top: 0.55rem;
        padding: 0.28rem 0.65rem;
        border-radius: 999px;
        background: rgba(27,94,32,0.10);
        color: #1b5e20 !important;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.2px;
    }

    .status-pill {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.16);
        color: white !important;
        border: 1px solid rgba(255,255,255,0.22);
        font-size: 0.88rem;
        font-weight: 600;
        margin-right: 0.45rem;
        margin-top: 0.55rem;
    }

    .soft-box {
        background: rgba(255,255,255,0.78);
        border: 1px solid rgba(46,125,50,0.10);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 8px 24px rgba(19,34,24,0.05);
        margin-bottom: 0.9rem;
    }

    .soft-box h4 {
        margin-top: 0;
        color: #1b5e20 !important;
    }

    .rec-box {
        background: linear-gradient(135deg, rgba(232,245,233,0.95), rgba(241,248,233,0.95));
        border-left: 6px solid #2e7d32;
        border-radius: 18px;
        padding: 1.2rem 1.35rem;
        box-shadow: 0 12px 28px rgba(46,125,50,0.10);
        min-height: 100%;
    }

    .rec-box h4 {
        color: #1b5e20 !important;
        margin-top: 0;
    }

    .note-box {
        background: rgba(227,242,253,0.82);
        border-left: 4px solid #1e88e5;
        border-radius: 14px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.9rem;
    }

    .strategy-box {
        background: rgba(255,255,255,0.82);
        border: 1px solid rgba(46,125,50,0.14);
        border-radius: 18px;
        padding: 0.95rem 1rem;
        margin-top: 0.75rem;
        box-shadow: 0 10px 24px rgba(19,34,24,0.05);
    }

    .strategy-title {
        font-weight: 800;
        color: #1b5e20 !important;
        margin-bottom: 0.2rem;
    }

    .hero, .glass-card, .soft-box, .rec-box, .strategy-box, .note-box {
        animation: fadeUp 0.65s ease both;
    }

    .status-pill {
        animation: pulseGlow 3.2s ease-in-out infinite;
    }

    .metric-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.95rem;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(239,248,241,0.92));
        border: 1px solid rgba(46,125,50,0.18);
        border-radius: 18px;
        padding: 1rem 1.05rem;
        box-shadow: 0 12px 28px rgba(19,34,24,0.08);
        min-height: 122px;
    }

    .metric-label {
        font-size: 0.90rem;
        font-weight: 800;
        color: #1b5e20 !important;
        margin-bottom: 0.35rem;
    }

    .metric-value {
        font-size: clamp(1.18rem, 2.2vw, 1.65rem);
        line-height: 1.18;
        font-weight: 900;
        color: #0f2d18 !important;
        white-space: normal;
        overflow-wrap: anywhere;
        word-break: break-word;
    }

    .metric-sub {
        font-size: 0.80rem;
        margin-top: 0.34rem;
        color: #355544 !important;
    }

    .asset-table-wrap {
        margin-top: 0.35rem;
        margin-bottom: 0.9rem;
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 12px 28px rgba(19,34,24,0.09);
        border: 1px solid rgba(27,94,32,0.18);
    }

    .asset-table {
        width: 100%;
        border-collapse: collapse;
        background: rgba(255,255,255,0.96);
        color: #102516 !important;
    }

    .asset-table thead th {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        color: white !important;
        padding: 0.82rem 0.9rem;
        font-size: 0.89rem;
        text-align: left;
        border-bottom: 1px solid rgba(255,255,255,0.10);
    }

    .asset-table tbody td {
        padding: 0.78rem 0.9rem;
        border-bottom: 1px solid rgba(27,94,32,0.10);
        font-size: 0.92rem;
        color: #102516 !important;
        font-weight: 600;
    }

    .asset-table tbody tr:nth-child(odd) {
        background: #f3fbf4;
    }

    .asset-table tbody tr:nth-child(even) {
        background: #e8f5e9;
    }

    .asset-table tbody tr:hover {
        background: #d9f2dd;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.45rem;
        background: rgba(255,255,255,0.62);
        padding: 0.35rem;
        border-radius: 999px;
        border: 1px solid rgba(46,125,50,0.10);
        box-shadow: 0 10px 24px rgba(19,34,24,0.05);
        width: fit-content;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 999px !important;
        padding: 0.55rem 1rem !important;
        color: #1b5e20 !important;
        font-weight: 700 !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%) !important;
        color: white !important;
        box-shadow: 0 8px 18px rgba(27,94,32,0.18);
    }

    .chart-card {
        background: rgba(255,255,255,0.82);
        border: 1px solid rgba(46,125,50,0.12);
        border-radius: 20px;
        padding: 1rem 1.05rem 0.55rem 1.05rem;
        box-shadow: 0 12px 28px rgba(19,34,24,0.06);
    }

    .why-box {
        background: linear-gradient(160deg, rgba(255,255,255,0.96), rgba(232,245,233,0.95));
        border-top: 4px solid #66bb6a;
        border-radius: 18px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 12px 28px rgba(19,34,24,0.06);
        height: 100%;
    }

    .why-box h4 {
        color: #1b5e20 !important;
        margin-top: 0;
    }

    @media (max-width: 1100px) {
        .metric-grid {
            grid-template-columns: repeat(1, minmax(0, 1fr));
        }
        .impact-grid {
            grid-template-columns: repeat(1, minmax(0, 1fr));
        }
    }

    @keyframes fadeUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0px);
        }
    }

    @keyframes pulseGlow {
        0%, 100% {
            transform: translateY(0px);
            box-shadow: 0 0 0 rgba(255,255,255,0.0);
        }
        50% {
            transform: translateY(-1px);
            box-shadow: 0 0 16px rgba(255,255,255,0.10);
        }
    }


    .impact-shell {
        background: linear-gradient(160deg, rgba(255,255,255,0.94), rgba(238,248,240,0.96));
        border: 1px solid rgba(46,125,50,0.14);
        border-radius: 22px;
        padding: 1.15rem 1.2rem;
        box-shadow: 0 14px 30px rgba(19,34,24,0.07);
        margin-top: 0.9rem;
        margin-bottom: 1rem;
    }

    .impact-shell h4 {
        margin: 0;
        color: #1b5e20 !important;
    }

    .impact-shell p {
        color: #274333 !important;
    }

    .impact-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.9rem;
        margin-top: 0.85rem;
        margin-bottom: 0.85rem;
    }

    .impact-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(241,248,243,0.95));
        border: 1px solid rgba(46,125,50,0.14);
        border-radius: 18px;
        padding: 0.95rem 1rem;
        box-shadow: 0 10px 24px rgba(19,34,24,0.05);
    }

    .impact-kicker {
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.35px;
        text-transform: uppercase;
        color: #2e7d32 !important;
        margin-bottom: 0.35rem;
    }

    .impact-value {
        font-size: clamp(1.06rem, 2.0vw, 1.45rem);
        font-weight: 900;
        color: #10311d !important;
        line-height: 1.15;
        margin-bottom: 0.22rem;
    }

    .impact-detail {
        font-size: 0.82rem;
        color: #3d5f4c !important;
    }

    .impact-note {
        background: rgba(27,94,32,0.06);
        border-left: 4px solid #2e7d32;
        border-radius: 14px;
        padding: 0.85rem 0.95rem;
        margin-top: 0.25rem;
    }

    .impact-note ul {
        margin: 0.45rem 0 0.1rem 1rem;
        padding-left: 0.4rem;
    }

    .impact-topline {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 0.75rem;
        margin-bottom: 0.9rem;
    }

    .impact-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.45rem 0.7rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 800;
        letter-spacing: 0.2px;
        border: 1px solid rgba(46,125,50,0.10);
        background: rgba(255,255,255,0.88);
        color: #183b26 !important;
    }

    .impact-pill-positive {
        background: rgba(232,245,233,0.95);
        color: #1b5e20 !important;
        border-color: rgba(46,125,50,0.22);
    }

    .impact-pill-neutral {
        background: rgba(243,248,244,0.95);
        color: #355844 !important;
        border-color: rgba(85,118,97,0.18);
    }

    .impact-pill-caution {
        background: rgba(255,243,224,0.94);
        color: #8a4b00 !important;
        border-color: rgba(249,168,37,0.22);
    }

    .impact-layout {
        display: grid;
        grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
        gap: 1rem;
        align-items: start;
        margin-top: 0.95rem;
    }

    .impact-sidecard {
        background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(241,248,243,0.96));
        border: 1px solid rgba(46,125,50,0.14);
        border-radius: 18px;
        padding: 1rem 1.05rem;
        box-shadow: 0 10px 24px rgba(19,34,24,0.05);
    }

    .impact-sidecard h5 {
        margin: 0;
        color: #184d2a !important;
        font-size: 0.98rem;
    }

    .impact-sidecard p {
        margin: 0.45rem 0 0 0;
        color: #335743 !important;
        font-size: 0.84rem;
    }

    .impact-compare {
        margin-top: 0.85rem;
        display: grid;
        gap: 0.75rem;
    }

    .impact-compare-row {
        background: rgba(247,251,248,0.96);
        border: 1px solid rgba(46,125,50,0.12);
        border-radius: 16px;
        padding: 0.8rem 0.85rem;
    }

    .impact-compare-head {
        display: flex;
        justify-content: space-between;
        gap: 0.8rem;
        align-items: baseline;
        margin-bottom: 0.55rem;
        color: #183b26 !important;
    }

    .impact-compare-label {
        font-size: 0.84rem;
        font-weight: 800;
        color: #184d2a !important;
    }

    .impact-compare-badge {
        font-size: 0.76rem;
        font-weight: 800;
        color: #2e7d32 !important;
    }

    .impact-bar-track {
        width: 100%;
        height: 10px;
        border-radius: 999px;
        background: rgba(183,225,192,0.34);
        overflow: hidden;
        margin-bottom: 0.45rem;
    }

    .impact-bar-fill {
        height: 100%;
        border-radius: 999px;
    }

    .impact-bar-current {
        background: linear-gradient(90deg, #1b5e20, #43a047);
    }

    .impact-bar-baseline {
        background: linear-gradient(90deg, #8fc79a, #c8e6c9);
    }

    .impact-compare-values {
        display: flex;
        justify-content: space-between;
        gap: 0.85rem;
        font-size: 0.8rem;
        color: #355844 !important;
    }

    .impact-footnote {
        margin-top: 0.85rem;
        font-size: 0.8rem;
        color: #4b6e59 !important;
    }

    @media (max-width: 1100px) {
        .impact-layout {
            grid-template-columns: 1fr;
        }
    }

    .disclaimer {
        background: rgba(255,248,225,0.88);
        border-left: 4px solid #f9a825;
        border-radius: 12px;
        padding: 0.8rem 1rem;
        font-size: 0.88rem;
        color: #5f4b00 !important;
        margin-top: 1.3rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# DATA
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


esg_df = load_esg_data()
company_names = esg_df["comname"].tolist()



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
    metric_fields = [
        "ESGScore",
        "ESGCombinedScore",
        "ESGCControversiesScore",
        "ESGEmissionsScore",
        "CO2EquivalentsEmissionDirectScope1",
        "CO2EquivalentsEmissionIndirectScope2",
        "CO2EquivalentsEmissionIndirectScope3",
        "BoardGenderDiversityPercent",
        "BoardCulturalDiversityPercent",
        "EmissionsTrading",
        "BiodiversityImpactReduction",
    ]

    work = raw.copy()
    work["ticker"] = work["ticker"].astype(str).str.strip().str.upper()
    work["ticker_key"] = work["ticker"].str.replace(r"[^A-Z0-9]", "", regex=True)
    work["year"] = pd.to_numeric(work["year"], errors="coerce")
    work["fieldname"] = work["fieldname"].astype(str).str.strip()
    work["value_num"] = pd.to_numeric(work["value"], errors="coerce")
    work["valuescore_num"] = pd.to_numeric(work["valuescore"], errors="coerce")
    work["bool_num"] = work["value"].astype(str).str.strip().str.lower().map({"true": 1.0, "false": 0.0})
    work["metric_value"] = np.where(work["fieldname"].isin(score_fields), work["valuescore_num"] * 100, work["value_num"])
    work.loc[work["fieldname"].isin(bool_fields), "metric_value"] = work.loc[work["fieldname"].isin(bool_fields), "bool_num"]
    work = work[work["fieldname"].isin(metric_fields)].copy()

    grouped = (
        work.groupby(["ticker", "ticker_key", "year", "fieldname"], dropna=False, as_index=False)
        .agg(metric_value=("metric_value", "mean"))
    )

    wide = grouped.pivot_table(
        index=["ticker", "ticker_key", "year"],
        columns="fieldname",
        values="metric_value",
        aggfunc="mean",
    ).reset_index()

    candidate_cols = [c for c in metric_fields if c in wide.columns]
    wide["impact_coverage"] = wide[candidate_cols].notna().sum(axis=1) if candidate_cols else 0
    wide["impact_data_source"] = "LSEG ESGMore.csv"
    wide = wide.sort_values(["ticker_key", "impact_coverage", "year"], ascending=[True, False, False])
    return wide


impact_wide = load_impact_data()
impact_lookup = {}
if not impact_wide.empty:
    for rec in impact_wide.to_dict(orient="records"):
        key = str(rec.get("ticker_key", "")).strip().upper()
        if key:
            impact_lookup.setdefault(key, []).append(rec)
impact_keys = sorted(impact_lookup.keys())


# ============================================================
# HELPERS
# ============================================================
def risk_profile_from_quiz(score: int):
    if score <= 4:
        return 8, "Conservative 🛡️"
    if score <= 6:
        return 4, "Balanced ⚖️"
    return 2, "Growth-Oriented 🚀"


def estimate_asset_characteristics(esg_score: float, style: str):
    e = float(esg_score)
    if style == "Conservative 🛡️":
        ret = 0.05 + 0.00025 * e
        sd = 0.10 + 0.00020 * (100 - e)
    elif style == "Balanced ⚖️":
        ret = 0.07 + 0.00022 * e
        sd = 0.14 + 0.00022 * (100 - e)
    else:
        ret = 0.09 + 0.00018 * e
        sd = 0.18 + 0.00025 * (100 - e)
    return round(ret, 4), round(sd, 4)


@st.cache_data(show_spinner=False)
def fetch_market_stats(ticker: str):
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
        return {
            "return": ann_return,
            "sd": ann_vol,
            "source": "Market data (last 3 years)",
        }
    except Exception:
        return None


def get_asset_from_row(row, style: str, mode_label: str):
    market = fetch_market_stats(row["ticker"])
    if market:
        ret, sd, source = market["return"], market["sd"], market["source"]
    else:
        ret, sd = estimate_asset_characteristics(row["esg_0_100"], style)
        source = "Transparent app estimate"
    impact_profile = get_impact_profile(row["ticker"], row.get("esg_0_100"), row.get("comname"))

    raw_name = str(row.get("comname", row["ticker"])).strip()
    raw_ticker = str(row["ticker"]).strip().upper()
    display_name = raw_ticker if raw_name.upper() == raw_ticker else raw_name.title()

    return {
        "name": display_name,
        "ticker": raw_ticker,
        "ret": float(ret),
        "sd": float(sd),
        "esg": float(row["esg_0_100"]),
        "source": source,
        "mode": mode_label,
        "impact_profile": impact_profile,
        "impact_available": bool(impact_profile),
    }


def derive_esg_preferences(answers):
    total = int(sum(answers))
    lambda_esg = total / 21.0

    if total == 0:
        model_name = "⚪ Finance as Usual Model"
        model_short = "Finance as Usual"
        description = "ESG does not enter portfolio choice because all ESG preference answers are zero."
    elif total <= 7:
        model_name = "🚫 Sustainable Finance Model 1.0 - Exclusion Screen"
        model_short = "Exclusion Screen"
        description = "Negative screening dominates, so the app can filter out lower-ESG assets before optimisation."
    elif total <= 14:
        model_name = "🏅 Sustainable Finance Model 2.0 - Best-in-Class"
        model_short = "Best-in-Class"
        description = "The app gives extra weight to relative ESG leaders while still balancing financial performance."
    else:
        model_name = "🌍 Sustainable Finance Model 3.0 - ESG Integration"
        model_short = "ESG Integration"
        description = "ESG is integrated directly into utility as part of the return-risk-sustainability trade-off."

    return {
        "total": total,
        "lambda": lambda_esg,
        "model_name": model_name,
        "model_short": model_short,
        "description": description,
    }


def ticker_key(value):
    return "".join(ch for ch in str(value).upper() if ch.isalnum())


def ticker_candidates(value):
    raw = str(value).upper().strip()
    candidates = []

    def add_candidate(v):
        key = ticker_key(v)
        if key and key not in candidates:
            candidates.append(key)

    add_candidate(raw)

    for sep in [".", ":", "/", " ", "-", "_"]:
        if sep in raw:
            add_candidate(raw.split(sep)[0])

    # Common vendor / exchange suffix cases: e.g. AAPL.OQ -> AAPL, VOD.L -> VOD
    if raw.endswith((".OQ", ".N", ".L", ".PA", ".DE", ".HK", ".TO", ".AX", ".MI")):
        add_candidate(raw.split(".")[0])

    return candidates


def get_impact_profile(ticker, esg_hint=None, name_hint=None):
    def choose_best_profile(profiles, match_type):
        if not profiles:
            return {}
        if len(profiles) == 1:
            enriched = dict(profiles[0])
            enriched["match_type"] = match_type
            enriched["match_quality"] = "single_candidate"
            return enriched

        scored_candidates = []
        for profile in profiles:
            score = profile.get("ESGScore")
            diff = None
            if esg_hint is not None and pd.notna(score):
                diff = abs(float(score) - float(esg_hint))
            scored_candidates.append((profile, diff))

        candidates_with_diff = [item for item in scored_candidates if item[1] is not None]
        if candidates_with_diff:
            candidates_with_diff.sort(key=lambda x: x[1])
            best_profile, best_diff = candidates_with_diff[0]
            second_diff = candidates_with_diff[1][1] if len(candidates_with_diff) > 1 else None
            enriched = dict(best_profile)
            enriched["esg_diff"] = float(best_diff)
            enriched["match_type"] = match_type + "_esg_resolved"
            if best_diff <= 2 and (second_diff is None or second_diff - best_diff >= 2):
                enriched["match_quality"] = "high_confidence"
            elif best_diff <= 5:
                enriched["match_quality"] = "medium_confidence"
            else:
                enriched["match_quality"] = "low_confidence"
            return enriched

        enriched = dict(profiles[0])
        enriched["match_type"] = match_type
        enriched["match_quality"] = "multiple_candidates_no_esg_hint"
        return enriched

    exact_profiles = []
    for key in ticker_candidates(ticker):
        profiles = impact_lookup.get(key)
        if profiles:
            exact_profiles.extend(profiles)
    chosen = choose_best_profile(exact_profiles, "exact_or_normalized")
    if chosen:
        return chosen

    prefix_profiles = []
    for key in ticker_candidates(ticker):
        prefix_matches = [k for k in impact_keys if k.startswith(key) or key.startswith(k)]
        prefix_matches = [k for k in prefix_matches if abs(len(k) - len(key)) <= 4]
        if len(prefix_matches) == 1:
            prefix_profiles.extend(impact_lookup[prefix_matches[0]])
    chosen = choose_best_profile(prefix_profiles, "prefix_fallback")
    if chosen:
        return chosen

    return {}


def weighted_metric(values, weights):
    arr = np.array(values, dtype=float)
    w = np.array(weights, dtype=float)
    mask = np.isfinite(arr)
    if not mask.any():
        return np.nan, 0.0
    used_weight = float(w[mask].sum())
    if used_weight <= 0:
        return np.nan, 0.0
    return float(np.dot(arr[mask], w[mask]) / used_weight), used_weight


def safe_sum_numeric(values):
    vals = [float(v) for v in values if pd.notna(v)]
    return float(np.sum(vals)) if vals else np.nan


def percent_delta(current, baseline):
    if pd.isna(current) or pd.isna(baseline) or baseline == 0:
        return np.nan
    return float((current - baseline) / baseline * 100)


def format_tco2e(value):
    if pd.isna(value):
        return "Not available"
    abs_val = abs(float(value))
    if abs_val >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}bn tCO₂e"
    if abs_val >= 1_000_000:
        return f"{value / 1_000_000:.2f}m tCO₂e"
    if abs_val >= 1_000:
        return f"{value / 1_000:.1f}k tCO₂e"
    return f"{value:,.0f} tCO₂e"


def format_number_or_na(value, suffix="", decimals=2):
    if pd.isna(value):
        return "Not available"
    return f"{float(value):,.{decimals}f}{suffix}"


def format_percent_or_na(value, decimals=1):
    if pd.isna(value):
        return "Not available"
    return f"{float(value):.{decimals}f}%"


def describe_delta(delta, lower_is_better=True):
    if pd.isna(delta):
        return "Baseline comparison unavailable"
    direction = "lower" if delta < 0 else "higher"
    if not lower_is_better:
        direction = "higher" if delta > 0 else "lower"
    return f"{abs(delta):.1f}% {direction} vs 50/50 baseline"


def impact_signal(delta, lower_is_better=True):
    if pd.isna(delta):
        return "Comparison unavailable", "neutral"
    if abs(delta) < 0.1:
        return "In line with baseline", "neutral"
    favourable = delta < 0 if lower_is_better else delta > 0
    if favourable:
        return f"{abs(delta):.1f}% better vs baseline", "positive"
    return f"{abs(delta):.1f}% weaker vs baseline", "caution"


def scaled_bar_width(current, baseline):
    vals = [v for v in [current, baseline] if pd.notna(v)]
    if not vals:
        return 0.0, 0.0
    max_val = max(abs(float(v)) for v in vals)
    if max_val <= 0:
        return 0.0, 0.0
    return max(8.0, abs(float(current)) / max_val * 100) if pd.notna(current) else 0.0, max(8.0, abs(float(baseline)) / max_val * 100) if pd.notna(baseline) else 0.0


def compute_impact_snapshot(asset1, asset2, w1, w2):
    profile1 = get_impact_profile(asset1.get("ticker"))
    profile2 = get_impact_profile(asset2.get("ticker"))

    has_profile_1 = bool(profile1)
    has_profile_2 = bool(profile2)
    overall_coverage = (w1 if has_profile_1 else 0.0) + (w2 if has_profile_2 else 0.0)

    if overall_coverage <= 0:
        return {
            "available": False,
            "message": "No impact match was found for the selected tickers in ESGMore.csv. This usually means the CSV extract does not include those firms or the ticker format differs from the app universe."
        }

    scope12_1 = safe_sum_numeric([profile1.get("CO2EquivalentsEmissionDirectScope1"), profile1.get("CO2EquivalentsEmissionIndirectScope2")]) if profile1 else np.nan
    scope12_2 = safe_sum_numeric([profile2.get("CO2EquivalentsEmissionDirectScope1"), profile2.get("CO2EquivalentsEmissionIndirectScope2")]) if profile2 else np.nan
    scope123_1 = safe_sum_numeric([profile1.get("CO2EquivalentsEmissionDirectScope1"), profile1.get("CO2EquivalentsEmissionIndirectScope2"), profile1.get("CO2EquivalentsEmissionIndirectScope3")]) if profile1 else np.nan
    scope123_2 = safe_sum_numeric([profile2.get("CO2EquivalentsEmissionDirectScope1"), profile2.get("CO2EquivalentsEmissionIndirectScope2"), profile2.get("CO2EquivalentsEmissionIndirectScope3")]) if profile2 else np.nan

    scope12_port, scope12_weight = weighted_metric([scope12_1, scope12_2], [w1, w2])
    scope123_port, scope123_weight = weighted_metric([scope123_1, scope123_2], [w1, w2])

    emissions_score_port, emissions_score_weight = weighted_metric(
        [profile1.get("ESGEmissionsScore", np.nan) if profile1 else np.nan, profile2.get("ESGEmissionsScore", np.nan) if profile2 else np.nan],
        [w1, w2],
    )

    gender_diversity_port, gender_weight = weighted_metric(
        [profile1.get("BoardGenderDiversityPercent", np.nan) if profile1 else np.nan, profile2.get("BoardGenderDiversityPercent", np.nan) if profile2 else np.nan],
        [w1, w2],
    )
    emissions_trading_share, trading_weight = weighted_metric(
        [100 * profile1.get("EmissionsTrading", np.nan) if profile1 else np.nan, 100 * profile2.get("EmissionsTrading", np.nan) if profile2 else np.nan],
        [w1, w2],
    )
    biodiversity_share, biodiversity_weight = weighted_metric(
        [100 * profile1.get("BiodiversityImpactReduction", np.nan) if profile1 else np.nan, 100 * profile2.get("BiodiversityImpactReduction", np.nan) if profile2 else np.nan],
        [w1, w2],
    )

    insights = []
    if pd.notna(scope12_port):
        insights.append(f"Weighted reported Scope 1 + 2 emissions exposure is {format_tco2e(scope12_port)} across the matched holdings.")
    if pd.notna(scope123_port):
        insights.append(f"Weighted reported Scope 1 + 2 + 3 emissions exposure is {format_tco2e(scope123_port)} where Scope 3 data is available.")
    if pd.notna(emissions_score_port):
        insights.append(f"The weighted LSEG emissions score is {emissions_score_port:.1f}/100, which signals the portfolio's relative emissions-management profile.")
    if pd.notna(gender_diversity_port):
        insights.append(f"Weighted board gender diversity is {gender_diversity_port:.1f}% across the selected holdings.")
    if pd.notna(emissions_trading_share):
        insights.append(f"{emissions_trading_share:.0f}% of portfolio weight sits in companies flagged for emissions-trading participation in the uploaded LSEG dataset.")
    if pd.notna(biodiversity_share):
        insights.append(f"{biodiversity_share:.0f}% of portfolio weight sits in companies with biodiversity-impact reduction coverage in the uploaded LSEG dataset.")

    data_points = {
        "scope12_port": scope12_port,
        "scope123_port": scope123_port,
        "emissions_score_port": emissions_score_port,
        "gender_diversity_port": gender_diversity_port,
        "emissions_trading_share": emissions_trading_share,
        "biodiversity_share": biodiversity_share,
        "coverage_weight": overall_coverage * 100,
        "scope12_weight": scope12_weight * 100,
        "scope123_weight": scope123_weight * 100,
        "emissions_score_weight": emissions_score_weight * 100,
        "gender_weight": gender_weight * 100,
        "trading_weight": trading_weight * 100,
        "biodiversity_weight": biodiversity_weight * 100,
        "insights": insights,
        "available": True,
    }
    return data_points


def build_portfolio_story(client_name, esg_mode, risk_label, result, asset1, asset2, w1, w2, lambda_esg, esg_threshold):
    if result["excluded"]:
        allocation = f"The recommendation concentrates in the remaining eligible asset because the exclusion screen removed {', '.join(result['excluded'])}."
    elif abs(w1 - w2) < 0.03:
        allocation = "The allocation stays relatively balanced because the two assets offer a similar overall trade-off once return, risk, and sustainability are considered together."
    elif w1 > w2:
        allocation = f"{asset1['name']} receives the higher weight because it improves the portfolio trade-off more strongly than {asset2['name']} at your chosen settings."
    else:
        allocation = f"{asset2['name']} receives the higher weight because it improves the portfolio trade-off more strongly than {asset1['name']} at your chosen settings."

    if "Finance as Usual" in esg_mode:
        headline = "Why this portfolio?"
        model_text = "You selected the Finance as Usual Model, so the optimiser prioritises financial efficiency only. ESG is displayed for transparency, but it does not directly affect utility when λ = 0."
    elif "Exclusion Screen" in esg_mode:
        headline = "Why this portfolio?"
        model_text = f"You selected Sustainable Finance Model 1.0 - Exclusion Screen, so QGreen first removes assets below the minimum ESG threshold of {esg_threshold:.0f} before optimising the remaining opportunity set."
    elif "Best-in-Class" in esg_mode:
        headline = "Why this portfolio?"
        model_text = "You selected Sustainable Finance Model 2.0 - Best-in-Class, so QGreen applies an internal tilt toward the stronger relative ESG performer while still balancing expected return and portfolio risk. The displayed portfolio ESG score remains the true weighted average of the chosen assets."
    else:
        headline = "Why this portfolio?"
        model_text = f"You selected Sustainable Finance Model 3.0 - ESG Integration, so QGreen directly incorporates sustainability into utility alongside return and risk, with λ = {lambda_esg:.2f}."

    if risk_label == "Conservative 🛡️":
        risk_text = "Your risk profile is conservative, so the recommendation leans more heavily toward stability and lower volatility." 
    elif risk_label == "Balanced ⚖️":
        risk_text = "Your risk profile is balanced, so the recommendation aims to preserve a measured trade-off between growth potential and downside control."
    else:
        risk_text = "Your risk profile is growth-oriented, so the recommendation can accept more volatility in pursuit of stronger upside potential."

    html = f"""
<div class="why-box">
    <h4>{headline}</h4>
    <p><strong>{client_name}</strong>, this portfolio reflects the preferences and constraints you selected in QGreen.</p>
    <p>{model_text}</p>
    <p>{risk_text}</p>
    <p>{allocation}</p>
</div>
"""
    return html


def pick_auto_pair(df: pd.DataFrame, style: str, lambda_esg: float, esg_mode: str, esg_threshold: float):
    work = df.copy()
    if "Exclusion Screen" in esg_mode:
        work = work[work["esg_0_100"] >= esg_threshold]
    if len(work) < 2:
        return None, None

    target = 45 + 45 * lambda_esg
    if "Finance as Usual" in esg_mode:
        target = 50
    if style == "Conservative 🛡️":
        target += 5
    elif style == "Growth-Oriented 🚀":
        target -= 5
    target = max(20, min(95, target))

    work = work.assign(dist=(work["esg_0_100"] - target).abs())
    anchor = work.sort_values(["dist", "comname"]).iloc[0]

    if style == "Conservative 🛡️":
        companion_pool = work[work["esg_0_100"] >= anchor["esg_0_100"]].sort_values(
            ["esg_0_100", "comname"], ascending=[False, True]
        )
    elif style == "Growth-Oriented 🚀":
        companion_pool = work[work["esg_0_100"] <= anchor["esg_0_100"]].sort_values(
            ["esg_0_100", "comname"], ascending=[True, True]
        )
    else:
        companion_pool = work.sort_values("dist", ascending=False)

    companion_pool = companion_pool[companion_pool["comname"] != anchor["comname"]]
    if len(companion_pool) == 0:
        companion_pool = work[work["comname"] != anchor["comname"]]
    companion = companion_pool.iloc[0]
    return anchor, companion


def optimise_two_asset_portfolio(asset1, asset2, gamma, lambda_esg, corr, rf, esg_mode, esg_threshold):
    excluded = []
    if "Exclusion Screen" in esg_mode:
        if asset1["esg"] < esg_threshold:
            excluded.append(asset1["name"])
        if asset2["esg"] < esg_threshold:
            excluded.append(asset2["name"])
    if len(excluded) == 2:
        return {"error": f"Both assets fall below the ESG threshold of {esg_threshold:.0f}."}

    esg1_eff, esg2_eff = asset1["esg"], asset2["esg"]
    if "Best-in-Class" in esg_mode:
        if esg1_eff >= esg2_eff:
            esg1_eff = min(esg1_eff * 1.15, 100)
        else:
            esg2_eff = min(esg2_eff * 1.15, 100)

    def port_return(w):
        return w * asset1["ret"] + (1 - w) * asset2["ret"]

    def port_std(w):
        variance = (
            (w ** 2) * (asset1["sd"] ** 2)
            + ((1 - w) ** 2) * (asset2["sd"] ** 2)
            + 2 * corr * w * (1 - w) * asset1["sd"] * asset2["sd"]
        )
        return float(np.sqrt(max(variance, 1e-10)))

    def port_esg_raw(w):
        return w * asset1["esg"] + (1 - w) * asset2["esg"]

    def port_esg_effective(w):
        return w * esg1_eff + (1 - w) * esg2_eff

    def utility(w):
        return port_return(w) - 0.5 * gamma * (port_std(w) ** 2) + lambda_esg * (port_esg_effective(w) / 100)

    if asset1["name"] in excluded:
        weights = np.array([0.0])
    elif asset2["name"] in excluded:
        weights = np.array([1.0])
    else:
        weights = np.linspace(0, 1, 1000)

    all_ret = np.array([port_return(w) for w in weights])
    all_std = np.array([port_std(w) for w in weights])
    all_esg_raw = np.array([port_esg_raw(w) for w in weights])
    all_esg_effective = np.array([port_esg_effective(w) for w in weights])
    all_util = np.array([utility(w) for w in weights])
    all_sharpe = np.where(all_std > 0, (all_ret - rf) / all_std, -np.inf)

    tang_idx = int(np.argmax(all_sharpe))
    best_idx = int(np.argmax(all_util))

    return {
        "asset1": asset1,
        "asset2": asset2,
        "weights": weights,
        "all_ret": all_ret,
        "all_std": all_std,
        "all_esg": all_esg_raw,
        "all_esg_effective": all_esg_effective,
        "all_sharpe": all_sharpe,
        "all_util": all_util,
        "tang_idx": tang_idx,
        "best_idx": best_idx,
        "w1": float(weights[best_idx]),
        "w2": float(1 - weights[best_idx]),
        "ret_opt": float(all_ret[best_idx]),
        "std_opt": float(all_std[best_idx]),
        "esg_opt": float(all_esg_raw[best_idx]),
        "esg_opt_effective": float(all_esg_effective[best_idx]),
        "util_opt": float(all_util[best_idx]),
        "sharpe_opt": float((all_ret[best_idx] - rf) / all_std[best_idx]),
        "ret_tang": float(all_ret[tang_idx]),
        "std_tang": float(all_std[tang_idx]),
        "esg_tang": float(all_esg_raw[tang_idx]),
        "esg_tang_effective": float(all_esg_effective[tang_idx]),
        "sharpe_tang": float(all_sharpe[tang_idx]),
        "rf": rf,
        "excluded": excluded,
    }


# ============================================================
# HEADER
# ============================================================
mode_options = [
    "A) Let QGreen choose 2 companies for me",
    "B) I choose 2 assets by ticker",
    "C) I enter everything manually",
]
if "mode" not in st.session_state:
    st.session_state["mode"] = mode_options[0]
selected_mode_card = st.session_state.get("mode", mode_options[0])
st.markdown(
    """
<div class="hero">
    <h1>🌿 QGreen</h1>
    <p>QGreen is an innovative sustainable finance platform built to turn investor preferences into clear portfolio decisions — combining risk appetite, return objectives, and ESG priorities to deliver intelligent, personalised, and investment-ready recommendations.</p>
    <div>
        <span class="status-pill">Innovation</span>
        <span class="status-pill">Sustainability</span>
        <span class="status-pill">Precision</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

m1, m2, m3 = st.columns(3)
card_specs = [
    (
        "A) Auto Portfolio",
        "QGreen selects two companies for you using your risk profile and sustainability preferences.",
        "Automated selection",
        mode_options[0],
    ),
    (
        "B) Choose 2 Companies",
        "You choose the companies, and QGreen handles the optimisation and sustainability logic.",
        "Directed choice",
        mode_options[1],
    ),
    (
        "C) Full Manual",
        "You input return, risk, ESG scores, and correlation directly for full control.",
        "Full control",
        mode_options[2],
    ),
]

for col, (title, desc, badge, mode_value) in zip((m1, m2, m3), card_specs):
    selected_class = " selected" if selected_mode_card == mode_value else ""
    col.markdown(
        f"""
<div class='glass-card{selected_class}'>
    <h4>{title}</h4>
    <p>{desc}</p>
    <span class='mode-badge'>{badge}</span>
</div>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR INPUTS
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Portfolio Builder")

    client_name = st.text_input("Client name", value=st.session_state.get("client_name", ""), placeholder="Enter client name")
    st.session_state["client_name"] = client_name

    mode = st.radio(
        "Choose how you want to build your portfolio:",
        mode_options,
        key="mode",
    )

    st.markdown("---")
    st.markdown("### 📊 Step 1 — Risk quiz")
    q1 = st.radio(
        "If your portfolio falls 20%, what do you do?",
        ["Sell quickly", "Hold and wait", "Buy more while prices are lower"],
        index=1,
    )
    q2 = st.radio(
        "What is your investment horizon?",
        ["Under 2 years", "2 to 10 years", "Over 10 years"],
        index=1,
    )
    q3 = st.radio(
        "Which goal matters most?",
        ["Capital protection", "Balanced growth and stability", "Maximum growth"],
        index=1,
    )

    score_map = {
        "Sell quickly": 1,
        "Hold and wait": 2,
        "Buy more while prices are lower": 3,
        "Under 2 years": 1,
        "2 to 10 years": 2,
        "Over 10 years": 3,
        "Capital protection": 1,
        "Balanced growth and stability": 2,
        "Maximum growth": 3,
    }
    quiz_score = score_map[q1] + score_map[q2] + score_map[q3]
    gamma, risk_label = risk_profile_from_quiz(quiz_score)
    st.success(f"Profile: {risk_label}")
    st.caption(f"Risk aversion coefficient: γ = {gamma}")

    st.markdown("---")
    st.markdown("### 🌱 Step 2 — ESG preference quiz")
    st.caption("Each answer ranges from 0 to 3. QGreen uses your answers to derive λ and the sustainable finance model automatically.")

    q_esg1 = st.slider(
        "1. How important is it to you to avoid controversial sectors entirely?",
        min_value=0, max_value=3, value=2,
        help="0 = not important, 3 = very important",
    )
    q_esg2 = st.slider(
        "2. Would you prefer to compare firms relative to others in the same industry?",
        min_value=0, max_value=3, value=2,
        help="0 = no, 3 = yes, strongly",
    )
    q_esg3 = st.slider(
        "3. How important is it that your investments contribute to positive environmental or social outcomes?",
        min_value=0, max_value=3, value=2,
        help="0 = not important, 3 = very important",
    )
    q_esg4 = st.slider(
        "4. Would you accept slightly lower returns for stronger sustainability performance?",
        min_value=0, max_value=3, value=2,
        help="0 = no, 3 = yes, strongly",
    )
    q_esg5 = st.slider(
        "5. Environmental importance",
        min_value=0, max_value=3, value=2,
        help="0 = not important, 3 = very important",
    )
    q_esg6 = st.slider(
        "6. Social importance",
        min_value=0, max_value=3, value=2,
        help="0 = not important, 3 = very important",
    )
    q_esg7 = st.slider(
        "7. Governance importance",
        min_value=0, max_value=3, value=2,
        help="0 = not important, 3 = very important",
    )

    esg_pref = derive_esg_preferences([q_esg1, q_esg2, q_esg3, q_esg4, q_esg5, q_esg6, q_esg7])
    lambda_esg = esg_pref["lambda"]
    esg_mode = esg_pref["model_name"]

    st.markdown(
        f"""
<div class="strategy-box">
    <div class="strategy-title">Derived model</div>
    <div><strong>{esg_mode}</strong></div>
    <div style="margin-top: 0.3rem;">Score = <strong>{esg_pref['total']}/21</strong> · λ = <strong>{lambda_esg:.2f}</strong></div>
    <div style="margin-top: 0.35rem;">{esg_pref['description']}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    esg_threshold = 50.0
    if "Exclusion Screen" in esg_mode:
        esg_threshold = st.slider("Minimum ESG score allowed", 0, 100, 50)

    st.markdown("---")
    st.markdown("### 🔗 Market assumptions")
    corr = st.slider("Correlation between the two assets (ρ)", -1.0, 1.0, 0.30, 0.05)
    rf = st.number_input("Risk-free rate (%)", min_value=0.0, max_value=20.0, value=4.0, step=0.1) / 100

    run = st.button("🚀 Generate portfolio", type="primary", use_container_width=True)

display_client_name = client_name.strip() if client_name and client_name.strip() else "Client"

# ============================================================
# BUILD ASSETS FOR EACH MODE
# ============================================================
asset1 = asset2 = None
mode_explainer = ""
data_message = ""

if mode.startswith("A"):
    mode_explainer = "QGreen selected two companies for you using your risk profile and ESG preferences."
    if len(esg_df) >= 2:
        a1, a2 = pick_auto_pair(esg_df, risk_label, lambda_esg, esg_mode, esg_threshold)
        if a1 is not None and a2 is not None:
            asset1 = get_asset_from_row(a1, risk_label, "A")
            asset2 = get_asset_from_row(a2, risk_label, "A")
            if asset1["source"] == "Market data (last 3 years)" and asset2["source"] == "Market data (last 3 years)":
                data_message = "Expected return and risk were pulled automatically from recent market data."
            else:
                data_message = "Some live market data was unavailable, so QGreen used transparent built-in estimates where needed."

elif mode.startswith("B"):
    st.subheader("Choose your two assets")
    c1, c2 = st.columns(2)
    with c1:
        name1 = st.selectbox("Asset 1 ticker", company_names, key="b_company1")
    with c2:
        available2 = [n for n in company_names if n != name1]
        name2 = st.selectbox("Asset 2 ticker", available2, key="b_company2")

    row1 = esg_df.loc[esg_df["comname"] == name1].iloc[0]
    row2 = esg_df.loc[esg_df["comname"] == name2].iloc[0]
    asset1 = get_asset_from_row(row1, risk_label, "B")
    asset2 = get_asset_from_row(row2, risk_label, "B")
    mode_explainer = "You picked two ticker symbols and QGreen handled the rest."
    if asset1["source"] == "Market data (last 3 years)" and asset2["source"] == "Market data (last 3 years)":
        data_message = "Expected return and risk were pulled automatically from recent market data, so you only needed to choose the companies."
    else:
        data_message = "Live market data was unavailable for some entries, so QGreen used transparent app estimates where necessary."

else:
    st.subheader("Enter both assets manually")
    c1, c2 = st.columns(2)
    with c1:
        n1 = st.text_input("Asset 1 name", "Asset 1")
        t1 = st.text_input("Asset 1 ticker", "A1")
        r1 = st.number_input("Asset 1 expected return (%)", 0.0, 100.0, 10.0, 0.1, key="c_r1") / 100
        sd1 = st.number_input("Asset 1 risk / SD (%)", 0.1, 100.0, 18.0, 0.1, key="c_sd1") / 100
        esg1 = st.number_input("Asset 1 ESG score", 0.0, 100.0, 65.0, 0.1, key="c_esg1")
    with c2:
        n2 = st.text_input("Asset 2 name", "Asset 2")
        t2 = st.text_input("Asset 2 ticker", "A2")
        r2 = st.number_input("Asset 2 expected return (%)", 0.0, 100.0, 7.0, 0.1, key="c_r2") / 100
        sd2 = st.number_input("Asset 2 risk / SD (%)", 0.1, 100.0, 12.0, 0.1, key="c_sd2") / 100
        esg2 = st.number_input("Asset 2 ESG score", 0.0, 100.0, 85.0, 0.1, key="c_esg2")
    asset1 = {"name": n1, "ticker": t1, "ret": r1, "sd": sd1, "esg": esg1, "source": "Manual input", "mode": "C", "impact_profile": get_impact_profile(t1, esg1, n1), "impact_available": bool(get_impact_profile(t1, esg1, n1))}
    asset2 = {"name": n2, "ticker": t2, "ret": r2, "sd": sd2, "esg": esg2, "source": "Manual input", "mode": "C", "impact_profile": get_impact_profile(t2, esg2, n2), "impact_available": bool(get_impact_profile(t2, esg2, n2))}
    mode_explainer = "You entered both assets manually."

# ============================================================
# PRE-RUN SCREEN
# ============================================================
if not run:
    st.markdown("### How to use QGreen")
    st.markdown(
        f"""
<div class="soft-box">
    <h4>Selected mode</h4>
    <p><strong>{mode}</strong></p>
    <p><strong>Client:</strong> {display_client_name}</p>
    <p>{mode_explainer if mode_explainer else 'Choose a mode, set your preferences, then click Generate portfolio.'}</p>
    <ul>
        <li><strong>Auto Portfolio</strong> selects two companies for you.</li>
        <li><strong>Choose 2 Companies</strong> lets you choose firms while QGreen handles the optimisation.</li>
        <li><strong>Full Manual</strong> gives complete control over the two-asset inputs.</li>
    </ul>
</div>
""",
        unsafe_allow_html=True,
    )
    st.stop()

# ============================================================
# OPTIMISE
# ============================================================
result = optimise_two_asset_portfolio(asset1, asset2, gamma, lambda_esg, corr, rf, esg_mode, esg_threshold)
if result.get("error"):
    st.error(result["error"])
    st.stop()

w1 = result["w1"]
w2 = result["w2"]
ret_opt = result["ret_opt"]
std_opt = result["std_opt"]
esg_opt = result["esg_opt"]
esg_opt_effective = result["esg_opt_effective"]
sharpe_opt = result["sharpe_opt"]
ret_tang = result["ret_tang"]
std_tang = result["std_tang"]
esg_tang = result["esg_tang"]
sharpe_tang = result["sharpe_tang"]

st.markdown(f"## 🎯 {display_client_name}’s QGreen Recommendation")
st.caption(f"Client: {display_client_name} · Mode: {mode} · Risk profile: {risk_label} · γ = {gamma} · λ = {lambda_esg:.2f} · {esg_mode}")
st.markdown(f"<div class='note-box'><strong>{display_client_name}</strong>, this recommendation is tailored to your selected mode, risk profile, and sustainability preferences.<br><br>{mode_explainer}<br><br>{data_message}</div>", unsafe_allow_html=True)
story_html = build_portfolio_story(display_client_name, esg_mode, risk_label, result, asset1, asset2, w1, w2, lambda_esg, esg_threshold)
impact_summary = compute_impact_snapshot(asset1, asset2, w1, w2)

if "Best-in-Class" in esg_mode:
    st.caption(f"Displayed ESG scores are true weighted averages. An internal best-in-class tilt is used only inside the optimiser (effective ESG at the recommended portfolio: {esg_opt_effective:.2f}/100).")

summary_left, summary_right = st.columns([1.05, 0.95])

with summary_left:
    st.markdown(
        f"""
<div class="metric-grid">
    <div class="metric-card">
        <div class="metric-label">Expected return</div>
        <div class="metric-value">{ret_opt*100:.2f}%</div>
        <div class="metric-sub">Annualised return</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Risk (SD)</div>
        <div class="metric-value">{std_opt*100:.2f}%</div>
        <div class="metric-sub">Portfolio volatility</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Portfolio ESG</div>
        <div class="metric-value">{esg_opt:.2f} / 100</div>
        <div class="metric-sub">Weighted ESG score</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Sharpe ratio</div>
        <div class="metric-value">{sharpe_opt:.2f}</div>
        <div class="metric-sub">Risk-adjusted return</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    out = pd.DataFrame(
        {
            "Asset": [asset1["name"], asset2["name"]],
            "Ticker": [asset1["ticker"], asset2["ticker"]],
            "Weight": [f"{w1*100:.2f}%", f"{w2*100:.2f}%"],
            "Expected return": [f"{asset1['ret']*100:.2f}%", f"{asset2['ret']*100:.2f}%"],
            "Risk / SD": [f"{asset1['sd']*100:.2f}%", f"{asset2['sd']*100:.2f}%"],
            "ESG score": [f"{asset1['esg']:.2f}", f"{asset2['esg']:.2f}"],
        }
    )
    st.markdown(
        "<div class='asset-table-wrap'>" + out.to_html(index=False, classes='asset-table', border=0) + "</div>",
        unsafe_allow_html=True,
    )

    if result["excluded"]:
        allocation_reason = f"Exclusion screening removed: {', '.join(result['excluded'])}."
    elif w1 > w2:
        allocation_reason = f"{asset1['name']} receives the larger weight because it contributes more to overall utility after balancing return, risk, and sustainability preferences."
    elif w2 > w1:
        allocation_reason = f"{asset2['name']} receives the larger weight because it contributes more to overall utility after balancing return, risk, and sustainability preferences."
    else:
        allocation_reason = "Both assets receive similar weights because the combined return-risk-sustainability trade-off is balanced."


with summary_right:
    fig2, ax2 = plt.subplots(figsize=(6.0, 4.1))
    fig2.patch.set_facecolor("#f4fbf5")
    wedges, texts, autotexts = ax2.pie(
        [max(w1, 0.0001), max(w2, 0.0001)],
        labels=[asset1["name"], asset2["name"]],
        autopct="%1.1f%%",
        colors=["#2E7D32", "#66BB6A"],
        startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 2.5},
    )
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
    ax2.set_title("Recommended allocation", color="#123321", fontweight="bold")
    st.pyplot(fig2)

    fig3, ax3 = plt.subplots(figsize=(6.0, 3.3))
    fig3.patch.set_facecolor("#f4fbf5")
    ax3.set_facecolor("#f4fbf5")
    scores = [asset1["esg"], asset2["esg"], esg_opt]
    labels = [asset1["name"], asset2["name"], "Your Portfolio"]
    bars = ax3.barh(labels, scores, color=["#145A32", "#2E8B57", "#7BC67E"])
    for bar, val in zip(bars, scores):
        ax3.text(val + 0.8, bar.get_y() + bar.get_height() / 2, f"{val:.2f}", va="center", fontweight="bold")
    ax3.set_xlim(0, 110)
    ax3.set_xlabel("ESG score")
    ax3.set_title("ESG score comparison", color="#123321", fontweight="bold")
    ax3.grid(True, axis="x", alpha=0.25)
    st.pyplot(fig3)
    st.caption("The portfolio ESG score shown here is the true weighted average of Asset 1 and Asset 2.")

allocation_col, story_col = st.columns([1.35, 1.0], gap="large")
with allocation_col:
    st.markdown(
        f"""
<div class="rec-box">
    <h4>Recommended allocation</h4>
    <p><strong>Prepared for {display_client_name}</strong></p>
    <p><strong>{w1*100:.0f}% in {asset1["name"]}</strong> and <strong>{w2*100:.0f}% in {asset2["name"]}</strong></p>
    <ul>
        <li>Expected annual return: <strong>{ret_opt*100:.2f}%</strong></li>
        <li>Risk (standard deviation): <strong>{std_opt*100:.2f}%</strong></li>
        <li>Portfolio ESG score: <strong>{esg_opt:.2f}/100</strong></li>
        <li>Sharpe ratio: <strong>{sharpe_opt:.2f}</strong></li>
    </ul>
    <p>{allocation_reason}</p>
</div>
""",
        unsafe_allow_html=True,
    )
with story_col:
    st.markdown(story_html, unsafe_allow_html=True)

portfolio_tab, esg_tab, impact_tab, method_tab = st.tabs(["📈 Portfolio Frontier", "🌱 ESG Frontier", "🌍 Impact Metrics", "🧠 Methodology"])

with portfolio_tab:
    st.markdown("### Portfolio frontier")
    st.caption("Risk-return frontier for all feasible two-asset portfolios. This is the standard portfolio frontier, not the ESG frontier.")
    fig_pf, ax_pf = plt.subplots(figsize=(9.2, 5.0))
    fig_pf.patch.set_facecolor("#f4fbf5")
    ax_pf.set_facecolor("#f4fbf5")
    sc = ax_pf.scatter(
        result["all_std"] * 100,
        result["all_ret"] * 100,
        c=result["all_esg"],
        cmap="RdYlGn",
        s=18,
        alpha=0.86,
        vmin=0,
        vmax=100,
    )
    cbar = plt.colorbar(sc, ax=ax_pf)
    cbar.set_label("ESG score")

    cml_x = np.linspace(0, max(result["all_std"]) * 100 * 1.25, 200)
    if std_tang > 0:
        cml_y = rf * 100 + ((ret_tang - rf) / std_tang) * (cml_x / 100) * 100
        ax_pf.plot(cml_x, cml_y, color="#2e7d32", linestyle="--", lw=1.8, label="Capital Market Line")

    ax_pf.scatter(0, rf * 100, color="#1b5e20", marker="s", s=90, label="Risk-free asset")
    ax_pf.scatter(asset1["sd"] * 100, asset1["ret"] * 100, color="#6A1B9A", marker="D", s=95, label=asset1["name"])
    ax_pf.scatter(asset2["sd"] * 100, asset2["ret"] * 100, color="#EF6C00", marker="D", s=95, label=asset2["name"])
    ax_pf.scatter(std_tang * 100, ret_tang * 100, color="#D32F2F", marker="*", s=230, label="Tangency portfolio")
    ax_pf.scatter(std_opt * 100, ret_opt * 100, color="#43A047", marker="*", s=255, label="Optimal portfolio")
    ax_pf.set_xlabel("Risk — standard deviation (%)")
    ax_pf.set_ylabel("Expected return (%)")
    ax_pf.set_title("Portfolio Frontier")
    ax_pf.grid(True, alpha=0.28)
    ax_pf.legend(fontsize=8.5, loc="lower right")
    st.pyplot(fig_pf)

with esg_tab:
    st.markdown("### ESG frontier")
    st.caption("This frontier shows the trade-off between the portfolio's actual weighted-average ESG score and Sharpe ratio across all feasible two-asset portfolios.")
    fig_esg, ax_esg = plt.subplots(figsize=(9.2, 5.0))
    fig_esg.patch.set_facecolor("#f4fbf5")
    ax_esg.set_facecolor("#f4fbf5")

    ax_esg.plot(result["all_esg"], result["all_sharpe"], color="#2e7d32", lw=2.2, label="ESG frontier")
    ax_esg.scatter(esg_tang, sharpe_tang, marker="X", color="#D32F2F", s=110, label="Tangency portfolio")
    ax_esg.scatter(esg_opt, sharpe_opt, marker="D", color="#2e7d32", s=110, label="Optimal portfolio")
    ax_esg.axvline(esg_opt, color="#2e7d32", linestyle=":", lw=1.2, alpha=0.7)
    ax_esg.axhline(sharpe_opt, color="#2e7d32", linestyle=":", lw=1.2, alpha=0.7)
    ax_esg.set_xlabel("Portfolio ESG score")
    ax_esg.set_ylabel("Sharpe ratio")
    ax_esg.set_title("ESG Frontier")
    ax_esg.grid(True, alpha=0.28)
    ax_esg.legend()
    st.pyplot(fig_esg)

with impact_tab:
    st.markdown("### Executive impact dashboard")
    if impact_summary.get("available"):
        coverage_class = "positive" if impact_summary["coverage_weight"] >= 99 else ("neutral" if impact_summary["coverage_weight"] >= 70 else "caution")
        headline = f"Impact metrics are available for {display_client_name}'s recommended allocation."

        metric_cards = []
        if pd.notna(impact_summary.get("emissions_score_port")):
            metric_cards.append(dedent(f"""
<div class="impact-card">
    <div class="impact-kicker">Emissions management</div>
    <div class="impact-value">{format_number_or_na(impact_summary.get('emissions_score_port'), ' / 100', 1)}</div>
    <div class="impact-detail">Weighted LSEG emissions score across matched holdings</div>
</div>"""))
        if pd.notna(impact_summary.get("gender_diversity_port")):
            metric_cards.append(dedent(f"""
<div class="impact-card">
    <div class="impact-kicker">Board diversity</div>
    <div class="impact-value">{format_percent_or_na(impact_summary.get('gender_diversity_port'), 1)}</div>
    <div class="impact-detail">Weighted board gender diversity across matched holdings</div>
</div>"""))
        if pd.notna(impact_summary.get("emissions_trading_share")):
            metric_cards.append(dedent(f"""
<div class="impact-card">
    <div class="impact-kicker">Emissions trading</div>
    <div class="impact-value">{format_percent_or_na(impact_summary.get('emissions_trading_share'), 0)}</div>
    <div class="impact-detail">Portfolio weight in companies flagged for emissions-trading participation</div>
</div>"""))
        if pd.notna(impact_summary.get("biodiversity_share")):
            metric_cards.append(dedent(f"""
<div class="impact-card">
    <div class="impact-kicker">Biodiversity coverage</div>
    <div class="impact-value">{format_percent_or_na(impact_summary.get('biodiversity_share'), 0)}</div>
    <div class="impact-detail">Portfolio weight in companies with biodiversity-impact reduction coverage</div>
</div>"""))

        if not metric_cards:
            metric_cards.append(dedent("""
<div class="impact-card">
    <div class="impact-kicker">Impact data</div>
    <div class="impact-value">Available</div>
    <div class="impact-detail">Matched LSEG rows were found, but the most visible impact fields are sparse for these holdings.</div>
</div>"""))

        impact_chart_labels = []
        impact_chart_values = []
        if pd.notna(impact_summary.get("emissions_score_port")):
            impact_chart_labels.append("Emissions score")
            impact_chart_values.append(float(impact_summary.get("emissions_score_port")))
        if pd.notna(impact_summary.get("gender_diversity_port")):
            impact_chart_labels.append("Board diversity")
            impact_chart_values.append(float(impact_summary.get("gender_diversity_port")))
        if pd.notna(impact_summary.get("emissions_trading_share")):
            impact_chart_labels.append("Emissions trading")
            impact_chart_values.append(float(impact_summary.get("emissions_trading_share")))
        if pd.notna(impact_summary.get("biodiversity_share")):
            impact_chart_labels.append("Biodiversity")
            impact_chart_values.append(float(impact_summary.get("biodiversity_share")))

        if impact_chart_labels:
            fig_imp, ax_imp = plt.subplots(figsize=(7.6, 3.2))
            fig_imp.patch.set_facecolor("#f6fbf7")
            ax_imp.set_facecolor("#f6fbf7")
            bars = ax_imp.barh(impact_chart_labels, impact_chart_values)
            ax_imp.set_xlim(0, 100)
            ax_imp.set_xlabel("Score / coverage (%)")
            ax_imp.set_title("Impact profile snapshot")
            ax_imp.grid(True, axis="x", alpha=0.22)
            for bar, val in zip(bars, impact_chart_values):
                ax_imp.text(min(val + 1.2, 98), bar.get_y() + bar.get_height()/2, f"{val:.1f}", va="center", fontsize=9)
            st.pyplot(fig_imp)

        st.markdown(
            f"""
<div class="impact-shell">
    <h4>Boardroom-ready sustainability view</h4>
    <p>{headline} This section reframes the uploaded LSEG impact data into portfolio-level indicators that can support an investment-committee conversation. The figures describe <strong>portfolio exposure and issuer characteristics</strong>; they are not avoided emissions or real-world emissions reductions.</p>
    <div class="impact-topline">
        <span class="impact-pill impact-pill-{coverage_class}">Data coverage · {impact_summary['coverage_weight']:.0f}% of portfolio weight</span>
    </div>
    <div class="impact-grid">
        {''.join(metric_cards)}
    </div>
    <div class="impact-note">
        <strong>Investment-committee read-out:</strong>
        <ul>
            {''.join(f"<li>{item}</li>" for item in impact_summary['insights'])}
        </ul>
        <p style="margin-top:0.55rem;"><strong>Interpretation:</strong> These are absolute portfolio indicators from the uploaded LSEG extract and should be read as portfolio characteristics rather than emissions reductions.</p>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.info("Impact metrics are shown when the selected firms can be matched to the uploaded LSEG impact extract in ESGMore.csv.")

with method_tab:
    st.markdown("### How QGreen works")
    st.markdown(
        f"""
<div class="soft-box">
    <h4>Utility function</h4>
    <p>QGreen converts your quiz answers into a <strong>risk-aversion coefficient (γ = {gamma})</strong> and an <strong>ESG preference strength (λ = {lambda_esg:.2f})</strong>.</p>
    <p>It then evaluates many possible portfolio weights and selects the one that maximises:</p>
    <p><strong>U = E[Rₚ] − 0.5 · γ · σ²ₚ + λ · ESGₚ / 100</strong></p>
    <p>So the recommendation balances <strong>expected return</strong>, <strong>risk</strong>, and <strong>sustainability</strong>.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    if impact_summary.get("available"):
        st.markdown(
            """
<div class="soft-box">
    <h4>Impact metrics methodology</h4>
    <p>The impact panel uses the uploaded 2025 LSEG dataset to compute weighted portfolio indicators from company-level reported emissions, diversity, and policy fields. These are portfolio exposure proxies and should not be interpreted as financed emissions, avoided emissions, or causal emissions reductions.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
<div class="soft-box">
    <h4>Current sustainable finance model</h4>
    <p><strong>{esg_mode}</strong></p>
    <p>{esg_pref['description']}</p>
    <ul>
        <li><strong>Finance as Usual Model</strong>: λ = 0, so ESG has no direct effect on utility.</li>
        <li><strong>Sustainable Finance Model 1.0 - Exclusion Screen</strong>: lower-ESG assets can be screened out.</li>
        <li><strong>Sustainable Finance Model 2.0 - Best-in-Class</strong>: stronger relative ESG performers receive an internal optimisation tilt, while displayed portfolio ESG remains the true weighted average.</li>
        <li><strong>Sustainable Finance Model 3.0 - ESG Integration</strong>: ESG enters utility directly alongside return and risk.</li>
    </ul>
</div>
""",
        unsafe_allow_html=True,
    )


st.markdown(
    """
<div class="disclaimer">
This tool is for educational purposes and should not be treated as personal financial advice.
</div>
""",
    unsafe_allow_html=True,
)
