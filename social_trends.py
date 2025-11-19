# social_trends.py
# AI-based social media trend scoring for each product

import pandas as pd
import numpy as np

# Load previous outputs
rankings = pd.read_csv('product_rankings.csv')
future = pd.read_csv('future_prediction_summary.csv')
ai_alerts = pd.read_csv('ai_alerts.csv')

# Normalize column names
rankings.columns = [c.lower().strip() for c in rankings.columns]
future.columns = [c.lower().strip() for c in future.columns]
ai_alerts.columns = [c.lower().strip() for c in ai_alerts.columns]

# Merge everything
merged = rankings.merge(future, on='product_id', how='left')
merged = merged.merge(ai_alerts[['product_id','movement']], on='product_id', how='left')

# --- AI SOCIAL TREND SCORING ---

# Social buzz factor (simulated social media buzz)
np.random.seed(42)
merged['social_buzz'] = np.random.randint(10, 100, size=len(merged))

# Trend score calculation
merged['trend_score'] = (
    merged['total_sales'] * 0.30 +
    merged['forecast_next_30'] * 0.30 +
    merged['social_buzz'] * 0.20 +
    merged['rank'].max() / merged['rank'] * 0.10 +
    merged['suggested_additional_stock'] * 0.10
).round(2)

# Trend category
def trend_label(score):
    if score >= merged['trend_score'].quantile(0.75):
        return "viral"
    if score >= merged['trend_score'].quantile(0.50):
        return "trending"
    if score >= merged['trend_score'].quantile(0.25):
        return "stable"
    return "declining"

merged['trend_category'] = merged['trend_score'].apply(trend_label)

# Save social trends
merged.to_csv('social_trends.csv', index=False)

# --- TREND-BASED BUYING RECOMMENDATIONS ---

recommendations = merged[['product_id','trend_score','trend_category',
                          'forecast_next_30','current_stock','suggested_additional_stock']].copy()

def buy_suggestion(row):
    if row['trend_category'] in ['viral','trending']:
        return int(row['suggested_additional_stock'] + (row['trend_score'] * 0.1))
    return 0  # don't buy for declining or stable

recommendations['extra_qty_to_buy'] = recommendations.apply(buy_suggestion, axis=1)

recommendations.to_csv('trend_based_recommendations.csv', index=False)

print("social_trends.csv and trend_based_recommendations.csv created successfully!")
print(recommendations.head(20).to_string(index=False))