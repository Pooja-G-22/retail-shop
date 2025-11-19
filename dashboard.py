# dashboard.py
# Streamlit dashboard for your Intelligent Retail Inventory System
# Put this file in the same folder as your CSV files:
# - sales.csv, stock.csv, transfer_suggestions.csv
# - ai_alerts.csv, store_alerts.csv, expiry_alerts.csv
# - historical_analysis.csv, product_rankings.csv
# - future_prediction_daily.csv, future_prediction_summary.csv
# - social_trends.csv, trend_based_recommendations.csv
# - buying_recommendations.csv

import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Retail AI Dashboard", layout="wide")

st.title("Retail AI Inventory Dashboard — Pooja")

# --- helper to load CSVs safely
@st.cache_data
def load_csv_safe(path):
    try:
        df = pd.read_csv(path)
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    except Exception:
        return None

# Load datasets (some may be missing — handle gracefully)
sales = load_csv_safe('sales.csv')
stock = load_csv_safe('stock.csv')
transfer = load_csv_safe('transfer_suggestions.csv')
ai_alerts = load_csv_safe('ai_alerts.csv')
store_alerts = load_csv_safe('store_alerts.csv')
expiry = load_csv_safe('expiry_alerts.csv')
historical = load_csv_safe('historical_analysis.csv')
rankings = load_csv_safe('product_rankings.csv')
future_daily = load_csv_safe('future_prediction_daily.csv')
future_summary = load_csv_safe('future_prediction_summary.csv')
social = load_csv_safe('social_trends.csv')
trend_reco = load_csv_safe('trend_based_recommendations.csv')
buying = load_csv_safe('buying_recommendations.csv')

# Small utility: show csv and provide download button
def show_table_and_download(df, file_label):
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label=f"Download {file_label} as CSV", data=csv, file_name=f"{file_label}.csv", mime='text/csv')

# Sidebar navigation
page = st.sidebar.selectbox("Choose page", [
    "Overview",
    "AI Alerts",
    "Store Alerts",
    "Expiry Tracker",
    "Forecast & Trends",
    "Social Trends & Buying Suggestions",
    "Transfer Suggestions",
    "Files"
])

# ---------- Overview ----------
if page == "Overview":
    st.header("Overview & KPIs")
    col1, col2, col3, col4 = st.columns(4)
    # KPI calculations (guard against missing files)
    total_products = int(rankings['product_id'].nunique()) if rankings is not None else (len(stock['product_id'].unique()) if stock is not None else 0)
    total_stores = int(stock['store_id'].nunique()) if stock is not None and 'store_id' in stock.columns else "N/A"
    low_stock_count = int((ai_alerts['status'] == 'low_stock').sum()) if ai_alerts is not None and 'status' in ai_alerts.columns else "N/A"
    overstock_count = int((ai_alerts['status'] == 'overstock').sum()) if ai_alerts is not None and 'status' in ai_alerts.columns else "N/A"

    col1.metric("Products (unique)", total_products)
    col2.metric("Stores", total_stores)
    col3.metric("Low stock products", low_stock_count)
    col4.metric("Overstock products", overstock_count)

    st.markdown("### Top 10 Best-Selling Products")
    if rankings is not None:
        show_table_and_download(rankings.head(20), "product_rankings_top20")
    else:
        st.info("product_rankings.csv not found.")

    st.markdown("### Summary: Forecast & Buying Suggestions")
    if buying is not None:
        st.dataframe(buying.sort_values('buying_priority', ascending=False).head(30))
    else:
        st.info("buying_recommendations.csv not found.")

# ---------- AI Alerts ----------
elif page == "AI Alerts":
    st.header("AI Alerts (Product-level)")
    if ai_alerts is None:
        st.info("ai_alerts.csv not found.")
    else:
        st.subheader("AI Alerts Table")
        show_table_and_download(ai_alerts, "ai_alerts")
        st.subheader("Low stock list")
        if 'status' in ai_alerts.columns:
            st.dataframe(ai_alerts[ai_alerts['status'] == 'low_stock'].sort_values('current_stock'))
        else:
            st.info("No status column in ai_alerts")

# ---------- Store Alerts ---------