import pandas as pd

# Load sales data
sales = pd.read_csv('sales.csv')

# Normalize column names
sales.columns = [c.lower().strip() for c in sales.columns]

# Rename qty_sold → quantity
if 'qty_sold' in sales.columns:
    sales = sales.rename(columns={'qty_sold': 'quantity'})

# Ensure date is datetime
sales['date'] = pd.to_datetime(sales['date'], errors='coerce')

# --- 1. TOTAL SALES PER PRODUCT ---
total_sales = sales.groupby('product_id')['quantity'].sum().reset_index()
total_sales = total_sales.rename(columns={'quantity': 'total_sales'})

# --- 2. AVERAGE DAILY SALES PER PRODUCT ---
daily_avg = sales.groupby(['product_id', 'date']).agg(
    daily_sales=('quantity', 'sum')
).reset_index()

avg_daily_sales = daily_avg.groupby('product_id')['daily_sales'].mean().reset_index()
avg_daily_sales = avg_daily_sales.rename(columns={'daily_sales': 'average_daily_sales'})

# --- 3. PEAK SALES DAY ---
peak_day = sales.groupby(['product_id', 'date'])['quantity'].sum().reset_index()
peak_day = peak_day.sort_values(['product_id', 'quantity'], ascending=[True, False])
peak_day = peak_day.groupby('product_id').head(1)
peak_day = peak_day.rename(columns={'date': 'peak_sales_day', 'quantity': 'peak_sales_qty'})

# --- 4. LOWEST SALES DAY ---
low_day = sales.groupby(['product_id', 'date'])['quantity'].sum().reset_index()
low_day = low_day.sort_values(['product_id', 'quantity'], ascending=[True, True])
low_day = low_day.groupby('product_id').head(1)
low_day = low_day.rename(columns={'date': 'lowest_sales_day', 'quantity': 'lowest_sales_qty'})

# --- 5. STORE COVERAGE (sold in how many stores) ---
store_coverage = sales.groupby('product_id')['store_id'].nunique().reset_index()
store_coverage = store_coverage.rename(columns={'store_id': 'total_store_coverage'})

# --- MERGE ALL METRICS ---
historical = total_sales.merge(avg_daily_sales, on='product_id')
historical = historical.merge(peak_day[['product_id', 'peak_sales_day', 'peak_sales_qty']], on='product_id')
historical = historical.merge(low_day[['product_id', 'lowest_sales_day', 'lowest_sales_qty']], on='product_id')
historical = historical.merge(store_coverage, on='product_id')

# Save historical analysis
historical.to_csv('historical_analysis.csv', index=False)

# --- CREATE PRODUCT RANKINGS ---
rankings = total_sales.sort_values('total_sales', ascending=False)
rankings['rank'] = rankings['total_sales'].rank(method='dense', ascending=False).astype(int)

def category(score):
    if score >= rankings['total_sales'].quantile(0.67):
        return "fast_selling"
    if score <= rankings['total_sales'].quantile(0.33):
        return "slow_selling"
    return "medium_selling"

rankings['category'] = rankings['total_sales'].apply(category)

rankings.to_csv('product_rankings.csv', index=False)

print("historical_analysis.csv and product_rankings.csv created successfully!")
print(rankings.head(20).to_string(index=False))