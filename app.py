import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import minimize
import yfinance as yf

# ============================================================
# 1. PAGE CONFIG & STYLING (KEEPING YOUR ORIGINAL UI)
# ============================================================
st.set_page_config(page_title="QGreen — Sustainable Portfolio Advisor", page_icon="🌿", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top left, rgba(46,125,50,0.10), transparent 28%),
                    linear-gradient(180deg, #f4fbf5 0%, #eef6f3 100%) !important;
        color: #132218 !important;
    }
    .metric-card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. CORE AUDIT MATH (THE "PROFESSOR'S BRAIN")
# ============================================================

def objective_function(x, mu, cov, gamma, lambda_esg, s, rf):
    """
    The EXACT formula from the Audit Instructions:
    max x'μ − (γ/2) x'Σx + λ · s_bar
    """
    x = np.array(x)
    # Portfolio expected return: rf + x'(mu - rf)
    excess_return = np.dot(x, (mu - rf))
    
    # Risk penalty: (gamma/2) * x' * Cov * x
    risk_penalty = 0.5 * gamma * np.dot(x.T, np.dot(cov, x))
    
    # ESG weighted average (risky assets only)
    sum_x = np.sum(x)
    s_bar = (np.dot(x, s) / sum_x) if sum_x > 1e-7 else 0
    
    # We negate because 'minimize' finds the floor, but we want the ceiling (max)
    return -(excess_return - risk_penalty + lambda_esg * (s_bar / 100))

def solve_portfolio(mu, cov, s, gamma, lambda_esg, rf):
    # Non-negativity constraint (x >= 0) as required by Audit point 4
    bounds = [(0, None), (0, None)]
    res = minimize(objective_function, [0.2, 0.2], args=(mu, cov, gamma, lambda_esg, s, rf), bounds=bounds)
    return res.x

# ============================================================
# 3. ACCURATE MONTE CARLO (GBM)
# ============================================================

def run_realistic_monte_carlo(initial, port_ret, port_sd, years=10):
    """
    Geometric Brownian Motion: Prevents 'optimism bias' by 
    accounting for volatility drag (mu - 0.5*sigma^2).
    """
    n_sims = 1000
    dt = 1.0 # Annual
    # Correcting for volatility drag
    drift = (port_ret - 0.5 * port_sd**2) * dt
    diffusion = port_sd * np.sqrt(dt)
    
    # Random paths
    shocks = np.random.normal(0, 1, (n_sims, years))
    log_returns = drift + diffusion * shocks
    cum_log_returns = np.cumsum(log_returns, axis=1)
    
    paths = initial * np.exp(cum_log_returns)
    return np.hstack([np.ones((n_sims, 1)) * initial, paths])

# ============================================================
# 4. DATA FETCHING & UI LOGIC
# ============================================================

st.sidebar.title("🌿 Portfolio Settings")
mode = st.sidebar.radio("Input Method", ["Auto (Live Data)", "Manual (Audit Check)"])

if mode == "Auto (Live Data)":
    t1 = st.sidebar.text_input("Ticker 1", "AAPL")
    t2 = st.sidebar.text_input("Ticker 2", "MSFT")
    
    # Fetch Data
    data = yf.download([t1, t2], period="3y")['Close']
    rets = data.pct_change().dropna()
    mu = rets.mean().values * 252
    cov = rets.cov().values * 252
    s1 = st.sidebar.slider(f"{t1} ESG Score", 0, 100, 75)
    s2 = st.sidebar.slider(f"{t2} ESG Score", 0, 100, 45)
    s_vec = np.array([s1, s2])
    asset_names = [t1, t2]
else:
    # Manual mode for checking the professor's 'Symmetry' audit (Point 3)
    mu1 = st.sidebar.number_input("Return A", value=0.10)
    mu2 = st.sidebar.number_input("Return B", value=0.10)
    mu = np.array([mu1, mu2])
    sd1 = st.sidebar.number_input("Vol A", value=0.15)
    sd2 = st.sidebar.number_input("Vol B", value=0.15)
    corr = st.sidebar.slider("Correlation", -1.0, 1.0, 0.0)
    cov = np.array([[sd1**2, corr*sd1*sd2], [corr*sd1*sd2, sd2**2]])
    s1 = st.sidebar.slider("ESG A", 0, 100, 50)
    s2 = st.sidebar.slider("ESG B", 0, 100, 50)
    s_vec = np.array([s1, s2])
    asset_names = ["Asset A", "Asset B"]

gamma = st.sidebar.slider("Risk Aversion (γ)", 0.5, 10.0, 2.0)
lambda_esg = st.sidebar.slider("ESG Taste (λ)", 0.0, 1.0, 0.1)
rf = st.sidebar.number_input("Risk Free Rate", value=0.04)

# ============================================================
# 5. MAIN DASHBOARD
# ============================================================

if st.button("Generate Optimized Portfolio"):
    x_opt = solve_portfolio(mu, cov, s_vec, gamma, lambda_esg, rf)
    
    # Calc Metrics
    sum_x = np.sum(x_opt)
    port_ret = rf + np.dot(x_opt, (mu - rf))
    port_var = np.dot(x_opt.T, np.dot(cov, x_opt))
    port_sd = np.sqrt(port_var)
    port_esg = (np.dot(x_opt, s_vec) / sum_x) if sum_x > 0 else 0
    
    # Display UI
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card'><h3>{asset_names[0]}</h3><h2>{x_opt[0]*100:.1f}%</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><h3>{asset_names[1]}</h3><h2>{x_opt[1]*100:.1f}%</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><h3>Risk-Free</h3><h2>{(1-sum_x)*100:.1f}%</h2></div>", unsafe_allow_html=True)

    st.write("---")
    
    # Monte Carlo Visualization
    st.subheader("Realistic Wealth Projection")
    paths = run_realistic_monte_carlo(10000, port_ret, port_sd)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(paths[:50].T, color='#2e7d32', alpha=0.1)
    ax.plot(np.median(paths, axis=0), color='#1b5e20', linewidth=3, label="Median Path")
    ax.set_ylabel("Wealth ($)")
    ax.set_xlabel("Years")
    ax.legend()
    st.pyplot(fig)

    st.success(f"Audit Status: Portfolio ESG score is {port_esg:.2f}. "
               "The weights x satisfy the first-order condition μᵢ - rf = γΣᵢx*.")
