import pandas as pd

REORDER_LEVEL = 10
OVERSTOCK_THRESHOLD = 60

# Load files
sales = pd.read_csv('sales.csv')
stock = pd.read_csv('stock.csv')

# Normalize column names
sales.columns = [c.lower().strip() for c in sales.columns]
stock.columns = [c.lower().strip() for c in stock.columns]

# Rename qty_sold → quantity
if 'qty_sold' in sales.columns:
    sales = sales.rename(columns={'qty_sold': 'quantity'})

# Ensure product_id exists
if 'product' in sales.columns and 'product_id' not in sales.columns:
    sales = sales.rename(columns={'product': 'product_id'})
if 'product' in stock.columns and 'product_id' not in stock.columns:
    stock = stock.rename(columns={'product': 'product_id'})

# Parse dates
sales['date'] = pd.to_datetime(sales['date'], errors='coerce')

# Group sales BY STORE + PRODUCT
sales_store = sales.groupby(['store_id','product_id']).agg(
    total_sold=('quantity','sum'),
    days_observed=('date', lambda x: x.nunique())
).reset_index()

# Compute avg daily sales
sales_store['avg_daily_sales'] = (sales_store['total_sold'] / sales_store['days_observed']).round(2)

# Merge with stock (store-wise)
merged = pd.merge(
    stock[['store_id','product_id','stock_level']],
    sales_store[['store_id','product_id','avg_daily_sales']],
    on=['store_id','product_id'],
    how='left'
)

# Movement label
def movement(avg):
    if pd.isna(avg):
        return 'unknown'
    if avg >= 10:
        return 'fast-moving'
    if avg <= 2:
        return 'slow-moving'
    return 'normal-moving'

merged['movement'] = merged['avg_daily_sales'].apply(movement)

# Stock status
def stock_status(val):
    if val == 0:
        return 'out_of_stock'
    if val < REORDER_LEVEL:
        return 'low_stock'
    if val > OVERSTOCK_THRESHOLD:
        return 'overstock'
    return 'ok'

merged['status'] = merged['stock_level'].apply(stock_status)

# Reorder suggestion
merged['reorder_target'] = REORDER_LEVEL * 2
merged['reorder_suggestion'] = merged.apply(
    lambda r: max(0, r['reorder_target'] - r['stock_level'])
              if r['status'] in ['low_stock','out_of_stock'] else 0,
    axis=1
)

# Save file
merged.to_csv('store_alerts.csv', index=False)

print("store_alerts.csv created successfully!")
print(merged.head(40).to_string(index=False))