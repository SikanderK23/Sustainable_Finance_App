import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
# CUSTOM CSS — premium green brand
# ============================================================
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #f7faf7; }

    /* Header banner */
    .qgreen-header {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%);
        color: white;
        padding: 2.2rem 2rem 1.8rem 2rem;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(27,94,32,0.25);
    }
    .qgreen-header h1 { font-size: 3rem; margin: 0; letter-spacing: 2px; }
    .qgreen-header p  { font-size: 1.05rem; margin: 0.4rem 0 0 0; opacity: 0.88; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid #c8e6c9;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    div[data-testid="metric-container"] label { color: #2E7D32 !important; font-weight: 600; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #f1f8f1; }
    section[data-testid="stSidebar"] h2 { color: #1B5E20; }
    section[data-testid="stSidebar"] h3 { color: #2E7D32; border-bottom: 2px solid #a5d6a7; padding-bottom: 4px; }

    /* Tab styling */
    button[data-baseweb="tab"] { font-size: 1rem; font-weight: 600; color: #2E7D32; }
    button[data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #2E7D32 !important; }

    /* Info box */
    .recommendation-box {
        background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
        border-left: 5px solid #2E7D32;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-top: 1rem;
    }

    /* Disclaimer */
    .disclaimer {
        background: #fff8e1;
        border-left: 4px solid #f9a825;
        border-radius: 6px;
        padding: 0.7rem 1rem;
        font-size: 0.85rem;
        color: #555;
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

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
# SIDEBAR — ALL INPUTS
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Build Your Portfolio")

    # ── STEP 1: RISK QUIZ ──────────────────────────────────
    st.markdown("### 📊 Step 1 — Risk Profile")
    st.caption("Answer 3 questions to find your risk tolerance (γ).")

    q1 = st.radio(
        "Your portfolio drops 20%. You:",
        ["😨 Sell everything", "😐 Hold and wait", "😎 Buy more"],
        index=1, key="q1"
    )
    q2 = st.radio(
        "Investment time horizon:",
        ["⏱️ Under 2 years", "📅 2–10 years", "🏆 Over 10 years"],
        index=1, key="q2"
    )
    q3 = st.radio(
        "Your investment goal:",
        ["🛡️ Protect capital", "⚖️ Balance growth & safety", "🚀 Maximise growth"],
        index=1, key="q3"
    )

    q_scores = {
        "😨 Sell everything": 1, "😐 Hold and wait": 2, "😎 Buy more": 3,
        "⏱️ Under 2 years": 1, "📅 2–10 years": 2, "🏆 Over 10 years": 3,
        "🛡️ Protect capital": 1, "⚖️ Balance growth & safety": 2, "🚀 Maximise growth": 3
    }
    quiz_score = q_scores[q1] + q_scores[q2] + q_scores[q3]

    if quiz_score <= 4:
        gamma = 8;  risk_label = "Conservative 🛡️"
    elif quiz_score <= 6:
        gamma = 4;  risk_label = "Balanced ⚖️"
    else:
        gamma = 2;  risk_label = "Growth-Oriented 🚀"

    st.success(f"**{risk_label}** — γ = {gamma}")
    st.markdown("---")

    # ── STEP 2: ESG PREFERENCES ────────────────────────────
    st.markdown("### 🌱 Step 2 — ESG Preferences")

    esg_model = st.selectbox(
        "ESG Strategy:",
        [
            "🚫 Model 1.0 — Exclusion Screening",
            "🏅 Model 2.0 — Best-in-Class",
            "🌍 Model 3.0 — Full ESG Integration"
        ],
        help=(
            "1.0: Exclude assets below your ESG floor.\n"
            "2.0: Reward the top ESG performer with a bonus.\n"
            "3.0: Fully embed ESG into the utility optimisation."
        )
    )

    lamda = st.slider("ESG weight (λ)", 0.0, 1.0, 0.5, 0.05,
        help="0 = pure financial optimisation | 1 = ESG equally weighted with return")

    esg_threshold = 0
    if esg_model.startswith("🚫"):
        esg_threshold = st.slider("Minimum ESG score allowed:", 0, 100, 50,
            help="Assets scoring below this are screened out entirely.")

    st.markdown("---")

    # ── STEP 3: ASSET INPUTS ───────────────────────────────
    st.markdown("### 📈 Step 3 — Asset Details")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Asset 1**")
        asset1_name = st.text_input("Name", "Apple",    key="n1")
        r1   = st.number_input("Return (%)",   10.0, 0.0, 100.0, 0.5, key="r1") / 100
        sd1  = st.number_input("Std Dev (%)",  18.0, 0.1, 100.0, 0.5, key="s1") / 100
        esg1 = st.number_input("ESG (0–100)",  72.0, 0.0, 100.0, 1.0, key="e1")

    with col_b:
        st.markdown("**Asset 2**")
        asset2_name = st.text_input("Name", "Unilever", key="n2")
        r2   = st.number_input("Return (%)",    6.0, 0.0, 100.0, 0.5, key="r2") / 100
        sd2  = st.number_input("Std Dev (%)",  12.0, 0.1, 100.0, 0.5, key="s2") / 100
        esg2 = st.number_input("ESG (0–100)",  85.0, 0.0, 100.0, 1.0, key="e2")

    corr = st.slider("Correlation (ρ)", -1.0, 1.0, 0.3, 0.05)
    rf   = st.number_input("Risk-free rate (%)", 4.0, 0.0, 20.0, 0.1) / 100

    st.markdown("---")
    run = st.button("🚀 Generate My Portfolio", type="primary", use_container_width=True)

# ============================================================
# WELCOME SCREEN
# ============================================================
if not run:
    wc1, wc2, wc3 = st.columns(3)
    wc1.markdown("""
    #### 📊 Step 1 — Risk Quiz
    Answer 3 questions in the sidebar.
    QGreen automatically calculates your risk aversion (γ).
    """)
    wc2.markdown("""
    #### 🌱 Step 2 — ESG Strategy
    Choose from three ESG models:
    exclusion screening, best-in-class, or full integration.
    """)
    wc3.markdown("""
    #### 📈 Step 3 — Your Assets
    Enter return, risk and ESG data for two assets you're considering.
    """)

    st.markdown("---")
    st.markdown("""
    | ESG Model | Description |
    |-----------|-------------|
    | 🚫 **Model 1.0 — Exclusion** | Screens out assets below your ESG threshold (e.g. sin stocks, fossil fuels) |
    | 🏅 **Model 2.0 — Best-in-Class** | Rewards the top ESG performer within each asset pair |
    | 🌍 **Model 3.0 — Full Integration** | ESG fully embedded into the utility function: U = μ − ½γσ² + λ·ESG |

    ---
    *ECN316 Sustainable Finance · Queen Mary University of London*
    """)
    st.stop()

# ============================================================
# CALCULATIONS
# ============================================================

# --- Model 1.0: ESG exclusion ---
excluded = []
if esg_model.startswith("🚫"):
    if esg1 < esg_threshold: excluded.append(asset1_name)
    if esg2 < esg_threshold: excluded.append(asset2_name)

if len(excluded) == 2:
    st.error(
        f"⚠️ Both assets are below your ESG threshold of {esg_threshold}. "
        "Please lower the threshold or enter different assets."
    )
    st.stop()

# --- Model 2.0: Best-in-class bonus ---
esg1_eff, esg2_eff = esg1, esg2
if esg_model.startswith("🏅"):
    if esg1 >= esg2: esg1_eff = min(esg1 * 1.15, 100)
    else:            esg2_eff = min(esg2 * 1.15, 100)

# --- Core portfolio functions ---
def port_return(w):
    return w * r1 + (1 - w) * r2

def port_std(w):
    v = w**2*sd1**2 + (1-w)**2*sd2**2 + 2*corr*w*(1-w)*sd1*sd2
    return np.sqrt(max(v, 1e-10))

def port_esg(w):
    return w * esg1_eff + (1 - w) * esg2_eff

def utility(w):
    # Lecture 6 utility function: U = μ − ½·γ·σ² + λ·(ESG/100)
    # λ=0 → pure mean-variance; λ>0 → ESG-adjusted optimisation
    return port_return(w) - 0.5*gamma*port_std(w)**2 + lamda*(port_esg(w)/100)

# --- Set weights (handle exclusions) ---
if asset1_name in excluded:
    weights = np.array([0.0])
elif asset2_name in excluded:
    weights = np.array([1.0])
else:
    weights = np.linspace(0, 1, 1000)

all_ret  = np.array([port_return(w) for w in weights])
all_std  = np.array([port_std(w)    for w in weights])
all_esg  = np.array([port_esg(w)    for w in weights])
all_util = np.array([utility(w)     for w in weights])

# --- Sharpe ratios for tangency portfolio ---
all_sharpe = np.where(all_std > 0, (all_ret - rf) / all_std, -np.inf)
tang_idx   = int(np.argmax(all_sharpe))
w1_tang    = float(weights[tang_idx])
ret_tang   = float(all_ret[tang_idx])
std_tang   = float(all_std[tang_idx])

# --- Optimal ESG portfolio (utility maximisation) ---
best_idx = int(np.argmax(all_util))
w1_opt   = float(weights[best_idx])
w2_opt   = 1 - w1_opt
ret_opt  = float(all_ret[best_idx])
std_opt  = float(all_std[best_idx])
esg_opt  = float(all_esg[best_idx])
sharpe_opt = (ret_opt - rf) / std_opt if std_opt > 0 else 0.0

# --- Capital allocation: optimal fraction in risky portfolio ---
# w* = (μ_T − r_f) / (γ · σ²_T)   (from Lecture 6)
w_star = (ret_tang - rf) / (gamma * std_tang**2) if std_tang > 0 else 1.0
w_rf   = 1 - w_star          # weight in risk-free asset

# ============================================================
# OUTPUT TABS
# ============================================================
strategy_label = esg_model.split("—")[1].strip() if "—" in esg_model else esg_model
st.markdown(f"## 🎯 Your QGreen Portfolio")
st.caption(f"Strategy: **{strategy_label}** · Risk profile: **{risk_label}** · γ = {gamma} · λ = {lamda}")

tab_results, tab_graph, tab_explain = st.tabs(["📊 Results", "📈 Charts", "💡 Explanation"])

# ──────────────────────────────────────────────────────────
# TAB 1: RESULTS
# ──────────────────────────────────────────────────────────
with tab_results:
    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📈 Expected Return", f"{ret_opt*100:.2f}%")
    k2.metric("📉 Risk (Std Dev)",   f"{std_opt*100:.2f}%")
    k3.metric("🌿 ESG Score",        f"{esg_opt:.1f} / 100")
    k4.metric("⚡ Sharpe Ratio",     f"{sharpe_opt:.2f}")

    st.markdown("---")
    st.markdown("#### Portfolio Weights")

    # Summary table
    df = pd.DataFrame({
        "Asset":           [asset1_name,           asset2_name],
        "Weight":          [f"{w1_opt*100:.1f}%",  f"{w2_opt*100:.1f}%"],
        "Expected Return": [f"{r1*100:.1f}%",       f"{r2*100:.1f}%"],
        "Risk (Std Dev)":  [f"{sd1*100:.1f}%",      f"{sd2*100:.1f}%"],
        "ESG Score":       [f"{esg1:.0f} / 100",    f"{esg2:.0f} / 100"],
        "ESG Model Eff.":  [f"{esg1_eff:.0f} / 100",f"{esg2_eff:.0f} / 100"],
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Plain English recommendation
    if esg_opt >= 80: esg_qual = "excellent 🌟"
    elif esg_opt >= 65: esg_qual = "good 👍"
    else: esg_qual = "moderate ⚠️"

    bigger_name = asset1_name if w1_opt >= w2_opt else asset2_name

    if asset1_name in excluded:
        alloc_reason = f"**{asset1_name}** was excluded (ESG score {esg1:.0f} < threshold {esg_threshold})."
    elif asset2_name in excluded:
        alloc_reason = f"**{asset2_name}** was excluded (ESG score {esg2:.0f} < threshold {esg_threshold})."
    elif w1_opt >= w2_opt:
        alloc_reason = (f"**{asset1_name}** receives the larger share because its return "
                        f"({r1*100:.1f}%) and ESG score ({esg1:.0f}/100) best fit your {risk_label} profile.")
    else:
        alloc_reason = (f"**{asset2_name}** receives the larger share because its ESG score "
                        f"({esg2:.0f}/100) and lower risk ({sd2*100:.1f}%) suit your {risk_label} profile.")

    esg_note = ("Since λ = 0, this is a **pure financial optimisation** — no ESG weighting applied."
                if lamda == 0 else
                f"Your ESG preference (λ = {lamda}) boosted portfolios with stronger sustainability scores.")

    st.markdown(f"""
<div class="recommendation-box">
<h4>💬 QGreen Recommends:</h4>

➡ <strong>{w1_opt*100:.0f}% in {asset1_name}</strong> &nbsp;|&nbsp; <strong>{w2_opt*100:.0f}% in {asset2_name}</strong>

<ul>
  <li>Expected annual return: <strong>{ret_opt*100:.2f}%</strong></li>
  <li>Risk (standard deviation): <strong>{std_opt*100:.2f}%</strong></li>
  <li>ESG score: <strong>{esg_opt:.0f}/100</strong> — {esg_qual}</li>
  <li>Sharpe ratio: <strong>{sharpe_opt:.2f}</strong></li>
</ul>

{alloc_reason}<br><br>{esg_note}
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="disclaimer">
⚠️ <strong>Disclaimer:</strong> QGreen is for educational purposes only.
Past performance does not guarantee future results.
Always consult a qualified financial advisor before making investment decisions.
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# TAB 2: CHARTS
# ──────────────────────────────────────────────────────────
with tab_graph:
    g1, g2 = st.columns(2)

    # --- LEFT: ESG-Efficient Frontier + CML ---
    with g1:
        st.markdown("#### ESG-Efficient Frontier")
        fig1, ax1 = plt.subplots(figsize=(6.5, 5))

        # Frontier coloured by ESG
        sc = ax1.scatter(
            all_std * 100, all_ret * 100,
            c=all_esg, cmap="RdYlGn",
            s=14, alpha=0.85, zorder=2, vmin=0, vmax=100
        )
        cbar = plt.colorbar(sc, ax=ax1)
        cbar.set_label("ESG Score", fontsize=9)

        # Capital Market Line
        cml_x = np.linspace(0, max(all_std)*100*1.3, 200)
        if std_tang > 0:
            cml_y = rf*100 + (ret_tang - rf) / std_tang * (cml_x / 100) * 100
            ax1.plot(cml_x, cml_y, "g--", linewidth=1.6, label="Capital Market Line", zorder=3)

        # Risk-free rate point
        ax1.scatter(0, rf*100, color="green", marker="s", s=100, zorder=5, label=f"Risk-Free ({rf*100:.1f}%)")

        # Tangency portfolio
        ax1.scatter(std_tang*100, ret_tang*100, color="red", marker="*",
                    s=280, zorder=6, label="Tangency Portfolio")

        # Individual assets
        ax1.scatter(sd1*100, r1*100, color="purple", marker="D", s=100, zorder=5, label=asset1_name)
        ax1.scatter(sd2*100, r2*100, color="orange",  marker="D", s=100, zorder=5, label=asset2_name)

        # Optimal ESG portfolio
        ax1.scatter(std_opt*100, ret_opt*100, color="blue", marker="*",
                    s=350, zorder=7, label="✅ Optimal ESG Portfolio")

        ax1.set_xlabel("Risk — Standard Deviation (%)", fontsize=10)
        ax1.set_ylabel("Expected Annual Return (%)", fontsize=10)
        ax1.set_title("ESG-Efficient Frontier & CML", fontweight="bold")
        ax1.legend(fontsize=7.5, loc="lower right")
        ax1.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig1)

    # --- RIGHT: Allocation Pie ---
    with g2:
        st.markdown("#### Recommended Allocation")
        fig2, ax2 = plt.subplots(figsize=(6.5, 5))

        pie_sizes  = [max(w1_opt, 0.0001), max(w2_opt, 0.0001)]
        pie_labels = [asset1_name, asset2_name]
        pie_colors = ["#1565C0", "#2E7D32"]

        wedges, texts, autotexts = ax2.pie(
            pie_sizes, labels=pie_labels, autopct="%1.1f%%",
            colors=pie_colors, startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 2.5},
            textprops={"fontsize": 11}
        )
        for at in autotexts:
            at.set_fontsize(13); at.set_fontweight("bold"); at.set_color("white")

        stats_txt = f"Return {ret_opt*100:.2f}%  ·  Risk {std_opt*100:.2f}%  ·  ESG {esg_opt:.0f}/100"
        ax2.text(0, -1.38, stats_txt, ha="center", fontsize=9,
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="#c8e6c9", alpha=0.9))
        ax2.set_title("Portfolio Allocation", fontweight="bold", fontsize=12)
        plt.tight_layout()
        st.pyplot(fig2)

    # --- ESG comparison bar chart ---
    st.markdown("#### ESG Score Comparison")
    fig3, ax3 = plt.subplots(figsize=(8, 3))
    bars = ax3.barh(
        [asset1_name, asset2_name, "Your Portfolio"],
        [esg1, esg2, esg_opt],
        color=["#1565C0", "#2E7D32", "#FF6F00"],
        edgecolor="white", height=0.5
    )
    for bar, val in zip(bars, [esg1, esg2, esg_opt]):
        ax3.text(val + 0.5, bar.get_y() + bar.get_height()/2,
                 f"{val:.1f}", va="center", fontweight="bold", fontsize=11)
    ax3.set_xlim(0, 110)
    ax3.axvline(50, color="red",    linestyle="--", alpha=0.5, label="Poor ESG threshold")
    ax3.axvline(75, color="orange", linestyle="--", alpha=0.5, label="Good ESG threshold")
    ax3.axvline(90, color="green",  linestyle="--", alpha=0.5, label="Excellent ESG threshold")
    ax3.set_xlabel("ESG Score (0–100)", fontsize=10)
    ax3.set_title("ESG Score Breakdown", fontweight="bold")
    ax3.legend(fontsize=8, loc="lower right")
    ax3.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    st.pyplot(fig3)

# ──────────────────────────────────────────────────────────
# TAB 3: EXPLANATION
# ──────────────────────────────────────────────────────────
with tab_explain:
    st.markdown("### 📚 How QGreen Works")

    st.markdown(f"""
**The Utility Function (Lecture 6)**

QGreen maximises the following ESG-adjusted utility function for each possible portfolio weight:

> **U = μₚ − ½ · γ · σ²ₚ + λ · (ESGₚ / 100)**

| Symbol | Meaning | Your Value |
|--------|---------|------------|
| μₚ | Portfolio expected return | {ret_opt*100:.2f}% |
| σ²ₚ | Portfolio variance (risk squared) | {std_opt**2*100:.4f}% |
| γ | Risk aversion coefficient | {gamma} |
| λ | ESG preference weight | {lamda} |
| ESGₚ | Portfolio ESG score | {esg_opt:.1f} / 100 |

**ESG Strategy: {strategy_label}**
""")

    if esg_model.startswith("🚫"):
        st.info(f"**Model 1.0 — Exclusion Screening:** Any asset with ESG score below **{esg_threshold}** is removed from the investable universe before optimisation begins. This mirrors real-world exclusion criteria used by ESG funds to avoid sin stocks (tobacco, weapons, fossil fuels).")
    elif esg_model.startswith("🏅"):
        st.info(f"**Model 2.0 — Best-in-Class:** The top ESG performer receives a 15% bonus to its effective ESG score. This incentivises relative ESG leadership within sectors, rather than excluding entire industries.")
    else:
        st.info(f"**Model 3.0 — Full Integration:** ESG is directly embedded into the utility function via λ = {lamda}. The optimiser naturally tilts the portfolio toward higher-ESG assets when this improves overall utility.")

    st.markdown(f"""
**The Efficient Frontier**

The efficient frontier shows all possible combinations of the two assets (from 0% to 100% in Asset 1).
Each combination is scored by its utility U. The combination with the highest U is your **optimal portfolio**.

**Tangency Portfolio**

The tangency portfolio (red star on the chart) is the risky portfolio with the highest Sharpe ratio — the best return per unit of risk. Your optimal ESG portfolio may differ from this because ESG preferences shift the optimum.

**Your Results**

- Optimal weight in {asset1_name}: **{w1_opt*100:.1f}%**
- Optimal weight in {asset2_name}: **{w2_opt*100:.1f}%**
- Expected return: **{ret_opt*100:.2f}%** | Risk: **{std_opt*100:.2f}%** | ESG: **{esg_opt:.1f}/100**
""")

    st.markdown("""
<div class="disclaimer">
⚠️ <strong>Disclaimer:</strong> QGreen is a prototype built for educational purposes (ECN316, QMUL).
It does not constitute financial advice. Always consult a qualified professional before investing.
</div>
""", unsafe_allow_html=True)
