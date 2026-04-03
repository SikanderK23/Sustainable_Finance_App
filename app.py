import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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

    /* Dropdown menu / popover fixes */
    div[data-baseweb="popover"],
    div[role="listbox"],
    ul[role="listbox"],
    li[role="option"] {
        background: #ffffff !important;
        color: #1a1a1a !important;
    }
    div[data-baseweb="popover"] * ,
    div[role="listbox"] * ,
    ul[role="listbox"] * ,
    li[role="option"] * {
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
    button[data-baseweb="tab"] { color: #2E7D32 !important; font-weight: 600 !important; font-size: 1rem !important; }

    .rec-box {
        background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
        border-left: 5px solid #2E7D32;
        border-radius: 8px;
        padding: 1.1rem 1.35rem;
        margin-top: 1rem;
        color: #1a1a1a !important;
    }
    .rec-box * { color: #1a1a1a !important; }

    .mode-card {
        background: white;
        border: 1px solid #d9eadb;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        min-height: 170px;
        box-shadow: 0 1px 8px rgba(0,0,0,0.04);
    }
    .mode-card h4 { margin-top: 0; color: #1B5E20 !important; }

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
    """Demo assumptions for options A/B when only ESG data is available.
    Keeps app aligned with project brief while remaining transparent.
    """
    e = float(esg_score)
    if style == "Conservative 🛡️":
        ret = 0.05 + 0.00025 * e        # 5.0% to 7.5%
        sd = 0.10 + 0.00020 * (100 - e) # lower ESG -> slightly higher risk
    elif style == "Balanced ⚖️":
        ret = 0.07 + 0.00022 * e        # 7.0% to 9.2%
        sd = 0.14 + 0.00022 * (100 - e)
    else:
        ret = 0.09 + 0.00018 * e        # 9.0% to 10.8%
        sd = 0.18 + 0.00025 * (100 - e)
    return round(ret, 4), round(sd, 4)


def pick_auto_pair(df: pd.DataFrame, style: str, lambda_esg: float, esg_mode: str, esg_threshold: float):
    work = df.copy()
    if esg_mode.startswith("🚫"):
        work = work[work["esg_0_100"] >= esg_threshold]
    if len(work) < 2:
        return None, None

    # Target ESG depends on preference intensity.
    target = 45 + 45 * lambda_esg
    if style == "Conservative 🛡️":
        target += 5
    elif style == "Growth-Oriented 🚀":
        target -= 5
    target = max(20, min(95, target))

    work = work.assign(dist=(work["esg_0_100"] - target).abs())

    # Choose one anchor near target, then one complementary stock from opposite side.
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


def build_asset_dict(name, ticker, ret, sd, esg):
    return {
        "name": str(name),
        "ticker": str(ticker),
        "ret": float(ret),
        "sd": float(sd),
        "esg": float(esg),
    }


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
    w1 = float(weights[best_idx])
    w2 = 1.0 - w1

    return {
        "asset1": asset1,
        "asset2": asset2,
        "weights": weights,
        "all_ret": all_ret,
        "all_std": all_std,
        "all_esg": all_esg,
        "w1": w1,
        "w2": w2,
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
    <p>Build a personalised two-asset sustainable portfolio in three different ways</p>
</div>
""", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
m1.markdown("""<div class='mode-card'><h4>A) Auto Portfolio</h4>
QGreen chooses <strong>two companies for you</strong> using your quiz answers and ESG preferences. Best for a fast recommendation.</div>""", unsafe_allow_html=True)
m2.markdown("""<div class='mode-card'><h4>B) Choose 2 Companies</h4>
You pick <strong>two real companies</strong> from the built-in ESG dataset. QGreen auto-fills ESG scores and demo return/risk assumptions.</div>""", unsafe_allow_html=True)
m3.markdown("""<div class='mode-card'><h4>C) Full Manual</h4>
You enter <strong>everything yourself</strong>: expected return, risk, correlation, risk-free rate, and ESG scores for both assets.</div>""", unsafe_allow_html=True)

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

    st.markdown("---")
    st.caption("For modes A and B, ESG scores come from your built-in company dataset. Expected return and risk use transparent demo assumptions so the app can still optimise a portfolio.")
    run = st.button("🚀 Generate portfolio", type="primary", use_container_width=True)

# ============================================================
# BUILD ASSETS FOR EACH MODE
# ============================================================
asset1 = asset2 = None
mode_explainer = ""

if mode.startswith("A"):
    mode_explainer = "QGreen automatically selected two companies using your risk quiz result and ESG preferences."
    if len(esg_df) >= 2:
        a1, a2 = pick_auto_pair(esg_df, risk_label, lambda_esg, esg_mode, esg_threshold)
        if a1 is not None and a2 is not None:
            r1, sd1 = estimate_asset_characteristics(a1["esg_0_100"], risk_label)
            r2, sd2 = estimate_asset_characteristics(a2["esg_0_100"], risk_label)
            asset1 = build_asset_dict(a1["comname"].title(), a1["ticker"], r1, sd1, a1["esg_0_100"])
            asset2 = build_asset_dict(a2["comname"].title(), a2["ticker"], r2, sd2, a2["esg_0_100"])

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
    r1, sd1 = estimate_asset_characteristics(row1["esg_0_100"], risk_label)
    r2, sd2 = estimate_asset_characteristics(row2["esg_0_100"], risk_label)

    st.info("QGreen auto-filled expected return and risk using the app's demo assumptions. You can edit them below if you want more control.")
    e1, e2 = st.columns(2)
    with e1:
        r1 = st.number_input("Company 1 expected return (%)", 0.0, 100.0, float(r1 * 100), 0.1, key="b_r1") / 100
        sd1 = st.number_input("Company 1 risk / SD (%)", 0.1, 100.0, float(sd1 * 100), 0.1, key="b_sd1") / 100
    with e2:
        r2 = st.number_input("Company 2 expected return (%)", 0.0, 100.0, float(r2 * 100), 0.1, key="b_r2") / 100
        sd2 = st.number_input("Company 2 risk / SD (%)", 0.1, 100.0, float(sd2 * 100), 0.1, key="b_sd2") / 100

    asset1 = build_asset_dict(row1["comname"].title(), row1["ticker"], r1, sd1, row1["esg_0_100"])
    asset2 = build_asset_dict(row2["comname"].title(), row2["ticker"], r2, sd2, row2["esg_0_100"])
    mode_explainer = "You chose two real companies from the dataset. ESG scores were auto-filled and return/risk assumptions can be adjusted."

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
    asset1 = build_asset_dict(n1, t1, r1, sd1, esg1)
    asset2 = build_asset_dict(n2, t2, r2, sd2, esg2)
    mode_explainer = "You entered all portfolio inputs manually, exactly matching the base-case requirement from the brief."

# ============================================================
# WELCOME SCREEN
# ============================================================
if not run:
    st.markdown("### How to use QGreen")
    st.markdown(f"**Selected mode:** {mode}")
    st.markdown(mode_explainer if mode_explainer else "Choose a mode, set your preferences, then click Generate portfolio.")

    st.markdown("""
- **A) Auto Portfolio**: best if the user wants the app to do most of the work.
- **B) Choose 2 Companies**: best if the user already knows which firms they want to compare.
- **C) Full Manual**: best if the user wants complete control over return, risk, correlation, risk-free rate, and ESG inputs.
    """)

    st.markdown("""
