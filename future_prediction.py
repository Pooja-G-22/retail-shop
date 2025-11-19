# future_prediction.py
# Simple & safe forecasting (no errors)

import pandas as pd
import numpy as np

N_DAYS_FORECAST = 30

# Load files
sales = pd.read_csv('sales.csv')
stock = pd.read_csv('stock.csv')

# Normalize column names
sales.columns = [c.lower().strip() for c in sales.columns]
stock.columns = [c.lower().strip() for c in stock.columns]

# Rename qty_sold → quantity
if 'qty_sold' in sales.columns:
    sales = sales.rename(columns={'qty_sold': 'quantity'})

# Rename product column if needed
if 'product' in sales.columns and 'product_id' not in sales.columns:
    sales = sales.rename(columns={'product': 'product_id'})
if 'product' in stock.columns and 'product_id' not in stock.columns:
    stock = stock.rename(columns={'product': 'product_id'})

# Parse date
sales['date'] = pd.to_datetime(sales['date'], errors='coerce')

# Daily totals per product
daily = sales.groupby(['product_id', 'date'], as_index=False).agg(
    daily_qty=('quantity', 'sum')
)

products = sorted(daily['product_id'].unique())

forecast_rows = []
summary_rows = []

# Get max date in data
last_date = daily['date'].max()

# Create future dates list
future_dates = [(last_date + pd.Timedelta(days=i)).date() for i in range(1, N_DAYS_FORECAST + 1)]

for pid in products:

    # Get past data for this product
    dfp = daily[daily['product_id'] == pid].copy().sort_values('date')

    # --- Simple forecast method ---
    # Use last 7 days average. If not enough days, use available average.
    if len(dfp) >= 7:
        forecast_value = dfp['daily_qty'].tail(7).mean()
    else:
        forecast_value = dfp['daily_qty'].mean()

    # If NaN -> set to 0
    if pd.isna(forecast_value):
        forecast_value = 0.0

    # Store daily forecast
    for fd in future_dates:
        forecast_rows.append({
            'product_id': pid,
            'date': fd,
            'forecast_qty': round(float(forecast_value), 2)
        })

    # Total forecast next 30 days
    total_30 = round(float(forecast_value * N_DAYS_FORECAST), 2)

    # Current stock
    cur_stock = stock[stock['product_id'] == pid]['stock_level'].sum()

    # Suggested additional stock
    suggested = max(0, int(np.ceil(total_30 - cur_stock)))

    summary_rows.append({
        'product_id': pid,
        'forecast_next_30': total_30,
        'current_stock': int(cur_stock),
        'suggested_additional_stock': suggested
    })

# Convert to DataFrames
df_forecast = pd.DataFrame(forecast_rows)
df_summary = pd.DataFrame(summary_rows)

# Save files
df_forecast.to_csv('future_prediction_daily.csv', index=False)
df_summary.to_csv('future_prediction_summary.csv', index=False)

print("future_prediction_daily.csv and future_prediction_summary.csv created successfully!")
print(df_summary.head(20).to_string(index=False))