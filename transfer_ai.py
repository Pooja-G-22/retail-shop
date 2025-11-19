import pandas as pd

# Load data
stock = pd.read_csv("stock.csv")
sales = pd.read_csv("sales.csv")

# Average sales per product per store
avg_sales = sales.groupby(["store_id","product_id"])["qty_sold"].mean().reset_index()
avg_sales.columns = ["store_id","product_id","avg_daily_sale"]

# Merge stock + demand
merged = stock.merge(avg_sales, on=["store_id","product_id"], how="left")

# Calculate shortage & excess
merged["required_stock"] = merged["avg_daily_sale"] * 7    # 1 week buffer
merged["excess"] = merged["stock_level"] - merged["required_stock"]

# Stores with excess
excess_items = merged[merged["excess"] > 20]

# Stores with shortage
shortage_items = merged[merged["excess"] < -5]

# --- CREATE TRANSFER SUGGESTIONS ---
suggestions = []

for _, excess_row in excess_items.iterrows():
    for _, short_row in shortage_items.iterrows():

        if excess_row["product_id"] == short_row["product_id"]:
            qty_to_send = min(excess_row["excess"], abs(short_row["excess"]))

            suggestions.append([
                excess_row["store_id"],
                short_row["store_id"],
                excess_row["product_id"],
                int(qty_to_send)
            ])

transfer_df = pd.DataFrame(suggestions,
    columns=["from_store","to_store","product_id","qty_transfer"]
)

print("\n=========== STORE TRANSFER SUGGESTIONS ===========")
print(transfer_df)
transfer_df.to_csv("transfer_suggestions.csv", index=False)