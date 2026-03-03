# calculator.py
# This file handles all the math logic — kept separate from the UI intentionally
import yfinance as yf
import pandas as pd

def get_stock_price(ticker: str) -> float:
    try:
        stock = yf.Ticker(ticker)
        price = stock.fast_info['last_price']
        return round(price, 2)
    except Exception:
        return None

def calculate_concentration_risk(
    rsu_shares: float,
    stock_price: float,
    cash_savings: float,
    other_investments: float
) -> dict:
    rsu_value = rsu_shares * stock_price
    total_net_worth = rsu_value + cash_savings + other_investments
    concentration_pct = (rsu_value / total_net_worth) * 100 if total_net_worth > 0 else 0

    if concentration_pct > 40:
        risk_label = "🔴 Dangerously Concentrated"
    elif concentration_pct > 20:
        risk_label = "🟡 High Concentration"
    else:
        risk_label = "🟢 Reasonably Diversified"

    return {
        "rsu_value": rsu_value,
        "total_net_worth": total_net_worth,
        "concentration_pct": round(concentration_pct, 1),
        "risk_label": risk_label
    }

def generate_diversification_plan(rsu_value: float, risk_tolerance: str) -> pd.DataFrame:
    allocations = {
        "Conservative": {
            "VTI (US Total Market)": 0.30,
            "VXUS (International)": 0.20,
            "BND (US Bonds)": 0.30,
            "SGOV (T-Bills/Cash)": 0.20,
        },
        "Moderate": {
            "VTI (US Total Market)": 0.45,
            "VXUS (International)": 0.25,
            "BND (US Bonds)": 0.20,
            "QQQ (Tech/Growth)": 0.10,
        },
        "Aggressive": {
            "VTI (US Total Market)": 0.50,
            "VXUS (International)": 0.30,
            "QQQ (Tech/Growth)": 0.15,
            "ARKK (Speculative)": 0.05,
        }
    }

    selected = allocations[risk_tolerance]
    rows = []
    for etf, pct in selected.items():
        rows.append({
            "Asset": etf,
            "Allocation %": f"{int(pct * 100)}%",
            "Dollar Amount": f"${rsu_value * pct:,.0f}"
        })
    return pd.DataFrame(rows)

def estimate_tax_drag(rsu_value: float, cost_basis: float, holding_period_months: int) -> dict:
    gain = rsu_value - cost_basis

    if gain <= 0:
        return {"gain": 0, "estimated_tax": 0, "net_proceeds": rsu_value, "rate_used": "N/A"}

    if holding_period_months < 12:
        rate = 0.37
        rate_label = "37% (Short-term, ordinary income)"
    else:
        rate = 0.20
        rate_label = "20% (Long-term federal)"

    estimated_tax = gain * rate
    net_proceeds = rsu_value - estimated_tax

    return {
        "gain": round(gain, 2),
        "estimated_tax": round(estimated_tax, 2),
        "net_proceeds": round(net_proceeds, 2),
        "rate_used": rate_label
    }