| ESG model | What it does |
|---|---|
| 🚫 Exclusion screening | removes assets below your minimum ESG threshold |
| 🏅 Best-in-class tilt | rewards the stronger ESG asset with a small ESG bonus |
| 🌍 Full ESG integration | uses the lecture 6 utility function directly: \(U = E[R_p] - \frac{\gamma}{2}\sigma_p^2 + \lambda \bar{s}\) |
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
st.info(mode_explainer)

tab1, tab2, tab3 = st.tabs(["📊 Results", "📈 Charts", "💡 How it works"])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Expected return", f"{ret_opt*100:.2f}%")
    c2.metric("Risk (SD)", f"{std_opt*100:.2f}%")
    c3.metric("Portfolio ESG", f"{esg_opt:.1f} / 100")
    c4.metric("Sharpe ratio", f"{sharpe_opt:.2f}")

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
        allocation_reason = f"{asset1['name']} receives the larger weight because it contributes more to your overall utility after balancing return, risk, and ESG."
    elif w2 > w1:
        allocation_reason = f"{asset2['name']} receives the larger weight because it contributes more to your overall utility after balancing return, risk, and ESG."
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

with tab2:
    left, right = st.columns(2)
    with left:
        fig, ax = plt.subplots(figsize=(6.3, 5))
        fig.patch.set_facecolor("#f7faf7")
        ax.set_facecolor("#f7faf7")
        sc = ax.scatter(result["all_std"]*100, result["all_ret"]*100, c=result["all_esg"], cmap="RdYlGn", s=14, alpha=0.85, vmin=0, vmax=100)
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
        ax.legend(fontsize=7.5, loc="lower right")
        st.pyplot(fig)

    with right:
        fig2, ax2 = plt.subplots(figsize=(6.3, 5))
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

    fig3, ax3 = plt.subplots(figsize=(8.5, 3))
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

with tab3:
    st.markdown("### How the app works")
    st.markdown(f"""
- **Risk quiz** maps your answers into a risk-aversion coefficient **γ = {gamma}**.
- **ESG preference slider** sets **λ = {lambda_esg:.2f}**, which controls how much extra utility you get from a greener portfolio.
- QGreen then evaluates 1,000 weight combinations between the two assets and selects the portfolio that maximises:

> **U = E[R_p] - 0.5·γ·σ²_p + λ·(ESG_p / 100)**

This follows the Week 6 portfolio-management framework, where ESG is treated as an additional source of utility in portfolio choice fileciteturn7file3L4-L6.
    """)

    st.markdown("### What each mode means")
    st.markdown("""
- **Mode A** is the most user-friendly: QGreen chooses the two companies for the user.
- **Mode B** is more specific: the user picks two real companies and QGreen handles the rest.
- **Mode C** is the base-case assignment requirement: the user manually enters both assets' return, standard deviation, correlation, risk-free rate, and ESG score.
    """)

    st.markdown("### Notes for your poster / demo")
    st.markdown("""
- The group brief requires the app to ask for risk preferences, ESG preferences, and two-asset characteristics, then construct the ESG-efficient frontier and determine the optimal portfolio fileciteturn8file1L9-L18.
- Modes A and B are extra design features that make your app more interactive and more suitable for retail users.
- In the current dataset, only ESG scores are provided directly, so QGreen uses transparent demo assumptions for expected return and volatility in modes A and B. Mode C gives full manual control.
    """)

    st.markdown("""
<div class="disclaimer">
This app is for educational use only. It demonstrates the Week 6 lecture logic and the group-project brief, not real investment advice.
</div>
""", unsafe_allow_html=True)
