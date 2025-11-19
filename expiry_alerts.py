import pandas as pd
from datetime import datetime

# Load stock file
stock = pd.read_csv('stock.csv')

# Normalize columns
stock.columns = [c.lower().strip() for c in stock.columns]

# Convert expiry_date to datetime
stock['expiry_date'] = pd.to_datetime(stock['expiry_date'], errors='coerce')

# Calculate days left
today = pd.Timestamp.today().normalize()
stock['days_left'] = (stock['expiry_date'] - today).dt.days

# Create expiry status
def expiry_status(days):
    if pd.isna(days):
        return "unknown"
    if days < 0:
        return "expired"
    if days <= 7:
        return "expiring_soon"
    return "safe"

stock['expiry_status'] = stock['days_left'].apply(expiry_status)

# Select final columns
expiry_alerts = stock[['store_id','product_id','stock_level','expiry_date',
                       'days_left','expiry_status']]

expiry_alerts.to_csv('expiry_alerts.csv', index=False)

print("expiry_alerts.csv generated successfully!")
print(expiry_alerts.head(30).to_string(index=False))