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
    /* Force light background and dark text everywhere */
    .stApp { background-color: #f7faf7 !important; color: #1a1a1a !important; }

    /* All text elements */
    p, span, label, div, li, td, th, h1, h2, h3, h4, h5, h6,
    .stMarkdown, .stMarkdown p, .stMarkdown li { color: #1a1a1a !important; }

    /* Input boxes — white background, dark text */
    input, textarea, select,
    input[type="number"], input[type="text"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #a5d6a7 !important;
        border-radius: 6px !important;
    }

    /* Selectbox and number input wrappers */
    div[data-baseweb="input"] { background-color: #ffffff !important; }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #1a1a1a !important; }
    div[data-baseweb="select"] * { color: #1a1a1a !important; }

    /* Radio buttons */
    .stRadio label, .stRadio div { color: #1a1a1a !important; }

    /* Slider labels */
    .stSlider label, .stSlider p { color: #1a1a1a !important; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f1f8f1 !important;
    }
    section[data-testid="stSidebar"] * { color: #1a1a1a !important; }
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }

    /* Header banner */
    .qgreen-header {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%);
        color: white !important;
        padding: 2.2rem 2rem 1.8rem 2rem;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(27,94,32,0.25);
    }
    .qgreen-header h1 { font-size: 3rem; margin: 0; letter-spacing: 2px; color: white !important; }
    .qgreen-header p  { font-size: 1.05rem; margin: 0.4rem 0 0 0; opacity: 0.9; color: white !important; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: white !important;
        border: 1px solid #c8e6c9 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    }
    div[data-testid="metric-container"] * { color: #1a1a1a !important; }
    div[data-testid="metric-container"] label { color: #2E7D32 !important; font-weight: 600 !important; }

    /* Dataframe */
    .stDataFrame, .stDataFrame * { color: #1a1a1a !important; background-color: white !important; }

    /* Tabs */
    button[data-baseweb="tab"] { color: #2E7D32 !important; font-weight: 600 !important; font-size: 1rem !important; }

    /* Info/success boxes */
    .stAlert { border-radius: 8px !important; }

    /* Recommendation box */
    .rec-box {
        background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
        border-left: 5px solid #2E7D32;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-top: 1rem;
        color: #1a1a1a !important;
    }
    .rec-box * { color: #1a1a1a !important; }

    /* Disclaimer */
    .disclaimer {
        background: #fff8e1;
        border-left: 4px solid #f9a825;
        border-radius: 6px;
        padding: 0.7rem 1rem;
        font-size: 0.85rem;
        color: #555 !important;
        margin-top: 1.5rem;
    }

    /* Dropdown option list */
    ul[role="listbox"] li { color: #1a1a1a !important; background: white !important; }
    ul[role="listbox"] { background: white !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOAD ESG DATA
# ============================================================
@st.cache_data
def load_esg_data():
    try:
        df = pd.read_csv("esg_scores.csv")
        df = df.dropna(subset=["comname", "esg_0_100"])
        df["comname"] = df["comname"].str.strip()
        df = df.sort_values("comname")
        return df
    except Exception:
        return pd.DataFrame(columns=["comname", "ticker", "esg_0_100"])

esg_df = load_esg_data()
company_list = esg_df["comname"].tolist()
has_data = len(company_list) > 0

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="qgreen-header">
    <h1>🌿 QGreen</h1>
    <p>Your Personalised Sustainable Investment Portfolio Advisor</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Build Your Portfolio")

    # ── STEP 1: RISK QUIZ ──────────────────────────────────
    st.markdown("### 📊 Step 1 — Risk Profile")
    st.caption("Answer 3 questions to find your risk tolerance (γ).")

    q1 = st.radio("Your portfolio drops 20%. You:",
        ["😨 Sell everything", "😐 Hold and wait", "😎 Buy more"], index=1)
    q2 = st.radio("Investment time horizon:",
        ["⏱️ Under 2 years", "📅 2–10 years", "🏆 Over 10 years"], index=1)
    q3 = st.radio("Your investment goal:",
        ["🛡️ Protect capital", "⚖️ Balance growth & safety", "🚀 Maximise growth"], index=1)

    score_map = {
        "😨 Sell everything":1,"😐 Hold and wait":2,"😎 Buy more":3,
        "⏱️ Under 2 years":1,"📅 2–10 years":2,"🏆 Over 10 years":3,
        "🛡️ Protect capital":1,"⚖️ Balance growth & safety":2,"🚀 Maximise growth":3
    }
    quiz_score = score_map[q1] + score_map[q2] + score_map[q3]

    if quiz_score <= 4:
        gamma = 8;  risk_label = "Conservative 🛡️"
    elif quiz_score <= 6:
        gamma = 4;  risk_label = "Balanced ⚖️"
    else:
        gamma = 2;  risk_label = "Growth-Oriented 🚀"

    st.success(f"**{risk_label}** — γ = {gamma}")
    st.markdown("---")

    # ── STEP 2: ESG STRATEGY ───────────────────────────────
    st.markdown("### 🌱 Step 2 — ESG Strategy")

    esg_model = st.selectbox("ESG Approach:", [
        "🚫 Model 1.0 — Exclusion Screening",
        "🏅 Model 2.0 — Best-in-Class",
        "🌍 Model 3.0 — Full ESG Integration"
    ])

    lamda = st.slider("ESG weight (λ)", 0.0, 1.0, 0.5, 0.05,
        help="0 = pure financial optimisation | 1 = ESG equally important")

    esg_threshold = 0
    if esg_model.startswith("🚫"):
        esg_threshold = st.slider("Minimum ESG score:", 0, 100, 50)

    st.markdown("---")

    # ── STEP 3: ASSET SELECTION ────────────────────────────
    st.markdown("### 📈 Step 3 — Select Your Assets")

    if has_data:
        st.caption("📂 Pick from 549 real companies — ESG score auto-fills from 2025 data.")
    else:
        st.caption("Enter asset details manually below.")

    # ── ASSET 1 ──
    st.markdown("**Asset 1**")
    if has_data:
        sel1 = st.selectbox("Company", ["-- Enter manually --"] + company_list, key="sel1")
        if sel1 != "-- Enter manually --":
            row1 = esg_df[esg_df["comname"] == sel1].iloc[0]
            default_esg1 = float(row1["esg_0_100"])
            asset1_name  = sel1.split(",")[0].strip().title()
            ticker1      = str(row1["ticker"])
        else:
            asset1_name  = st.text_input("Name", "Asset 1", key="n1")
            default_esg1 = 70.0
            ticker1      = ""
    else:
        sel1 = "-- Enter manually --"
        asset1_name  = st.text_input("Name", "Asset 1", key="n1")
        default_esg1 = 70.0
        ticker1      = ""

    r1   = st.number_input("Return (%)",  min_value=0.0, max_value=100.0, value=10.0, step=0.5, key="r1") / 100
    sd1  = st.number_input("Std Dev (%)", min_value=0.1, max_value=100.0, value=18.0, step=0.5, key="s1") / 100
    esg1 = st.number_input("ESG Score (0–100)",
                            min_value=0.0, max_value=100.0,
                            value=default_esg1, step=0.1, key="e1",
                            help="Auto-filled from real data. You can override this.")

    st.markdown("**Asset 2**")
    if has_data:
        sel2 = st.selectbox("Company", ["-- Enter manually --"] + company_list, key="sel2",
                            index=company_list.index("UNILEVER PLC") + 1
                            if "UNILEVER PLC" in company_list else 0)
        if sel2 != "-- Enter manually --":
            row2 = esg_df[esg_df["comname"] == sel2].iloc[0]
            default_esg2 = float(row2["esg_0_100"])
            asset2_name  = sel2.split(",")[0].strip().title()
            ticker2      = str(row2["ticker"])
        else:
            asset2_name  = st.text_input("Name", "Asset 2", key="n2")
            default_esg2 = 85.0
            ticker2      = ""
    else:
        sel2 = "-- Enter manually --"
        asset2_name  = st.text_input("Name", "Asset 2", key="n2")
        default_esg2 = 85.0
        ticker2      = ""

    r2   = st.number_input("Return (%)",  min_value=0.0, max_value=100.0, value=6.0,  step=0.5, key="r2") / 100
    sd2  = st.number_input("Std Dev (%)", min_value=0.1, max_value=100.0, value=12.0, step=0.5, key="s2") / 100
    esg2 = st.number_input("ESG Score (0–100)",
                            min_value=0.0, max_value=100.0,
                            value=default_esg2, step=0.1, key="e2",
                            help="Auto-filled from real data. You can override this.")

    st.markdown("---")
    corr = st.slider("Correlation (ρ)", -1.0, 1.0, 0.3, 0.05)
    rf   = st.number_input("Risk-free rate (%)", min_value=0.0, max_value=20.0, value=4.0, step=0.1) / 100

    st.markdown("---")
    run = st.button("🚀 Generate My Portfolio", type="primary", use_container_width=True)

# ============================================================
# WELCOME SCREEN
# ============================================================
if not run:
    wc1, wc2, wc3 = st.columns(3)
    wc1.markdown("""
    #### 📊 Step 1 — Risk Quiz
    Answer 3 quick questions. QGreen automatically
    calculates your risk aversion coefficient (γ).
    """)
    wc2.markdown("""
    #### 🌱 Step 2 — ESG Strategy
    Choose from three sustainable investing models:
    exclusion, best-in-class, or full integration.
    """)
    wc3.markdown("""
    #### 📈 Step 3 — Your Assets
    Pick from **549 real companies** with live ESG scores,
    or enter your own custom asset details.
    """)

    st.markdown("---")
    st.markdown("""
| ESG Model | Description |
|-----------|-------------|
| 🚫 **Model 1.0 — Exclusion** | Screens out assets below your ESG threshold (e.g. sin stocks, fossil fuels) |
| 🏅 **Model 2.0 — Best-in-Class** | Rewards the top ESG performer with a scoring bonus |
| 🌍 **Model 3.0 — Full Integration** | ESG fully embedded into the utility function: **U = μ − ½γσ² + λ·ESG** |

---
*ECN316 Sustainable Finance · Queen Mary University of London*
    """)
    st.stop()

# ============================================================
# CALCULATIONS
# ============================================================

# Model 1.0: exclusion
excluded = []
if esg_model.startswith("🚫"):
    if esg1 < esg_threshold: excluded.append(asset1_name)
    if esg2 < esg_threshold: excluded.append(asset2_name)

if len(excluded) == 2:
    st.error(f"⚠️ Both assets are below your ESG threshold of {esg_threshold}. Lower the threshold or pick different companies.")
    st.stop()

# Model 2.0: best-in-class bonus
esg1_eff, esg2_eff = esg1, esg2
if esg_model.startswith("🏅"):
    if esg1 >= esg2: esg1_eff = min(esg1 * 1.15, 100)
    else:            esg2_eff = min(esg2 * 1.15, 100)

# Portfolio functions
def port_return(w): return w * r1 + (1 - w) * r2
def port_std(w):
    v = w**2*sd1**2 + (1-w)**2*sd2**2 + 2*corr*w*(1-w)*sd1*sd2
    return np.sqrt(max(v, 1e-10))
def port_esg(w):    return w * esg1_eff + (1 - w) * esg2_eff
def utility(w):
    # Lecture 6: U = μ − ½·γ·σ² + λ·(ESG/100)
    # λ=0 → pure mean-variance; λ>0 → ESG-integrated optimisation
    return port_return(w) - 0.5*gamma*port_std(w)**2 + lamda*(port_esg(w)/100)

# Weights array
if asset1_name in excluded:   weights = np.array([0.0])
elif asset2_name in excluded: weights = np.array([1.0])
else:                          weights = np.linspace(0, 1, 1000)

all_ret   = np.array([port_return(w) for w in weights])
all_std   = np.array([port_std(w)    for w in weights])
all_esg   = np.array([port_esg(w)    for w in weights])
all_util  = np.array([utility(w)     for w in weights])
all_sharpe = np.where(all_std > 0, (all_ret - rf) / all_std, -np.inf)

# Tangency portfolio
tang_idx  = int(np.argmax(all_sharpe))
ret_tang  = float(all_ret[tang_idx])
std_tang  = float(all_std[tang_idx])

# Optimal ESG portfolio
best_idx  = int(np.argmax(all_util))
w1_opt    = float(weights[best_idx])
w2_opt    = 1 - w1_opt
ret_opt   = float(all_ret[best_idx])
std_opt   = float(all_std[best_idx])
esg_opt   = float(all_esg[best_idx])
sharpe_opt = (ret_opt - rf) / std_opt if std_opt > 0 else 0.0

# ============================================================
# OUTPUT
# ============================================================
st.markdown(f"## 🎯 Your QGreen Recommendation")
st.caption(f"ESG Strategy: **{esg_model.split('—')[1].strip()}** · Risk Profile: **{risk_label}** · γ={gamma} · λ={lamda}")

tab_results, tab_charts, tab_explain = st.tabs(["📊 Results", "📈 Charts", "💡 How It Works"])

# ──────────────────────────────────────────────────────────
# TAB 1: RESULTS
# ──────────────────────────────────────────────────────────
with tab_results:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📈 Expected Return", f"{ret_opt*100:.2f}%")
    k2.metric("📉 Risk (Std Dev)",   f"{std_opt*100:.2f}%")
    k3.metric("🌿 ESG Score",        f"{esg_opt:.1f} / 100")
    k4.metric("⚡ Sharpe Ratio",     f"{sharpe_opt:.2f}")

    st.markdown("---")
    st.markdown("#### Portfolio Weights")

    df_out = pd.DataFrame({
        "Asset":          [asset1_name,           asset2_name],
        "Ticker":         [ticker1,                ticker2],
        "Weight":         [f"{w1_opt*100:.1f}%",  f"{w2_opt*100:.1f}%"],
        "Return (est.)":  [f"{r1*100:.1f}%",       f"{r2*100:.1f}%"],
        "Risk (Std Dev)": [f"{sd1*100:.1f}%",      f"{sd2*100:.1f}%"],
        "ESG Score":      [f"{esg1:.1f} / 100",    f"{esg2:.1f} / 100"],
    })
    st.dataframe(df_out, use_container_width=True, hide_index=True)

    # Recommendation text
    if esg_opt >= 80:   esg_qual = "excellent 🌟"
    elif esg_opt >= 65: esg_qual = "good 👍"
    else:               esg_qual = "moderate ⚠️"

    if asset1_name in excluded:
        alloc_reason = f"**{asset1_name}** was excluded — ESG score ({esg1:.0f}) below your threshold ({esg_threshold})."
    elif asset2_name in excluded:
        alloc_reason = f"**{asset2_name}** was excluded — ESG score ({esg2:.0f}) below your threshold ({esg_threshold})."
    elif w1_opt >= w2_opt:
        alloc_reason = f"**{asset1_name}** receives the larger share — its return ({r1*100:.1f}%) and ESG score ({esg1:.0f}/100) best match your {risk_label} profile."
    else:
        alloc_reason = f"**{asset2_name}** receives the larger share — its ESG score ({esg2:.0f}/100) and lower risk ({sd2*100:.1f}%) suit your {risk_label} profile."

    esg_note = ("λ = 0: pure financial optimisation — no ESG weighting applied."
                if lamda == 0 else
                f"ESG preference λ={lamda} rewarded portfolios with stronger sustainability scores.")

    st.markdown(f"""
<div class="rec-box">
<h4>💬 QGreen Recommends:</h4>
<p>➡ <strong>{w1_opt*100:.0f}% in {asset1_name}</strong> &nbsp;|&nbsp;
   <strong>{w2_opt*100:.0f}% in {asset2_name}</strong></p>
<ul>
  <li>Expected annual return: <strong>{ret_opt*100:.2f}%</strong></li>
  <li>Risk (standard deviation): <strong>{std_opt*100:.2f}%</strong></li>
  <li>ESG score: <strong>{esg_opt:.0f}/100</strong> — {esg_qual}</li>
  <li>Sharpe ratio: <strong>{sharpe_opt:.2f}</strong></li>
</ul>
<p>{alloc_reason}<br>{esg_note}</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="disclaimer">
⚠️ <strong>Disclaimer:</strong> QGreen is for educational purposes only.
ESG scores are sourced from real 2025 data. Return and risk estimates are user-provided.
Always consult a qualified financial advisor before investing.
</div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# TAB 2: CHARTS
# ──────────────────────────────────────────────────────────
with tab_charts:
    g1, g2 = st.columns(2)

    with g1:
        st.markdown("#### ESG-Efficient Frontier")
        fig1, ax1 = plt.subplots(figsize=(6.5, 5))
        fig1.patch.set_facecolor("#f7faf7")
        ax1.set_facecolor("#f7faf7")

        sc = ax1.scatter(all_std*100, all_ret*100, c=all_esg,
                         cmap="RdYlGn", s=14, alpha=0.85, zorder=2, vmin=0, vmax=100)
        cbar = plt.colorbar(sc, ax=ax1)
        cbar.set_label("ESG Score", fontsize=9)

        # CML
        if std_tang > 0:
            cml_x = np.linspace(0, max(all_std)*100*1.3, 200)
            cml_y = rf*100 + (ret_tang - rf)/std_tang * cml_x/100 * 100
            ax1.plot(cml_x, cml_y, "g--", lw=1.6, label="Capital Market Line", zorder=3)

        ax1.scatter(0, rf*100, color="green", marker="s", s=90, zorder=5, label=f"Risk-Free ({rf*100:.1f}%)")
        ax1.scatter(std_tang*100, ret_tang*100, color="red", marker="*", s=260, zorder=6, label="Tangency Portfolio")
        ax1.scatter(sd1*100, r1*100, color="purple", marker="D", s=100, zorder=5, label=asset1_name)
        ax1.scatter(sd2*100, r2*100, color="orange",  marker="D", s=100, zorder=5, label=asset2_name)
        ax1.scatter(std_opt*100, ret_opt*100, color="blue", marker="*", s=320, zorder=7, label="✅ Optimal ESG Portfolio")

        ax1.set_xlabel("Risk — Std Dev (%)", fontsize=10)
        ax1.set_ylabel("Expected Annual Return (%)", fontsize=10)
        ax1.set_title("ESG-Efficient Frontier & CML", fontweight="bold")
        ax1.legend(fontsize=7.5, loc="lower right")
        ax1.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig1)

    with g2:
        st.markdown("#### Recommended Allocation")
        fig2, ax2 = plt.subplots(figsize=(6.5, 5))
        fig2.patch.set_facecolor("#f7faf7")

        wedges, texts, autotexts = ax2.pie(
            [max(w1_opt, 0.0001), max(w2_opt, 0.0001)],
            labels=[asset1_name, asset2_name],
            autopct="%1.1f%%", colors=["#1565C0","#2E7D32"],
            startangle=90, wedgeprops={"edgecolor":"white","linewidth":2.5}
        )
        for at in autotexts:
            at.set_fontsize(13); at.set_fontweight("bold"); at.set_color("white")
        ax2.text(0, -1.38,
                 f"Return {ret_opt*100:.2f}%  ·  Risk {std_opt*100:.2f}%  ·  ESG {esg_opt:.0f}/100",
                 ha="center", fontsize=9,
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="#c8e6c9", alpha=0.9))
        ax2.set_title("Portfolio Allocation", fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig2)

    # ESG comparison bar
    st.markdown("#### ESG Score Comparison")
    fig3, ax3 = plt.subplots(figsize=(9, 3))
    fig3.patch.set_facecolor("#f7faf7")
    ax3.set_facecolor("#f7faf7")

    bars = ax3.barh([asset1_name, asset2_name, "Your Portfolio"],
                    [esg1, esg2, esg_opt],
                    color=["#1565C0","#2E7D32","#FF6F00"], edgecolor="white", height=0.5)
    for bar, val in zip(bars, [esg1, esg2, esg_opt]):
        ax3.text(val+0.8, bar.get_y()+bar.get_height()/2,
                 f"{val:.1f}", va="center", fontweight="bold", fontsize=11, color="#1a1a1a")

    ax3.set_xlim(0, 115)
    ax3.axvline(50, color="red",    linestyle="--", alpha=0.5, label="Poor (< 50)")
    ax3.axvline(70, color="orange", linestyle="--", alpha=0.5, label="Good (≥ 70)")
    ax3.axvline(85, color="green",  linestyle="--", alpha=0.5, label="Excellent (≥ 85)")
    ax3.set_xlabel("ESG Score (0–100)", fontsize=10, color="#1a1a1a")
    ax3.set_title("ESG Score Breakdown", fontweight="bold", color="#1a1a1a")
    ax3.tick_params(colors="#1a1a1a")
    ax3.legend(fontsize=8, loc="lower right")
    ax3.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    st.pyplot(fig3)

# ──────────────────────────────────────────────────────────
# TAB 3: HOW IT WORKS
# ──────────────────────────────────────────────────────────
with tab_explain:
    st.markdown("### 📚 How QGreen Works")
    st.markdown(f"""
**The Utility Function (Lecture 6)**

QGreen tests 1,000 possible portfolio combinations and selects the one that
maximises this ESG-adjusted utility function:

> **U = μₚ − ½ · γ · σ²ₚ + λ · (ESGₚ / 100)**

| Symbol | Meaning | Your Value |
|--------|---------|------------|
| μₚ | Portfolio expected return | {ret_opt*100:.2f}% |
| σ²ₚ | Portfolio variance | {std_opt**2:.6f} |
| γ | Risk aversion coefficient | {gamma} (from your quiz) |
| λ | ESG preference weight | {lamda} |
| ESGₚ | Portfolio ESG score | {esg_opt:.1f} / 100 |

When λ = 0, the formula reduces to **pure mean-variance optimisation** (no ESG).
As λ increases, portfolios with higher ESG scores are increasingly rewarded.

**ESG Data Source**

ESG scores are sourced from a real 2025 dataset covering **549 publicly listed companies**.
Scores reflect Environmental, Social and Governance performance and range from 0–100.
    """)

    if esg_model.startswith("🚫"):
        st.info(f"**Model 1.0 — Exclusion Screening:** Assets with ESG below **{esg_threshold}** are removed before optimisation. This mirrors how ESG funds exclude sin stocks (tobacco, weapons, fossil fuels).")
    elif esg_model.startswith("🏅"):
        st.info("**Model 2.0 — Best-in-Class:** The stronger ESG performer receives a 15% bonus, incentivising relative ESG leadership without excluding whole industries.")
    else:
        st.info(f"**Model 3.0 — Full Integration:** ESG is embedded directly into the utility function via λ = {lamda}. The optimiser naturally favours higher-ESG assets when it improves overall utility.")

    st.markdown(f"""
**Your Results**
- Optimal: **{w1_opt*100:.1f}% {asset1_name}** / **{w2_opt*100:.1f}% {asset2_name}**
- Expected Return: **{ret_opt*100:.2f}%** | Risk: **{std_opt*100:.2f}%** | ESG: **{esg_opt:.1f}/100** | Sharpe: **{sharpe_opt:.2f}**
    """)

    st.markdown("""
<div class="disclaimer">
⚠️ For educational purposes only (ECN316, QMUL). Not financial advice.
</div>""", unsafe_allow_html=True)
