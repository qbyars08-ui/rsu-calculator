# app.py
# This is the UI layer — all math lives in calculator.py, not here
import streamlit as st
import plotly.graph_objects as go
from calculator import (
    get_stock_price,
    calculate_concentration_risk,
    generate_diversification_plan,
    estimate_tax_drag
)

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="RSU Diversification Calculator",
    page_icon="📊",
    layout="centered"
)

st.title("📊 RSU Concentration Risk Calculator")
st.caption("For tech employees holding company stock. Not financial advice.")

# --- INPUTS ---
st.header("1. Your Current Holdings")

col1, col2 = st.columns(2)
with col1:
    ticker = st.text_input("Company Stock Ticker", value="GOOGL").upper().strip()
with col2:
    rsu_shares = st.number_input("Vested RSU Shares", min_value=0, value=100, step=10)
cash_savings = st.number_input("Cash Savings ($)", min_value=0, value=50000, step=1000)
other_investments = st.number_input("Other Investments ($)", min_value=0, value=20000, step=1000) 

st.header("2. Tax Estimate Inputs")
col3, col4 = st.columns(2)
with col3:
    cost_basis = st.number_input("Grant Price Per Share ($)", min_value=0.0, value=100.0)
with col4:
    holding_months = st.slider("Months Since Vesting", min_value=1, max_value=60, value=8)

st.header("3. Risk Tolerance")
risk_tolerance = st.select_slider(
    "How would you reinvest if you sold?",
    options=["Conservative", "Moderate", "Aggressive"],
    value="Moderate"
)

# --- CALCULATE ---
if st.button("Calculate My Risk", type="primary", use_container_width=True):

    with st.spinner(f"Fetching live price for {ticker}..."):
        stock_price = get_stock_price(ticker)

    if stock_price is None:
        st.error(f"Couldn't fetch price for '{ticker}'. Check the ticker and try again.")
        st.stop()

    st.success(f"Live price for **{ticker}**: ${stock_price:,.2f}")

    risk_data = calculate_concentration_risk(rsu_shares, stock_price, cash_savings, other_investments)
    tax_data = estimate_tax_drag(risk_data["rsu_value"], cost_basis * rsu_shares, holding_months)
    div_plan = generate_diversification_plan(risk_data["rsu_value"], risk_tolerance)

    # --- RESULTS ---
    st.divider()
    st.header("Your Results")

    m1, m2, m3 = st.columns(3)
    m1.metric("RSU Value", f"${risk_data['rsu_value']:,.0f}")
    m2.metric("Total Net Worth", f"${risk_data['total_net_worth']:,.0f}")
    m3.metric("Concentration Risk", f"{risk_data['concentration_pct']}%")

    st.subheader(risk_data['risk_label'])

    # --- PIE CHART ---
    fig = go.Figure(data=[go.Pie(
        labels=[f"{ticker} RSUs", "Cash", "Other Investments"],
        values=[risk_data["rsu_value"], cash_savings, other_investments],
        hole=0.4,
        marker_colors=["#FF4B4B", "#0068C9", "#83C9FF"],
        texttemplate="%{label}<br>%{percent:.1%}",  # rounds to 1 decimal
        textposition="inside",
        rotation=90
    )])
    fig.update_traces(
        # hides label entirely if slice is under 1% — fixes the clutter
        textinfo="label+percent",
        insidetextorientation="radial",
        pull=[0.05 if v / sum([risk_data["rsu_value"], cash_savings, other_investments]) > 0.01 
              else 0 for v in [risk_data["rsu_value"], cash_savings, other_investments]]
    )
    fig.update_layout(
        title_text="Your Current Portfolio Breakdown",
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- TAX ---
    st.subheader("💸 Estimated Tax Drag If You Sell Now")
    t1, t2, t3 = st.columns(3)
    t1.metric("Capital Gain", f"${tax_data['gain']:,.0f}")
    t2.metric("Estimated Tax", f"${tax_data['estimated_tax']:,.0f}")
    t3.metric("Net Proceeds", f"${tax_data['net_proceeds']:,.0f}")
    st.caption(f"Rate applied: {tax_data['rate_used']} (US federal only — consult a CPA)")

    # --- DIVERSIFICATION PLAN ---
    st.subheader(f"📈 Suggested Reallocation ({risk_tolerance})")
    st.dataframe(div_plan, use_container_width=True, hide_index=True)

    st.info("💡 Educational only. Talk to a fee-only financial advisor before making any moves.")