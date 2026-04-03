import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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
st.markdown("""
<style>
    .stApp { background-color: #f7faf7 !important; color: #1a1a1a !important; }
    p, span, label, div, li, td, th, h1, h2, h3, h4, h5, h6,
    .stMarkdown, .stMarkdown p, .stMarkdown li { color: #1a1a1a !important; }

    input, textarea, select, input[type="number"], input[type="text"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #a5d6a7 !important;
        border-radius: 6px !important;
    }

    div[data-baseweb="input"] { background-color: #ffffff !important; }
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    div[data-baseweb="select"] * { color: #1a1a1a !important; }
    div[data-baseweb="popover"], div[role="listbox"], ul[role="listbox"], li[role="option"] {
        background: #ffffff !important;
        color: #1a1a1a !important;
    }
    div[data-baseweb="popover"] *, div[role="listbox"] *, ul[role="listbox"] *, li[role="option"] * {
        color: #1a1a1a !important;
        background: transparent !important;
    }
    li[role="option"][aria-selected="true"] {
        background: #e8f5e9 !important;
        color: #1a1a1a !important;
    }

    .stRadio label, .stRadio div, .stSlider label, .stSlider p { color: #1a1a1a !important; }
    section[data-testid="stSidebar"] { background-color: #f1f8f1 !important; }
    section[data-testid="stSidebar"] * { color: #1a1a1a !important; }

    .qgreen-header {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%);
        color: white !important;
        padding: 2.2rem 2rem 1.8rem 2rem;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 15px rgba(27,94,32,0.25);
    }
    .qgreen-header h1 { font-size: 3rem; margin: 0; letter-spacing: 1px; color: white !important; }
    .qgreen-header p  { font-size: 1.05rem; margin: 0.4rem 0 0 0; opacity: 0.95; color: white !important; }

    div[data-testid="metric-container"] {
        background: white !important;
        border: 1px solid #c8e6c9 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    }
    div[data-testid="metric-container"] * { color: #1a1a1a !important; }
    div[data-testid="metric-container"] label { color: #2E7D32 !important; font-weight: 600 !important; }

    .stDataFrame, .stDataFrame * { color: #1a1a1a !important; background-color: white !important; }

    .mode-card {
        background: white;
        border: 1px solid #d9eadb;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        min-height: 165px;
        box-shadow: 0 1px 8px rgba(0,0,0,0.04);
    }
    .mode-card h4 { margin-top: 0; color: #1B5E20 !important; }

    .rec-box {
        background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
        border-left: 5px solid #2E7D32;
        border-radius: 8px;
        padding: 1.1rem 1.35rem;
        margin-top: 1rem;
        color: #1a1a1a !important;
    }
    .rec-box * { color: #1a1a1a !important; }

    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #1e88e5;
        border-radius: 8px;
        padding: 0.9rem 1rem;
        margin: 0.75rem 0 1rem 0;
    }

    .disclaimer {
        background: #fff8e1;
        border-left: 4px solid #f9a825;
        border-radius: 6px;
        padding: 0.7rem 1rem;
        font-size: 0.85rem;
        color: #555 !important;
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA
# ============================================================
@st.cache_data
def load_esg_data():
    try:
        df = pd.read_csv("esg_scores.csv")
        df = df.dropna(subset=["comname", "ticker", "esg_0_100"]).copy()
        df["comname"] = df["comname"].astype(str).str.strip()
        df["ticker"] = df["ticker"].astype(str).str.strip()
        df["esg_0_100"] = pd.to_numeric(df["esg_0_100"], errors="coerce")
        df = df.dropna(subset=["esg_0_100"]).sort_values("comname")
        return df
    except Exception:
        return pd.DataFrame(columns=["comname", "ticker", "esg_0_100"])

esg_df = load_esg_data()
company_names = esg_df["comname"].tolist()

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
            "source": "Market data (last 3 years)"
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
    return {
        "name": str(row["comname"]).title(),
        "ticker": str(row["ticker"]),
        "ret": float(ret),
        "sd": float(sd),
        "esg": float(row["esg_0_100"]),
        "source": source,
        "mode": mode_label,
    }


def pick_auto_pair(df: pd.DataFrame, style: str, lambda_esg: float, esg_mode: str, esg_threshold: float):
    work = df.copy()
    if esg_mode.startswith("🚫"):
        work = work[work["esg_0_100"] >= esg_threshold]
    if len(work) < 2:
        return None, None

    target = 45 + 45 * lambda_esg
    if style == "Conservative 🛡️":
        target += 5
    elif style == "Growth-Oriented 🚀":
        target -= 5
    target = max(20, min(95, target))

    work = work.assign(dist=(work["esg_0_100"] - target).abs())
    anchor = work.sort_values(["dist", "comname"]).iloc[0]

    if style == "Conservative 🛡️":
        companion_pool = work[work["esg_0_100"] >= anchor["esg_0_100"]].sort_values(["esg_0_100", "comname"], ascending=[False, True])
    elif style == "Growth-Oriented 🚀":
        companion_pool = work[work["esg_0_100"] <= anchor["esg_0_100"]].sort_values(["esg_0_100", "comname"], ascending=[True, True])
    else:
        companion_pool = work.sort_values("dist", ascending=False)

    companion_pool = companion_pool[companion_pool["comname"] != anchor["comname"]]
    if len(companion_pool) == 0:
        companion_pool = work[work["comname"] != anchor["comname"]]
    companion = companion_pool.iloc[0]
    return anchor, companion


def optimise_two_asset_portfolio(asset1, asset2, gamma, lambda_esg, corr, rf, esg_mode, esg_threshold):
    excluded = []
    if esg_mode.startswith("🚫"):
        if asset1["esg"] < esg_threshold:
            excluded.append(asset1["name"])
        if asset2["esg"] < esg_threshold:
            excluded.append(asset2["name"])
    if len(excluded) == 2:
        return {"error": f"Both assets fall below the ESG threshold of {esg_threshold:.0f}."}

    esg1_eff, esg2_eff = asset1["esg"], asset2["esg"]
    if esg_mode.startswith("🏅"):
        if esg1_eff >= esg2_eff:
            esg1_eff = min(esg1_eff * 1.15, 100)
        else:
            esg2_eff = min(esg2_eff * 1.15, 100)

    def port_return(w):
        return w * asset1["ret"] + (1 - w) * asset2["ret"]

    def port_std(w):
        v = (w**2) * (asset1["sd"]**2) + ((1 - w)**2) * (asset2["sd"]**2) + 2 * corr * w * (1 - w) * asset1["sd"] * asset2["sd"]
        return float(np.sqrt(max(v, 1e-10)))

    def port_esg(w):
        return w * esg1_eff + (1 - w) * esg2_eff

    def utility(w):
        return port_return(w) - 0.5 * gamma * (port_std(w) ** 2) + lambda_esg * (port_esg(w) / 100)

    if asset1["name"] in excluded:
        weights = np.array([0.0])
    elif asset2["name"] in excluded:
        weights = np.array([1.0])
    else:
        weights = np.linspace(0, 1, 1000)

    all_ret = np.array([port_return(w) for w in weights])
    all_std = np.array([port_std(w) for w in weights])
    all_esg = np.array([port_esg(w) for w in weights])
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
        "all_esg": all_esg,
        "w1": float(weights[best_idx]),
        "w2": float(1 - weights[best_idx]),
        "ret_opt": float(all_ret[best_idx]),
        "std_opt": float(all_std[best_idx]),
        "esg_opt": float(all_esg[best_idx]),
        "util_opt": float(all_util[best_idx]),
        "sharpe_opt": float((all_ret[best_idx] - rf) / all_std[best_idx]),
        "ret_tang": float(all_ret[tang_idx]),
        "std_tang": float(all_std[tang_idx]),
        "rf": rf,
        "excluded": excluded,
        "esg1_eff": esg1_eff,
        "esg2_eff": esg2_eff,
    }

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="qgreen-header">
    <h1>🌿 QGreen</h1>
    <p>Personalised sustainable portfolio recommendations based on your risk and ESG preferences</p>
</div>
""", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
m1.markdown("""<div class='mode-card'><h4>A) Auto Portfolio</h4>
QGreen chooses <strong>two companies for you</strong> using your quiz answers and ESG preferences.</div>""", unsafe_allow_html=True)
m2.markdown("""<div class='mode-card'><h4>B) Choose 2 Companies</h4>
You pick <strong>two real companies</strong>. QGreen pulls the company data for you and builds the portfolio automatically.</div>""", unsafe_allow_html=True)
m3.markdown("""<div class='mode-card'><h4>C) Full Manual</h4>
You enter <strong>everything yourself</strong>: expected return, risk, correlation, risk-free rate, and ESG scores.</div>""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR INPUTS
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Portfolio Builder")

    mode = st.radio(
        "Choose how you want to build your portfolio:",
        [
            "A) Let QGreen choose 2 companies for me",
            "B) I choose 2 real companies",
            "C) I enter everything manually",
        ],
        index=0,
    )

    st.markdown("---")
    st.markdown("### 📊 Step 1 — Risk quiz")
    q1 = st.radio("If your portfolio falls 20%, what do you do?",
                  ["Sell quickly", "Hold and wait", "Buy more while prices are lower"], index=1)
    q2 = st.radio("What is your investment horizon?",
                  ["Under 2 years", "2 to 10 years", "Over 10 years"], index=1)
    q3 = st.radio("Which goal matters most?",
                  ["Capital protection", "Balanced growth and stability", "Maximum growth"], index=1)

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
    st.success(f"Profile: **{risk_label}**  \\nRisk aversion coefficient: **γ = {gamma}**")

    st.markdown("---")
    st.markdown("### 🌱 Step 2 — ESG preferences")
    esg_mode = st.selectbox(
        "ESG strategy",
        [
            "🚫 Model 1.0 — Exclusion screening",
            "🏅 Model 2.0 — Best-in-class tilt",
            "🌍 Model 3.0 — Full ESG integration",
        ],
    )
    lambda_esg = st.slider("How strongly should ESG matter? (λ)", 0.0, 1.0, 0.50, 0.05)
    esg_threshold = 50.0
    if esg_mode.startswith("🚫"):
        esg_threshold = st.slider("Minimum ESG score allowed", 0, 100, 50)

    st.markdown("---")
    st.markdown("### 🔗 Market assumptions")
    corr = st.slider("Correlation between the two assets (ρ)", -1.0, 1.0, 0.30, 0.05)
    rf = st.number_input("Risk-free rate (%)", min_value=0.0, max_value=20.0, value=4.0, step=0.1) / 100

    run = st.button("🚀 Generate portfolio", type="primary", use_container_width=True)

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
                data_message = "Some live market data was unavailable, so QGreen used built-in estimates for any missing values."

elif mode.startswith("B"):
    st.subheader("Choose your two companies")
    c1, c2 = st.columns(2)
    with c1:
        name1 = st.selectbox("Company 1", company_names, key="b_company1")
    with c2:
        available2 = [n for n in company_names if n != name1]
        name2 = st.selectbox("Company 2", available2, key="b_company2")

    row1 = esg_df.loc[esg_df["comname"] == name1].iloc[0]
    row2 = esg_df.loc[esg_df["comname"] == name2].iloc[0]
    asset1 = get_asset_from_row(row1, risk_label, "B")
    asset2 = get_asset_from_row(row2, risk_label, "B")
    mode_explainer = "You picked two companies and QGreen handled the rest."
    if asset1["source"] == "Market data (last 3 years)" and asset2["source"] == "Market data (last 3 years)":
        data_message = "Expected return and risk were pulled automatically from recent market data, so you only needed to choose the two companies."
    else:
        data_message = "QGreen tried to pull recent market data automatically. Where live data was unavailable, it used built-in estimates so you still did not need to enter stock information manually."

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
    asset1 = {"name": n1, "ticker": t1, "ret": r1, "sd": sd1, "esg": esg1, "source": "Manual input", "mode": "C"}
    asset2 = {"name": n2, "ticker": t2, "ret": r2, "sd": sd2, "esg": esg2, "source": "Manual input", "mode": "C"}
    mode_explainer = "You entered both assets manually."

# ============================================================
# PRE-RUN SCREEN
# ============================================================
if not run:
    st.markdown("### How to use QGreen")
    st.markdown(f"**Selected mode:** {mode}")
    st.markdown(mode_explainer if mode_explainer else "Choose a mode, set your preferences, then click Generate portfolio.")
    st.markdown("""
- **A) Auto Portfolio** is the fastest route: QGreen chooses two companies for you.
- **B) Choose 2 Companies** lets you pick two real firms while QGreen automatically handles the portfolio inputs.
- **C) Full Manual** gives you complete control over both assets.
    """)
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
sharpe_opt = result["sharpe_opt"]
ret_tang = result["ret_tang"]
std_tang = result["std_tang"]

st.markdown("## 🎯 Your QGreen Recommendation")
st.caption(f"Mode: **{mode}** · Risk profile: **{risk_label}** · γ = **{gamma}** · λ = **{lambda_esg:.2f}**")
st.markdown(f"<div class='info-box'>{mode_explainer}<br><br>{data_message}</div>", unsafe_allow_html=True)

# ============================================================
# RESULTS + VISUALS TOGETHER
# ============================================================
summary_left, summary_right = st.columns([1.05, 0.95])

with summary_left:
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Expected return", f"{ret_opt*100:.2f}%")
    r2.metric("Risk (SD)", f"{std_opt*100:.2f}%")
    r3.metric("Portfolio ESG", f"{esg_opt:.1f} / 100")
    r4.metric("Sharpe ratio", f"{sharpe_opt:.2f}")

    out = pd.DataFrame({
        "Asset": [asset1["name"], asset2["name"]],
        "Ticker": [asset1["ticker"], asset2["ticker"]],
        "Weight": [f"{w1*100:.1f}%", f"{w2*100:.1f}%"],
        "Expected return": [f"{asset1['ret']*100:.1f}%", f"{asset2['ret']*100:.1f}%"],
        "Risk / SD": [f"{asset1['sd']*100:.1f}%", f"{asset2['sd']*100:.1f}%"],
        "ESG score": [f"{asset1['esg']:.1f}", f"{asset2['esg']:.1f}"],
    })
    st.dataframe(out, use_container_width=True, hide_index=True)

    if result["excluded"]:
        allocation_reason = f"Exclusion screening removed: {', '.join(result['excluded'])}."
    elif w1 > w2:
        allocation_reason = f"{asset1['name']} receives the larger weight because it adds more to your overall utility after balancing return, risk, and ESG preferences."
    elif w2 > w1:
        allocation_reason = f"{asset2['name']} receives the larger weight because it adds more to your overall utility after balancing return, risk, and ESG preferences."
    else:
        allocation_reason = "Both assets receive similar weights because their combined return-risk-ESG trade-off is balanced."

    st.markdown(f"""
