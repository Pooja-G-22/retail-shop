import pandas as pd
from datetime import datetime, timedelta

# Load files
products = pd.read_csv("products.csv")
stock = pd.read_csv("stock.csv")
sales = pd.read_csv("sales.csv")

# ---- FIX DATE CONVERSION (ACCEPT ANY FORMAT) ----
stock["expiry_date"] = pd.to_datetime(stock["expiry_date"], dayfirst=True, errors="coerce")
stock["date"] = pd.to_datetime(stock["date"], dayfirst=True, errors="coerce")
sales["date"] = pd.to_datetime(sales["date"], dayfirst=True, errors="coerce")

# ---- 1. EXPIRY ALERTS ----
today = datetime(2025,1,1)
expiry_limit = today + timedelta(days=7)

expiry_alerts = stock[stock["expiry_date"] <= expiry_limit]

# ---- 2. AVERAGE SALES PER PRODUCT ----
avg_sales = sales.groupby("product_id")["qty_sold"].mean().reset_index()
avg_sales.columns = ["product_id","avg_daily_sale"]

# ---- 3. MERGE STOCK + SALES ----
merged = stock.merge(avg_sales, on="product_id", how="left")

# ---- 4. OVERSTOCK ALERT ----
merged["overstock"] = merged["stock_level"] > (merged["avg_daily_sale"] * 10)

overstock_alerts = merged[merged["overstock"] == True]

# ---- 5. LOW STOCK ALERT ----
merged = merged.merge(products, on="product_id")
low_stock_alerts = merged[merged["stock_level"] < merged["reorder_level"]]

# ---- 6. FAST / SLOW MOVING PRODUCTS ----
product_speed = avg_sales.copy()
product_speed["category"] = product_speed["avg_daily_sale"].apply(
    lambda x: "Fast Moving" if x > 15 else ("Slow Moving" if x < 5 else "Medium")
)

# ---- PRINT OUTPUT ----
print("\n=========== EXPIRY ALERTS ===========")
print(expiry_alerts[["store_id","product_id","stock_level","expiry_date"]])

print("\n=========== OVERSTOCK ALERTS ===========")
print(overstock_alerts[["store_id","product_id","stock_level","avg_daily_sale"]])

print("\n=========== LOW STOCK ALERTS ===========")
print(low_stock_alerts[["store_id","product_id","stock_level","reorder_level"]])

print("\n=========== FAST / SLOW MOVING ITEMS ===========")
print(product_speed.head(30))