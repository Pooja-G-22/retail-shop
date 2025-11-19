# seasonal_discounts.py
# Creates seasonal discount recommendations based on sales patterns

import pandas as pd
import numpy as np

# Load historical analysis (sales trends)
historical = pd.read_csv('historical_analysis.csv')

# Normalize column names
historical.columns = [c.lower().strip() for c in historical.columns]

# Create a mock seasonal factor based on sales performance
def get_season(total):
    if total > historical['total_sales'].quantile(0.75):
        return "festival"
    elif total > historical['total_sales'].quantile(0.50):
        return "summer"
    elif total > historical['total_sales'].quantile(0.25):
        return "winter"
    else:
        return "off-season"

# Assign season
historical['season'] = historical['total_sales'].apply(get_season)

# Discount logic
def discount_factor(season):
    if season == "festival":
        return 5   # small discount
    if season == "summer":
        return 10
    if season == "winter":
        return 15
    return 25  # off-season highest discount

historical['recommended_discount_percent'] = historical['season'].apply(discount_factor)

# Explanation column
def reason(season):
    if season == "festival":
        return "High demand season — only small discount needed"
    if season == "summer":
        return "Good demand — moderate discount"
    if season == "winter":
        return "Low demand — increase discount"
    return "Very low sales — offer big discount"

historical['discount_reason'] = historical['season'].apply(reason)

# Save output
historical.to_csv('seasonal_discounts.csv', index=False)

print("seasonal_discounts.csv created successfully!")
print(historical[['product_id','total_sales','season','recommended_discount_percent','discount_reason']].head(20))