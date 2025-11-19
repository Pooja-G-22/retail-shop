# buying_recommendations.py
# Combines forecast + social trends + ai alerts into final buying suggestions

import pandas as pd
import numpy as np

# Load needed files
forecast = pd.read_csv('future_prediction_summary.csv')
trends = pd.read_csv('social_trends.csv')
alerts = pd.read_csv('ai_alerts.csv')

# Normalize column names
forecast.columns = [c.lower().strip() for c in forecast.columns]
trends.columns = [c.lower().strip() for c in trends.columns]
alerts.columns = [c.lower().strip() for c in alerts.columns]

# Merge everything
df = forecast.merge(
        trends[['product_id','trend_score','trend_category']],
        on='product_id', how='left'
    ).merge(
        alerts[['product_id','movement']],
        on='product_id', how='left'
    )

# Desired stock = forecast for next 30 * safety factor
SAFETY_FACTOR = 1.2
df['optimal_stock_next_30'] = (df['forecast_next_30'] * SAFETY_FACTOR).round(2)

# Units to buy = optimal - current
df['units_to_buy'] = (df['optimal_stock_next_30'] - df['current_stock']).apply(lambda x: max(0, int(np.ceil(x))))

# Buying priority
def priority(row):
    if row['trend_category'] in ['viral','trending'] and row['units_to_buy'] > 0:
        return 'HIGH'
    if row['movement'] == 'fast-moving':
        return 'HIGH'
    if row['trend_category'] == 'stable' and row['units_to_buy'] > 0:
        return 'MEDIUM'
    if row['units_to_buy'] > 0:
        return 'LOW'
    return 'NO NEED'

df['buying_priority'] = df.apply(priority, axis=1)

# Final table
final = df[['product_id','forecast_next_30','trend_category','trend_score',
            'movement','current_stock','optimal_stock_next_30','units_to_buy',
            'buying_priority']]

# Save file
final.to_csv('buying_recommendations.csv', index=False)

print("buying_recommendations.csv generated successfully!")
print(final.head(20).to_string(index=False))