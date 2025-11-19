# generate_ai_alerts.py
# For Pooja's files:
# sales.csv has column: qty_sold
# stock.csv has columns: date, store_id, product_id, stock_level, expiry_date
# Option 2 settings: REORDER_LEVEL = 10, OVERSTOCK_THRESHOLD = 60

import pandas as pd

REORDER_LEVEL = 10
OVERSTOCK_THRESHOLD = 60

# --- Load files ---
sales = pd.read_csv('sales.csv')
stock = pd.read_csv('stock.csv')

# Normalize column names
sales.columns = [c.lower().strip() for c in sales.columns]
stock.columns = [c.lower().strip() for c in stock.columns]

# Ensure product column is product_id
if 'product' in sales.columns and 'product_id' not in sales.columns:
    sales = sales.rename(columns={'product': 'product_id'})
if 'product' in stock.columns and 'product_id' not in stock.columns:
    stock = stock.rename(columns={'product': 'product_id'})

# Rename qty_sold -> quantity for calculations
if 'qty_sold' in sales.columns:
    sales = sales.rename(columns={'qty_sold': 'quantity'})

# If sales has date, parse it; otherwise create a single date
if 'date' in sales.columns:
    sales['date'] = pd.to_datetime(sales['date'])
else:
    sales['date'] = pd.Timestamp.today().normalize()

# --- Aggregate sales: average daily sales per product (across all stores) ---
avg_daily = sales.groupby('product_id').agg(
    total_sold=('quantity', 'sum'),
    days_observed=('date', lambda x: x.nunique())
).reset_index()
avg_daily['avg_daily_sales'] = (avg_daily['total_sold'] / avg_daily['days_observed']).round(2)

# --- Aggregate stock: sum stock_level across stores per product ---
if 'stock_level' not in stock.columns:
    raise SystemExit("stock.csv must contain column named 'stock_level' (you have: {})".format(list(stock.columns)))

stock_agg = stock.groupby('product_id').agg(
    current_stock=('stock_level', 'sum')
).reset_index()

# --- Merge stock + avg sales ---
alerts = pd.merge(stock_agg, avg_daily[['product_id', 'avg_daily_sales']], on='product_id', how='left')

# --- Movement label ---
def movement_label(avg):
    if pd.isna(avg):
        return 'unknown'
    if avg >= 10:
        return 'fast-moving'
    if avg <= 2:
        return 'slow-moving'
    return 'normal-moving'

alerts['movement'] = alerts['avg_daily_sales'].apply(movement_label)

# --- Stock status ---
def status_label(s):
    if s == 0:
        return 'out_of_stock'
    if s < REORDER_LEVEL:
        return 'low_stock'
    if s > OVERSTOCK_THRESHOLD:
        return 'overstock'
    return 'ok'

alerts['status'] = alerts['current_stock'].apply(status_label)

# --- Reorder suggestion ---
alerts['reorder_target'] = REORDER_LEVEL * 2
alerts['reorder_suggestion'] = alerts.apply(
    lambda r: int(max(0, r['reorder_target'] - r['current_stock']))
    if r['status'] in ['low_stock', 'out_of_stock'] else 0,
    axis=1
)

# --- Final columns & save ---
alerts = alerts[['product_id', 'current_stock', 'avg_daily_sales', 'movement', 'status', 'reorder_target', 'reorder_suggestion']]
alerts.to_csv('ai_alerts.csv', index=False)

print("ai_alerts.csv generated successfully in this folder.")
print(alerts.head(50).to_string(index=False))