<div class="rec-box">
<h4>QGreen recommends:</h4>
<p><strong>{w1*100:.0f}% in {asset1['name']}</strong> and <strong>{w2*100:.0f}% in {asset2['name']}</strong></p>
<ul>
<li>Expected annual return: <strong>{ret_opt*100:.2f}%</strong></li>
<li>Risk (standard deviation): <strong>{std_opt*100:.2f}%</strong></li>
<li>Portfolio ESG score: <strong>{esg_opt:.1f}/100</strong></li>
<li>Sharpe ratio: <strong>{sharpe_opt:.2f}</strong></li>
</ul>
<p>{allocation_reason}</p>
</div>
""", unsafe_allow_html=True)

with summary_right:
    fig2, ax2 = plt.subplots(figsize=(6.2, 4.3))
    fig2.patch.set_facecolor("#f7faf7")
    wedges, texts, autotexts = ax2.pie(
        [max(w1, 0.0001), max(w2, 0.0001)],
        labels=[asset1["name"], asset2["name"]],
        autopct="%1.1f%%",
        colors=["#1565C0", "#2E7D32"],
        startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 2.5},
    )
    for a in autotexts:
        a.set_color("white")
        a.set_fontweight("bold")
    ax2.set_title("Recommended allocation")
    st.pyplot(fig2)

    fig3, ax3 = plt.subplots(figsize=(6.2, 3.2))
    fig3.patch.set_facecolor("#f7faf7")
    ax3.set_facecolor("#f7faf7")
    bars = ax3.barh([asset1["name"], asset2["name"], "Your Portfolio"], [asset1["esg"], asset2["esg"], esg_opt], color=["#1565C0", "#2E7D32", "#FF6F00"])
    for bar, val in zip(bars, [asset1["esg"], asset2["esg"], esg_opt]):
        ax3.text(val + 0.8, bar.get_y() + bar.get_height()/2, f"{val:.1f}", va="center", fontweight="bold")
    ax3.set_xlim(0, 110)
    ax3.set_xlabel("ESG score")
    ax3.set_title("ESG score comparison")
    ax3.grid(True, axis="x", alpha=0.3)
    st.pyplot(fig3)

st.markdown("### Portfolio frontier")
fig, ax = plt.subplots(figsize=(9, 4.8))
fig.patch.set_facecolor("#f7faf7")
ax.set_facecolor("#f7faf7")
sc = ax.scatter(result["all_std"]*100, result["all_ret"]*100, c=result["all_esg"], cmap="RdYlGn", s=16, alpha=0.85, vmin=0, vmax=100)
plt.colorbar(sc, ax=ax, label="ESG score")
cml_x = np.linspace(0, max(result["all_std"])*100*1.25, 200)
if std_tang > 0:
    cml_y = rf*100 + ((ret_tang - rf) / std_tang) * (cml_x / 100) * 100
    ax.plot(cml_x, cml_y, "g--", lw=1.6, label="Capital Market Line")
ax.scatter(0, rf*100, color="green", marker="s", s=85, label="Risk-free")
ax.scatter(asset1["sd"]*100, asset1["ret"]*100, color="#6A1B9A", marker="D", s=90, label=asset1["name"])
ax.scatter(asset2["sd"]*100, asset2["ret"]*100, color="#EF6C00", marker="D", s=90, label=asset2["name"])
ax.scatter(std_tang*100, ret_tang*100, color="red", marker="*", s=220, label="Tangency portfolio")
ax.scatter(std_opt*100, ret_opt*100, color="blue", marker="*", s=260, label="Optimal ESG portfolio")
ax.set_xlabel("Risk — standard deviation (%)")
ax.set_ylabel("Expected return (%)")
ax.set_title("ESG-efficient frontier")
ax.grid(True, alpha=0.3)
ax.legend(fontsize=8, loc="lower right")
st.pyplot(fig)

with st.expander("How QGreen works"):
    st.markdown(f"""
QGreen first converts your quiz answers into a **risk-aversion coefficient (γ = {gamma})** and combines that with your **ESG preference strength (λ = {lambda_esg:.2f})**.

It then evaluates many possible weight combinations between the two assets and chooses the portfolio that maximises:

> **U = E[Rₚ] − 0.5 · γ · σ²ₚ + λ · ESGₚ / 100**

That means your final recommendation balances:
- expected return,
- risk,
- and your preference for a greener portfolio.

For **mode B**, you only need to choose the two companies. QGreen automatically uses the company ESG data and tries to pull return and risk from recent market data. If live market data is unavailable, it uses built-in estimates so the app can still give you a recommendation.
    """)

st.markdown("""
<div class="disclaimer">
This tool is for educational purposes and should not be treated as personal financial advice.
</div>
""", unsafe_allow_html=True)
